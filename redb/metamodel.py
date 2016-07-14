from collections import OrderedDict
import copy

from .fields import Field

# from: http://stackoverflow.com/questions/12006267/how-do-django-models-work
# from: lib/python2.7/site-packages/django/db/models/base.py
#
# remember that `type` is actually a class like `str` and `int`
# so you can inherit from it
class MetaModel(type):
    """
    base class for Models. this complicated metaclass is required to convert
    a stylized class into a useful concrete one.

    it converts Field() variables into their base types as attributes on the
    instantiated class.
    """

    # __new__ is the method called before __init__
    # meta_class is _this_ class, aka: MetaModel
    # this makes a new MetaModel instance, I'm not sure why we want to
    # do that
    def __new__(meta_class, name, bases, attrs):
        #print "__new__ cls:",type(meta_class),meta_class,name
        super_new = super(MetaModel, meta_class).__new__

        # Also ensure initialization is only performed for subclasses of Model
        # (excluding Model class itself). This keeps all of Models attrs intact.
        parents = [b for b in bases if isinstance(b, MetaModel)]
        if not parents:
            new_class = super_new(meta_class, name, bases, attrs)
            return new_class

        # new_class is an instance of 'name' (aka Model) whose type is MetaModel
        # print "new_class", type(new_class), new_class
        # new_class <class 'redb.metamodel.MetaModel'> <class 'redb.metamodel.MyModel'>
        new_class = super_new(meta_class, name, bases, {})
        new_class._add_meta( attrs )
        new_class._add_manager()

        # put the rest of the attributes (methods and properties)
        # defined in the Model derived class into the "new" Model
        for name, attr in attrs.items():
            setattr(new_class, name, attr)

        setattr( new_class, 'name', new_class.__name__ )

        return new_class

    def _add_manager( new_class ):
        from .manager import Manager
        setattr( new_class, 'objects', Manager(new_class) )

    @property
    def pk_fields(new_class):
        return [name for name,field in new_class.Meta.fields.items() if field.primary_key]

    def _add_meta( new_class, attrs ):
        class Object(object): pass

        meta = attrs.pop( 'Meta', Object() )
        setattr( new_class, 'Meta', meta )

        if not hasattr(meta, 'filename'):
            meta.filename = ''

        if not hasattr(meta, 'storage'):
            meta.storage = ''

        if not hasattr(meta, 'ordering'):
            meta.ordering = []

        ordering = meta.ordering or [k for k,v in attrs.items() if isinstance(v,Field)]

        meta.fields = OrderedDict()

        for field in ordering:
            meta.fields[field] = attrs.pop(field)

        # HACK I can't figure out how to set a property function on Meta directly
        # meta.pk_fields is a property
        meta.pk_fields = new_class.pk_fields

    # creates a new instance of derived model
    def __call__(self, *args, **kw):
        kw_fields={}
        for name,_ in self.Meta.fields.items():
            kw_fields[name] = kw.pop(name, None)

        # obj is a instance of Model (or a derived class)
        obj = type.__call__(self, *args, **kw) # this calls obj.__init__

        for name, value in kw_fields.items():
            value = self.Meta.fields[name].cast(value)
            setattr(obj, name, value)

        return obj
