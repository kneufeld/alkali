from zope.interface import Interface, Attribute, implements
from collections import OrderedDict
import inspect
import os

from .query import Query
from .storage import IStorage

import logging
logger = logging.getLogger(__name__)

class IManager( Interface ):

    pass

class Manager(object):
    """
    the Manaager class holds the data of the database. It could rightly be
    called Table.
    """
    implements(IManager)

    def __init__( self, model_class, *args, **kw ):
        self._model_class = model_class
        self._instances = {}
        self._dirty = False

        self.clear()

    def __repr__(self):
        return "<{}: {}>".format(self.name, len(self))

    def __len__(self):
        return len(self._instances)

    @property
    def count(self):
        return len(self)

    @property
    def name(self):
        return "{}Manager".format(self._model_class.__name__)

    @property
    def pks(self):
        "return all primary keys in sorted order"
        return self._instances.keys()

    @property
    def instances(self):
        "return list of model instances"
        return [elem for elem in Manager.sorter(self._instances)]

    @property
    def dirty(self):
        if self._dirty:
            return True

        return any( map( lambda e: e.dirty, self.instances ) )

    @staticmethod
    def sorter(elements, **kw ):
        """
        yield elements in key order
        pass in reverse=True for reverse order
        """
        keys = sorted( elements.keys(), **kw )
        for key in keys:
            yield elements[key]


    def save(self, instance, dirty=True):
        #logger.debug( "saving model instance: %s", str(instance.pk) )

        assert instance.pk is not None
        self._instances[ instance.pk ] = instance

        if dirty:
            self._dirty = True

    def clear(self):
        logger.debug( "%s: clearing all models", self.name )

        self._dirty = len(self._instances) > 0
        self._instances = {}

    def delete(self, instance):
        logger.debug( "deleting model instance: %s", str(instance.pk) )

        try:
            del self._instances[ instance.pk ]
            self._dirty = True
        except KeyError:
            pass

    def store(self, storage, force=False):
        "save all our instances to storage"
        assert not inspect.isclass(storage)

        if force:
            self._dirty = True

        if self.dirty:
            logger.debug( "%s: has dirty records, saving", self.name )
            logger.debug( "%s: storing models via storage class: %s", self.name, storage.name )

            storage.write( Manager.sorter(self._instances) )
        else:
            logger.debug( "%s: has no dirty records, not saving", self.name )

        self._dirty = False


    def load(self, storage):
        "load all our instances from storage"

        storage = IStorage(storage)

        self.clear()

        logger.debug( "%s: loading models via storage class: %s", self.name, storage.name )

        for elem in storage.read( self._model_class ):
            if isinstance(elem, dict):
                elem = self._model_class( **elem )

            if elem.pk in self._instances:
                raise RuntimeError( 'pk collision detected during load: %s' % str(elem.pk) )

            # this adds elem to our internal list
            self.save(elem, dirty=False)

        logger.debug( "%s: finished loading", self.name )


    def get(self, *args, **kw):
        """
        return an instance of a model
        """
        if len(args):
            kw['pk'] = args[0]

        results = Query(self).filter(**kw).instances

        if len(results) == 0:
            raise KeyError("got no results")

        if len(results) > 1:
            raise KeyError("got more than 1 result")

        return results[0]

    def filter(self, **kw):
        """
        return a Query, aka a subset of model instances
        """
        return Query(self).filter(**kw)

    def all(self):
        """
        return a full Query, aka list of all model instances
        """
        return Query(self)
