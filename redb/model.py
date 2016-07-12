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
        self._modified = False

    def __repr__(self):
        return "<{}: {}>".format(self.name, self.pk)

    def __setattr__(self, attr, val):
        # if we're setting a field value and that value is different
        # than current value, mark self as modified
        if attr in self.meta.fields:
            if hasattr(self,attr):
                curr_val = getattr(self,attr)
                if curr_val != val:
                    self.__dict__['_modified'] = True
            self.__dict__[attr] = self.meta.fields[attr].cast(val)
        else:
            self.__dict__[attr] = val

    @property
    def modified(self):
        return self._modified

    @property
    def meta(self):
        return self.__class__.Meta

    @property
    def name(self):
        return self.__class__.__name__

    @property
    def schema(self):
        def fmt(name, field):
            return "{}:{}".format(name, field.field_type.__name__)

        name_type = [ fmt(n,f) for n,f in self.meta.fields.items() ]
        fields = ", ".join( name_type )
        return "<{} {}>".format(self.name, fields)

    @property
    def pk(self):
        """return the primary key value or a tuple of them"""
        pks = map( lambda name: getattr(self, name), self.meta.pk_fields )

        if len(pks) == 1:
            return pks[0]

        return tuple(pks)

    @property
    def dict(self):
        return { name: field.dumps( getattr(self,name) )
                for name, field in self.meta.fields.items() }

    def save(self):
        self.__class__.objects.save(self)
