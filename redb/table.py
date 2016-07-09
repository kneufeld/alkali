from zope.interface import Interface, Attribute, implements
import copy
import os

from .fields import Field
from .metatable import MetaTable

class ITable( Interface ):

    pass
    # modified   = Attribute("are any fields dirty")
    # fields     = Attribute("the dict of fields")

class Table(object):
    __metaclass__ = MetaTable
    implements(ITable)

    def __init__( self, *args, **kw ):
        self._filename = kw.pop('filename',None)
        self._storage_type = kw.pop('storage',None)

        # make sure at least one field is the primary key
        #assert any( [field.primary_key for name,field in self.fields.items()] )

    def __str__(self):
        try:
            basename = ' ' + os.path.basename( self.filename )
        except AttributeError:
            basename = ''
        return "<{name}{fname}>".format(name=self.name, fname=basename)

    @property
    def name(self):
        return self.__class__.__name__

    @property
    def schema(self):
        ret = "<{} {{".format(self.name)

        for k,v in self.fields.items():
            nice_type = v.field_type.__name__
            ret += '{}:{}, '.format(k,nice_type)

        ret += "}>"
        return ret

    @property
    def filename(self):
        return self._filename

    @property
    def storage(self):
        return self._storage_type

    @property
    def fields(self):
        return self._fields

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
