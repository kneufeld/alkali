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

        def fmt(name, field):
            return "{}:{}".format(name, field.field_type.__name__)

        name_type = [ fmt(n,f) for n,f in self.fields.items() ]
        fields = ", ".join( name_type )
        return "<{} {}>".format(self.name, fields)

    @property
    def modified(self):
        return any( [field.modified for name,field in self.fields.items()] )

    @property
    def fields(self):
        return self.Meta.fields

    @property
    def pk_fields(self):
        return [name for name,field in self.Meta.fields.items() if field.primary_key]

    @property
    def pk(self):
        """return the primary key value or a tuple of them"""
        pks = map( lambda name: getattr(self, name), self.pk_fields )

        if len(pks) == 1:
            return pks[0]

        return tuple(pks)

    @property
    def dict(self):

        return { name: field.dumps( getattr(self,name) )
                for name, field in self.fields.items() }

    def save(self):
        self.__class__.objects.save(self)
