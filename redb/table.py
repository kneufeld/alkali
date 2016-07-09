from zope.interface import Interface, Attribute, implements
import datetime as dt

from .fields import Field

class ITable( Interface ):

    modified   = Attribute("are any fields dirty")
    fields     = Attribute("the dict of fields")

class Table(object):
    implements(ITable)

    def __init__( self, *args, **kw ):
        self._fields = {}
        self.__get_fields()

    def __get_fields(self):
        # the interesting fields are attached to the class, not
        # the instance
        for k,v in self.__class__.__dict__.items():
            if isinstance( v, Field ):
                self._fields[k]=v

    @property
    def name(self):
        return self.__class__.__name__

    @property
    def fields(self):
        return self._fields

    @property
    def modified(self):
        return False
        return any( [field.modifed for name,field in self.fields] )
