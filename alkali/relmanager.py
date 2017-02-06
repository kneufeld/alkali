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
        :param Model foreign: instance of the model that is pointed at
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
                self._foreign.__class__.__name__,
                self._child_class.__name__,
                self._child_field )

    @property
    def foreign(self):
        return self._foreign

    @property
    def child_class(self):
        return self._child_class

    @property
    def child_field(self):
        return self._child_field

    def add(self, child):
        assert isinstance(child, self.child_class)
        setattr(child, self.child_field, self.foreign)
        return child

    def create(self, **kw):
        assert self.child_field not in kw, "can't pass in foreign key value to create"
        child = self.child_class(**kw)
        child = self.add(child)
        return child

    def all(self):
        """
        get all objects that point to this instance
        see :func:`alkali.manager.Manager.all` for syntax

        :rtype: :class:`alkali.query.Query`
        """
        return self.child_class.objects.filter(**{self.child_field: self.foreign})

    def get(self, **kw):
        """
        get a single object that refers to this instance
        see :func:`alkali.manager.Manager.get` for syntax

        :rtype: :class:`alkali.model.Model`
        """
        if not kw:
            return self.child_class.objects.get( **{self.child_field: self.foreign} )

        return self.child_class.objects.get(**kw)
