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
    *do not use this class directly*

    *code reviews of this class are vey welcome*

    base class for :class:`alkali.model.Model`. this complicated
    metaclass is required to convert a stylized class into a useful
    concrete one.

    it converts :class:`alkali.fields.Field` variables into their base
    itypes as attributes on the nstantiated class.

    **Meta**: adds a ``Meta`` class if not already defined in ``Model`` derived class

    **objects**: :class:`alkali.manager.Manager`
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
        if not any( map( lambda b: isinstance(b, MetaModel), bases ) ):
            new_class = super_new(meta_class, name, bases, attrs)
            return new_class

        # new_class is an instance of 'name' (aka Model) whose type is MetaModel
        # print "new_class", type(new_class), new_class
        # new_class <class 'alkali.metamodel.MetaModel'> <class 'redb.metamodel.MyModel'>
        new_class = super_new(meta_class, name, bases, {})
        new_class._add_meta( attrs )
        new_class._add_manager()

        # put the rest of the attributes (methods and properties)
        # defined in the Model derived class into the "new" Model
        for name, attr in attrs.items():
            setattr(new_class, name, attr)

        return new_class

    def _add_manager( new_class ):
        from .manager import Manager
        setattr( new_class, 'objects', Manager(new_class) )

    # this attribute exists on the class
    @property
    def name(new_class):
        return new_class.__name__

    def _add_meta( new_class, attrs ):

        def _get_fields( attrs ):
            return [(k,v) for k,v in attrs.items() if isinstance(v,Field)]

        def _get_field_order(attrs):
            fields = _get_fields(attrs)
            fields.sort(key=lambda e: e[1]._order)
            return [k for k,v in fields]

        class Object(object): pass

        meta = attrs.pop( 'Meta', Object )
        setattr( new_class, 'Meta', meta )

        if not hasattr(meta, 'filename'):
            meta.filename = None

        if not hasattr(meta, 'storage'):
            meta.storage = None

        if not hasattr(meta, 'ordering'):
            meta.ordering = _get_field_order(attrs)

        # don't let user miss a field if they've defined Meta.ordering
        assert len(meta.ordering) == len(_get_fields(attrs)), "missing/extra fields defined in Meta.ordering"

        meta.fields = OrderedDict()
        for field in meta.ordering:
            meta.fields[field] = attrs.pop(field)
            delattr( meta.fields[field], '_order' )

        # you can set a property on a class but it will only be called on an instance
        # I'd prefer this to be a read-only property but I guess that can't happen
        meta.pk_fields = [name for name,field in meta.fields.items() if field.primary_key]

    # creates a new instance of derived model
    def __call__(self, *args, **kw):
        kw_fields=OrderedDict()
        for name,_ in self.Meta.fields.items():
            kw_fields[name] = kw.pop(name, None)
        kw['kw_fields'] = kw_fields

        # this calls Model.__new__ and then Model.__init__
        return type.__call__(self, **kw)
