from zope.interface import Interface, Attribute, implements
import copy
import os

from .fields import Field
from .metamodel import MetaModel

class IModel( Interface ):

    dict   = Attribute("represent our data as a dict")


class Model(object):
    """
    main class for any database. this holds the actual data of the database.
    """
    __metaclass__ = MetaModel
    implements(IModel)

    def __init__( self, *args, **kw ):
        pass

    def __str__(self):
        return "<{}: {}>".format(self.name, self.pk)

    @property
    def name(self):
        return self.__class__.__name__

    @property
    def schema(self):

        fields = ", ".join(
                [ "{}:{}".format(name, field.field_type.__name__)
                  for name, field in self.fields.items() ]
                )
        return "<{} {}>".format(self.name, fields)


    @property
    def filename(self):
        try:
            return self.Meta.filename
        except AttributeError:
            return None

    @property
    def storage(self):
        try:
            return self.Meta.storage
        except AttributeError:
            return None

    @property
    def fields(self):
        return self.__class__._fields

    @property
    def modified(self):
        return any( [field.modified for name,field in self.fields.items()] )

    @property
    def pk(self):
        """return the primary key or a tuple of them"""
        pks = [name for name,field in self.fields.items() if field.primary_key]
        pks = map( lambda name: getattr(self, name), pks )

        if len(pks) == 1:
            return pks[0]

        return tuple(pks)

    @property
    def dict(self):

        return { name: field.dumps( getattr(self,name) )
                for name, field in self.fields.items() }
