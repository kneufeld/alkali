from zope.interface import Interface, Attribute, implements
import copy

from .fields import Field

class ITable( Interface ):

    modified   = Attribute("are any fields dirty")
    fields     = Attribute("the dict of fields")

class Table(object):
    implements(ITable)

    def __init__( self, *args, **kw ):
        self._filename = kw.pop('filename',None)
        self._storage_type = kw.pop('storage',None)

        self._fields = {}
        self.__get_fields()
        self.__set_fields(**kw)

    def __get_fields(self):
        # the interesting fields are attached to the class, not
        # the instance, copy them into self._fields
        for k,v in self.__class__.__dict__.items():
            if isinstance( v, Field ):
                self._fields[k] = copy.deepcopy(v)

    def __set_fields(self, **kw):
        for k,v in kw.items():
            if k in self.fields:
                self.fields[k].value = kw.pop(k)

    def __getattr__(self, name):
        try:
            fields = self.__dict__['fields']
            return fields[name]
        except KeyError:
            raise AttributeError( 'no attribute %s' % name )
    def __str__(self):
        return "<{name} {fname}>".format(
                name=self.__class__.__name__, fname=self.filename
                )

    @property
    def name(self):
        return self.__class__.__name__

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
        return False
        return any( [field.modifed for name,field in self.fields] )
