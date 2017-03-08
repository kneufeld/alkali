from zope.interface import Interface, implements
import inspect
import copy

from .query import Query
from .storage import IStorage
from . import fields
from . import signals

import logging
logger = logging.getLogger(__name__)

class IManager( Interface ):
    pass

class Manager(object):
    """
    the ``Manager`` class is the parent/owner of all the
    :class:`alkali.model.Model` instances. Each ``Model`` has it's own
    manager. ``Manager`` could rightly be called ``Table``.
    """
    implements(IManager)

    def __init__( self, model_class ):
        """
        :param Model model_class: the model that we should store (not an instance)
        """
        assert inspect.isclass(model_class)
        self._model_class = model_class
        self._instances = {}
        self._dirty = False

        self.clear()

    def __repr__(self):
        return "<{}: {}>".format(self._name, len(self))

    def __len__(self):
        return len(self._instances)

    def __getattr__(self, attr):
        # return a Query object, this prevents us from having to
        # make pass-through functions for each Query param.
        # eg. Manager().filter() -> Query().filter()
        return getattr(Query(self), attr)

    @property
    def model_class(self):
        return self._model_class

    @property
    def count(self):
        """
        **property**: number of model instances we're holding
        """
        return len(self)

    @property
    def _name(self):
        """
        **property**: pretty version of our class name, based on our model
            eg. *MyModelManager*
        """
        return "{}Manager".format(self._model_class.__name__)

    @property
    def pks(self):
        """
        **property**: return all primary keys

        :rtype: ``list``
        """
        return self._instances.keys()

    @property
    def instances(self):
        """
        **property**: return all model instances

        :rtype: ``list``
        """
        return map( copy.copy, self._instances.itervalues() )


    @property
    def dirty(self):
        """
        **property**: return True if any model instances are dirty

        :rtype: ``bool``
        """
        if self._dirty:
            return True


    @staticmethod
    def sorter(elements, reverse=False ):
        """
        yield model instances in primary key order

        :param Manager.instances elements: our instances
        :param kw:
            * reverse: return in reverse order
        :rtype: ``generator``
        """
        for key in sorted( elements.iterkeys(), reverse=reverse ):
            yield elements[key]


    def save(self, instance, dirty=True, copy_instance=True):
        """
        Copy instance into our collection. We make a copy so that caller
        can't change its object and affect our version without calling
        save() again.

        :param Model instance:
        :param dirty: don't mark us as dirty if False, used during loading
        """
        #logger.debug( "saving model instance: %s", str(instance.pk) )
        signals.pre_save.send(self.model_class, instance=instance )

        assert instance.pk is not None, \
                "{}.save(): instance '{}' has None for pk".format(self._name, instance)

        if copy_instance:
            instance = self._instances[instance.pk] = copy.copy(instance)
        else:
            self._instances[instance.pk] = instance

        # THINK may be mistake to send the actual object out via the signal but probably
        # what any reciever actually wants
        signals.post_save.send( self.model_class, instance=instance )

        # self._dirty is required because think what would happen
        # if we add a clean model instance
        if dirty:
            self._dirty = True


    def clear(self):
        """
        remove all instances of our models. we'll be marked as
        dirty if we previously had model instances.

        **Note**: this does not affect on-disk files until
        :func:`Manager.save` is called.
        """
        logger.debug( "%s: clearing all models", self._name )

        self._dirty = len(self) > 0
        self._instances = {}


    def delete(self, instance):
        """
        remove an instance from our models by calling ``del`` on it

        :param Model instance:
        """
        # TODO should probably take an pk instead of an instance
        # logger.debug( "deleting model instance: %s", str(instance.pk) )

        signals.pre_delete.send(self.model_class, instance=instance)

        try:
            del self._instances[ instance.pk ]
            self._dirty = True

            signals.post_delete.send(self.model_class, instance=instance)
        except KeyError:
            pass


    def cb_delete_foreign(self, sender, instance ):
        """
        called when our foreign parent is about to be deleted
        """
        # keep in sync with metamodel._add_relmanagers()
        fk_set = self.model_class.__name__.lower() + '_set'

        # eg. instance.auxinfo_set.all()
        for elem in getattr(instance, fk_set).all():
            self.delete(elem)


    def store(self, storage, force=False):
        """
        save all our instances to storage

        :param Storage storage: an instance
        :param bool force: force save even if we're not dirty
        """
        assert not inspect.isclass(storage)

        if force:
            self._dirty = True

        if self.dirty:
            signals.pre_store.send(self.model_class)

            logger.debug( "%s: has dirty records, saving", self._name )
            logger.debug( "%s: storing models via storage class: %s", self._name, storage._name )

            gen = Manager.sorter(self._instances)
            storage.write(gen)

            logger.debug( "%s: finished storing %d records", self._name, len(self) )
            signals.post_store.send(self.model_class)
        else:
            logger.debug( "%s: has no dirty records, not saving", self._name )

        self._dirty = False


    def load(self, storage):
        """
        load all our instances from storage

        :param Storage storage: an instance
        :raises KeyError: if there are duplicate primary keys

        """
        def validate(elem):
            for fk_field_name in elem.Meta.field_filter(fields.ForeignKey):
                try:
                    getattr(elem, fk_field_name) # this does a lookup on foreign key object
                except KeyError:
                    # get elem's pk value, need to do it in this convoluted way since
                    # elem.pk might try to lookup the very thing that is missing
                    field_name = elem.Meta.pk_fields.keys()[0]
                    pk_value = elem.__dict__[field_name]
                    logger.warn( "%s.%s: foreign instance missing: %s",
                           self._model_class.__name__, elem.__dict__[fk_field_name], pk_value)

                    return False

            return True


        assert not inspect.isclass(storage)
        storage = IStorage(storage)
        logger.debug( "%s: loading models via storage class: %s", self._name, storage._name )

        signals.pre_load.send(self.model_class)

        self.clear()

        dirty = False

        for elem in storage.read( self._model_class ):
            if isinstance(elem, dict):
                elem = self._model_class( **elem )

            if not validate(elem):
                dirty = True
                continue

            if elem.pk in self._instances:
                raise KeyError( '%s: pk collision detected during load: %s' \
                        % (self._model_class.__name__, str(elem.pk)) )

            if elem.pk is None:
                raise KeyError( '%s: pk was None during load' \
                        % (self._model_class.__name__) )

            self.save(elem, dirty=False, copy_instance=False)


        self._dirty = dirty

        logger.debug( "%s: finished loading %d records", self._name, len(self) )
        signals.post_load.send(self.model_class)


    def get(self, *pk, **kw):
        """
        perform a query that returns a single instance of a model

        :param pk: optional primary key
        :type pk: value or ``tuple`` if multi-pk
        :param kw: optional ``field_name=value``
        :rtype: single :class:`alkali.model.Model` instance
        :raises KeyError: if 0 or more than 1 instance returned

        ::

            m = MyModel.objects.get(1)      # equiv to
            m = MyModel.objects.get(pk=1)

            m = MyModel.objects.get(some_field='a unique value')
            m = MyModel.objects.get(field1='a unique', field2='value')
        """
        # FIXME need to support direct access multi pk models

        # NOTE without this, direct access ForeignKeys are 100x slower
        if len(pk) == 1:
            pk = self.model_class.Meta.pk_fields.values()[0].cast(pk[0])
            return copy.copy( self._instances[pk] )

        results = Query(self).filter(**kw)

        if len(results) == 0:
            raise KeyError("{}: no results for: {}".format(
                self.model_class.__name__, str(kw)) )

        if len(results) > 1:
            raise KeyError("{}: got {} results  for: {}".format(
                self.model_class.__name__, len(results), str(kw)) )

        return results[0]
