from zope.interface import Interface, Attribute, implements
import json

from .metamodel import MetaModel

class IModel( Interface ):

    dict   = Attribute("represent our data as a dict")


class Model(object):
    """
    main class for the database.

    the definition of this class defines a table schema but instances of
    this class hold a row.

    model fields are available as attributes. eg. ``m.my_field = 'foo'``

    the Django docs at https://docs.djangoproject.com/en/1.10/topics/db/models/
    will be fairly relevant to alkali

    see :mod:`alkali.database` for some example code
    """
    __metaclass__ = MetaModel
    implements(IModel)

    def __new__(cls, *args, **kw):
        # return a new instance of Model (or derived type)
        #
        # MetaModel.__call__ calls this method and passes in our fields.
        # we need to add the fields before Model.__init__ is called so
        # that they exist and can be referenced

        # obj is a instance of Model (or a derived class)
        obj = super(Model,cls).__new__(cls)

        meta_fields = obj.Meta.fields # local cache
        kw_fields = kw.pop('kw_fields')
        for name, value in kw_fields.items():
            value = meta_fields[name].cast(value)
            setattr(obj, name, value)

        for name, value in kw.items():
            setattr(obj, name, value)

        setattr( obj, '_dirty', False )

        return obj

    def __repr__(self):
        return "<{}: {}>".format(self.name, self.pk)

    def __setattr__(self, attr, val):
        # if we're setting a field value and that value is different
        # than current value, mark self as modified
        if attr in self.meta.fields:
            if hasattr(self,attr):
                curr_val = getattr(self,attr)
                if curr_val != val:
                    self.__dict__['_dirty'] = True
            self.__dict__[attr] = self.meta.fields[attr].cast(val)
        else:
            self.__dict__[attr] = val

    def __eq__(self, other):
        # this is obviously a very shallow comparison
        return self.pk == other.pk

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def dirty(self):
        """
        **property**: return True if our fields have changed since creation
        """
        return self._dirty

    @property
    def meta(self):
        """
        **property**: return this class's ``Meta`` class

        :rtype: ``Meta``
        """
        return self.__class__.Meta

    # this property exists on the instance
    @property
    def name(self):
        """
        **property**: shortcut to our class name
        """
        return self.__class__.__name__

    @property
    def schema(self):
        """
        **property**: a string that quickly shows the fields and types
        """
        def fmt(name, field):
            return "{}:{}".format(name, field.field_type.__name__)

        name_type = [ fmt(n,f) for n,f in self.meta.fields.items() ]
        fields = ", ".join( name_type )
        return "<{} {}>".format(self.name, fields)

    @property
    def pk(self):
        """
        **property**: returns this models primary key. If the model is
        comprised of serveral primary keys then return a tuple of them.

        :rtype: :class:`alkali.fields.Field` or tuple-of-Field
        """
        pks = map( lambda name: getattr(self, name), self.meta.pk_fields )

        if len(pks) == 1:
            return pks[0]

        return tuple(pks)

    @property
    def dict(self):
        """
        **property**: returns a dict of all the fields, the fields are
        json consumable

        :rtype: ``dict``
        """
        return { name: field.dumps( getattr(self,name) )
                for name, field in self.meta.fields.items() }

    @property
    def json(self):
        """
        **property**: returns json that holds all the fields

        :rtype: ``str``
        """
        return json.dumps(self.dict)

    def save(self):
        """
        add ourselves to our :class:`alkali.manager.Manager` and mark
        ourselves as no longer dirty.

        it's up to our ``Manager`` to persistently save us
        """
        self.__class__.objects.save(self)
        self._dirty = False
