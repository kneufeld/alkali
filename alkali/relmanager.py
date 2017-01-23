from zope.interface import Interface, implements
import inspect

from .query import Query

import logging
logger = logging.getLogger(__name__)

class IRelManager( Interface ):
    pass

class RelManager(object):
    """
    This is an internal class that a user of alkali unlikely to use directly.

    The ``RelManager`` class manages queries/connections between two
    models that have a :class:`alkali.fields.ForeignKey` (or equivalent) field.
    """
    implements(IRelManager)

    def __init__( self, foreign, child_class, child_field ):
        """
        :param Model foregin: instance of the model that is pointed at
        :param Model child_class: the model class that contains the ForeignKey
        :param str child_field: the field name that points to ForeignKey
        """
        assert not inspect.isclass(foreign)
        assert inspect.isclass(child_class)
        assert isinstance(child_field, str)

        self._foreign = foreign
        self._child_class = child_class
        self._child_field = child_field

    def __repr__(self):
        return "RelManager<{} <- {}.{}>".format(
                self._foreign.__class__.__name__, self._child_class.__name__, self._child_field)

    @property
    def foreign(self):
        return self._foreign

    @property
    def child_class(self):
        return self._child_class

    @property
    def child_field(self):
        return self._child_field

    @property
    def name(self):
        """
        **property**: easy to call version of str(self)
        """
        return str(self)


    def clear(self):
        """
        remove all instances of our models. we'll be marked as
        dirty if we previously had model instances.

        **Note**: this does not affect on-disk files until
        :func:`alkali.manager.Manager.save` is called.
        """
        return
        # THINK when foreign is deleted should we delete
        # child instances?
        logger.debug( "%s: clearing all models", self.name )

        self._dirty = len(self) > 0
        self._instances = {}

    def add(self, instance):
        assert isinstance(instance, self.child_class)
        setattr(instance, self.child_field, self)
        return instance

    def create(self, **kw):
        assert self.child_field not in kw
        child = self.child_class(**kw)
        return self.add(child)

    def remove(self, instance):
        """
        remove an instance from our models by calling ``del`` on it

        :param Model instance:
        """
        return
        # THINK when foreign is deleted should we delete
        # child instances?

        # TODO should probably take an pk instead of an instance
        logger.debug( "deleting model instance: %s", str(instance.pk) )

        try:
            del self._instances[ instance.pk ]
            self._dirty = True
        except KeyError:
            pass


    def all(self):
        """
        get all objects that point to this instance

        :rtype: :class:`alkali.query.Query`
        """
        return self.child_class.objects.filter(**{self.child_field: self.foreign})


    def get(self, **kw):
        """
        perform a query that returns a single instance of a model

        :param kw: optional ``field_name=value``
        :rtype: single :class:`alkali.model.Model` instance
        :raises KeyError: if number of results != 1

        ::

            m = MyModel.objects.get(1)      # equiv to
            m = MyModel.objects.get(pk=1)

            m = MyModel.objects.get(some_field='a unique value')
            m = MyModel.objects.get(field1='a unique', field2='value')
        """
        results = self.child_class.objects.get(**kw)

        if len(results) == 0:
            raise KeyError("got no results")

        if len(results) > 1:
            raise KeyError("got more than 1 result (%d)" % len(results) )

        return results[0]
