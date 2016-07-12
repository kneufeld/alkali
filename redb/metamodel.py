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
            #meta_class._add_fields( new_class, {}, {} )
            return new_class

        # new_class is an instance of 'name' (aka Model) whose type is MetaModel
        new_class = super_new(meta_class, name, bases, {})
        # print "new_class", type(new_class), new_class
        # new_class <class 'redb.metamodel.MetaModel'> <class 'redb.metamodel.MyModel'>

        new_class._prepare( attrs )
        #new_class._meta.apps.register_model(new_class._meta.app_label, new_class)

        return new_class

    # creates a new instance of derived model
    def __call__(self, *args, **kw):
        #print "__call__ self:",type(self),self
        # First, create the object in the normal default way.
        fields={}
        for name, field in self.Meta.fields.items():
            fields[name] = kw.pop(name, None)#field.field_type())

        obj = type.__call__(self, *args, **kw)

        for name, value in fields.items():
            value = self.Meta.fields[name].loads(value)
            setattr(obj, name, value)

        return obj

    def _prepare( new_class, attrs ):
        class Object(object): pass

        meta = attrs.pop( 'Meta', Object() )
        setattr( new_class, 'Meta', meta )

        setattr( new_class, 'name', new_class.__name__ )

        if not hasattr(new_class.Meta, 'filename'):
            new_class.Meta.filename = ''

        if not hasattr(new_class.Meta, 'storage'):
            new_class.Meta.storage = ''

        if not hasattr(new_class.Meta, 'ordering'):
            new_class.Meta.ordering = []

        new_class._add_fields( new_class.Meta, attrs )
        new_class._add_manager( new_class.Meta, attrs )

    @property
    def pk_fields(new_class):
        return [name for name,field in new_class.Meta.fields.items() if field.primary_key]

    def _add_fields( new_class, meta, attrs):
        "put fields in meta class"
        ordering = meta.ordering or [k for k,v in attrs.items() if isinstance(v,Field)]

        meta.fields = OrderedDict()

        for field in ordering:
            meta.fields[field] = attrs[field]

        # HACK I can't figure out how to set a property function on Meta directly
        # meta.pk_fields is a property
        meta.pk_fields = new_class.pk_fields


    def _add_manager( new_class, meta, attrs ):
        from .manager import Manager
        setattr( new_class, 'objects', Manager(new_class) )
