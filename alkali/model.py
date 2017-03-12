from zope.interface import Interface, Attribute, implements
from collections import OrderedDict
import json

from .memoized_property import memoized_property
from .metamodel import MetaModel
from . import fields
from . import signals

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

    def __init__(self, *args, **kw):
        # MetaModel.__call__ has put fields in self,
        # put any other keywords into self
        for name, value in kw.iteritems():
            setattr(self, name, value)

        # note, this is called twice, once during initial object creation
        # and then again when this object is copied during a save
        signals.creation.send(self.__class__, instance=self)

    # called via copy.copy() module, when getting from manager
    def __copy__(self):
        new = type(self)()
        new.__dict__.update(self.__dict__)
        return new

    def __repr__(self):
        return "<{}: {}>".format(self.__class__.__name__, self.pk)

    def __eq__(self, other):
        # this is obviously a very shallow comparison
        return type(self) == type(other) and self.pk == other.pk

    def __ne__(self, other):
        return not self.__eq__(other)

    def set_field(self, field, value):
        """
        set a field value, this method is automatically called when setting
        a field value. safe to call externally.

        fires :data:`alkali.signals.field_update` for any listeners

        :param field: instance of Field
        :type field: :class:`alkali.fields.Field`
        :param value: the already-cast value to store
        :type value: ``Field.field_type``
        """
        # if we're setting a field value and that value is different
        # than current value, mark self as modified

        curr_val = getattr(self, field.name)

        # do not let user change pk after it has been set
        if field.primary_key:
            if curr_val is not None and curr_val != value:
                _vals = (self.__class__.__name__, self.pk, value)
                raise RuntimeError( "{}: trying to change set pk value: {} to {}".format(*_vals) )

        self.__dict__[field.name] = value # actually set the value

        if curr_val != value:
            self.__dict__['_dirty'] = True
            signals.field_update.send(self.__class__, field=field.name, old_val=curr_val, new_val=value)

    @property
    def dirty(self):
        """
        **property**: return True if our fields have changed since creation
        """
        return self._dirty

    @property
    def schema(self):
        """
        **property**: a string that quickly shows the fields and types
        """
        def fmt(name, field):
            return "{}:{}".format(name, field.field_type.__name__)

        name_type = [ fmt(n,f) for n,f in self.Meta.fields.iteritems() ]
        fields = ", ".join( name_type )
        return "<{}: {}>".format(self.__class__.__name__, fields)

    @memoized_property
    def pk(self):
        """
        **property**: returns this models primary key value. If the model is
        comprised of serveral primary keys then return a tuple of them.

        :rtype: ``Field.field_type`` or tuple-of-Field.field_type
        """
        pks = self.Meta.pk_fields.values()
        foreign_pks = filter(lambda f: isinstance(f, fields.ForeignKey), pks)

        if foreign_pks:
            pk_vals = tuple( getattr(self, f.name).pk for f in pks )
            if len(pk_vals) == 1:
                return pk_vals[0]
            return pk_vals # pragma: nocover, not actually supported at this time
        else:
            pk_vals = tuple( getattr(self, f.name) for f in pks )
            if len(pk_vals) == 1:
                return pk_vals[0]
            return pk_vals

    @property
    def dict(self):
        """
        **property**: returns a dict of all the fields, the fields are
        json consumable

        :rtype: ``OrderedDict``
        """
        return OrderedDict( [(name, field.dumps(getattr(self, name)))
                for name, field in self.Meta.fields.iteritems() ])

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
        return self
