from collections import OrderedDict
import copy

from .fields import Field

# from: http://stackoverflow.com/questions/12006267/how-do-django-models-work
#
# remember that `type` is actually a class like `str` and `int`
# so you can inherit from it
class MetaTable(type):

    # __new__ is the method called before __init__
    # meta_class is _this_ class, aka: MetaTable
    # this makes a new MetaTable instance, I'm not sure why we want to
    # do that
    def __new__(meta_class, name, bases, attrs):
        #print "__new__ cls:",type(meta_class),meta_class,name
        super_new = super(MetaTable, meta_class).__new__

        # Also ensure initialization is only performed for subclasses of Model
        # (excluding Model class itself). This keeps all of Tables attrs intact.
        parents = [b for b in bases if isinstance(b, MetaTable)]
        if not parents:
            new_class = super_new(meta_class, name, bases, attrs)
            meta_class.add_fields( new_class, {}, {} )
            return new_class

        # new_class is an instance of 'name' (aka Table) whose type is MetaTable
        new_class = super_new(meta_class, name, bases, {})
        # print "new_class", type(new_class), new_class
        # new_class <class 'redb.metatable.MetaTable'> <class 'redb.metatable.MyTable'>

        meta = attrs.pop('Meta', {})
        meta_class.add_fields( new_class, meta, attrs )

        assert hasattr(new_class,'_fields')
        return new_class

    # creates a new instance of derived table
    def __call__(self, *args, **kw):
        #print "__call__ self:",type(self),self
        # First, create the object in the normal default way.
        fields={}
        for name, field in self._fields.items():
            fields[name] = kw.pop(name, None)#field.field_type())

        obj = type.__call__(self, *args, **kw)

        for name, value in fields.items():
            setattr(obj, name, value)

        return obj

    def add_fields( new_class, meta, attrs):
        try:
            ordering = meta.ordering
        except AttributeError:
            ordering = [k for k,v in attrs.items() if isinstance(v,Field)]

        setattr(new_class, '_fields', OrderedDict())

        for k in ordering:
            new_class._fields[k] = copy.deepcopy( attrs[k] )
