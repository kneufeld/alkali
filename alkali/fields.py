import datetime as dt
import dateutil.parser
import itertools
import types

from .utils import tzadd, tznow

import logging
logger = logging.getLogger(__name__)


class Field(object):
    """
    Base class for all field types. it tries to hold all the functionality
    so derived classes only need to override methods in special circumstances.

    Field objects are instantiated during model creation. ``i = IntField()``

    All Model instances share the same instantiated Field objects in their
    Meta class. ie: ``id(MyModel().Meta.fields['i']) == id(MyModel().Meta.fields['i'])``

    Fields are python descriptors (@property is also a descriptor). So when a field
    is get/set the actual value is stored in the parent model instance.

    The actual Field() object is accessable via model().Meta.fields[field_name] or
    via dynamic lookup of <field_name>__field. eg. m.email__field.
    """

    _counter = itertools.count() # keeps track of declaration order in the Models

    def __init__(self, field_type, **kw):
        """
        :param field_type: the type this field should hold
        :type field_type: str/int/float/etc
        :param kw:
            * primary_key: is this field a primary key of parent model
            * indexed:     is this field indexed (not implemented yet)
        """
        self._order = Field._counter.next() # DO NOT TOUCH, deleted in MetaModel

        assert field_type is not None
        self._field_type = field_type

        self._properties = ['primary_key', 'indexed',
                'auto_increment', 'auto_now', 'auto_now_add']

        # create a getter property based on _properties list
        # self.property_name returns self._property_name
        for name in self._properties:
            val = kw.pop(name, None)
            name = '_'+name
            setattr(self, name, val)

            fget = lambda self, name=name: getattr(self, name)
            setattr( self.__class__, name[1:], property(fget=fget) )

        assert len(kw) == 0, "unhandeled kwargs: {}".format(str(kw))

    def __get__(self, model, owner):
        """
        Field is a descriptor `python.org <https://docs.python.org/2/howto/descriptor.html>`_.

        return the value stored in model's __dict__ (stored via __set__ below)
        """
        if model is None:
            return self

        return model.__dict__[self._name]

    def __set__(self, model, value):
        """
        Cast the value via individual Field rules and then store the value
        in model instance.

        This allows the same Field instance to "save" multiple values because
        the actual value is in a different model instance.
        """
        # WARNING: if it existed, Model.__setattr__ would intercept this method
        value = self.cast(value)
        model.set_field(self, value)

    def __str__(self):
        # name is set via MetaModel during Model creation
        name = getattr(self, 'name', '')
        return "<{}: {}>".format(self.__class__.__name__, name)

    @property
    def field_type(self):
        """
        **property**: return ``type`` of this field (int, str, etc)
        """
        return self._field_type

    @property
    def properties(self):
        """
        **property**: return list of possible Field properties
        """
        return self._properties

    @property
    def default_value(self):
        """
        **property**: what value does this Field default to during
        model instantiation
        """
        return None

    def cast(self, value):
        """
        Whenever a field value is set, the given value passes through
        this (or derived class) function. This allows validation plus
        helpful conversion.

        ::
            int_field = "1"             # converts to int("1")
            date_field = "Jan 1 2017"   # coverted to datetime()
        """
        if value is None:
            return None

        # simple cast, eg. int(value)
        return self._field_type(value)

    def dumps(self, value):
        """
        called during json serialization, if json module is unable to
        deal with given Field.field_type, convert to a known type here.
        """
        return value

    def loads(self, value):
        """
        called during json serialization, if json module is unable to
        deal with given Field.field_type, convert to a known type here.
        """
        return value


class IntField(Field):

    def __init__(self, **kw):
        super(IntField, self).__init__(int, **kw)

    @property
    def default_value(self):
        """
        IntField implements auto_increment, useful for a primary_key. The
        value is incremented during model instantiation.
        """
        if self.auto_increment:
            val = getattr(self.meta, '_auto__' + self.name, 0) + 1
            setattr( self.meta, '_auto__' + self.name, val )
            return val

        return None


class FloatField(Field):

    def __init__(self, **kw):
        super(FloatField, self).__init__(float, **kw)


class StringField(Field):
    """
    holds a unicode string
    """

    def __init__(self, **kw):
        super(StringField, self).__init__(unicode, **kw)

    def cast(self, value):
        if value is None:
            return None

        if type(value) is not self._field_type:
            try:
                return self.field_type(value)
            except UnicodeDecodeError:
                # assume value is a utf-8 byte string
                return self.field_type( value.decode('utf-8') )

        return value


class DateTimeField(Field):

    def __init__(self, **kw):
        super(DateTimeField, self).__init__(dt.datetime, **kw)

    # TODO def default_value: auto_now, auto_now_add

    def cast(self, value):
        """
        make sure date always has a time zone
        """
        if value is None:
            return None

        if isinstance(value, types.StringTypes):
            if value == 'now':
                value = tznow()
            else:
                return self.loads(value)

        if type(value) is not self.field_type:
            value = self.field_type(value)

        return tzadd( value )

    def dumps(cls, value):
        if value is None:
            return 'null'
        return value.isoformat()

    def loads(cls, value):
        if value is None or value == 'null':
            return None

        # assume date is in isoformat, this preserves timezone info
        if isinstance(value, types.StringTypes):
            value = dateutil.parser.parse(value)

        if value.tzinfo is None:
            value = tzadd( value )

        return value


class SetField(Field):

    def __init__(self, **kw):
        super(SetField, self).__init__(set, **kw)


class ForeignKey(Field):
    """
    A ForeignKey is a special type of field. It stores the same value
    as a primary key in another field. When the model gets/sets a
    ForeignKey the appropriate lookup is done in the remote manager
    to return the remote instance.
    """

    def __init__(self, foreign_model, **kw):
        """
        :param foreign_model: the Model that this field is referencing
        :type foreign_model: :class:`alkali.model.Model`
        :param kw:
            * primary_key: is this field a primary key of parent model
        """
        from .model import Model

        # TODO treat foreign_model as model name and lookup in database
        # if isinstance(foreign_model, types.StringTypes):
        #     foreign_model = <db>.get_model(foreign_model)

        self.foreign_model = foreign_model

        # a Model is an instance of MetaModel so type(foreign_model) == MetaModel
        # an instance of a Model is of course a Model. type(Model()) == Model
        assert issubclass(self.foreign_model, Model), "foreign_model isn't a Model"

        # test for appropriate primary key
        assert len(self.foreign_model.Meta.pk_fields) == 1, \
                "compound foreign key is not currently allowed"

        super(ForeignKey, self).__init__(self.foreign_model, **kw)

    def __get__(self, model, owner):
        ":rtype: Model instance"
        if model is None:
            return self

        fk_value = model.__dict__[self._name]
        return self.lookup(fk_value)

    # don't require a __set__ because Model.set_field() calls our cast() method

    @property
    def pk_field(self):
        ":rtype: :func:`IField.field_type`, eg: IntField"
        pks = self.foreign_model.Meta.pk_fields.values()
        return pks[0]

    def lookup(self, pk):
        """
        given a pk, return foreign_model instance
        """
        if pk is None:
            return None

        return self.foreign_model.objects.get(pk)

    def cast(self, value):
        """
        return the primary_key value of the foreign model
        """
        if value is None:
            return None

        if isinstance(value, self.foreign_model):
            return value.pk

        if isinstance(value, self.pk_field.field_type):
            return value

        return self.pk_field.cast(value)

    def dumps(self, value):
        from .model import Model

        if not isinstance(value, Model):
            raise RuntimeError("ForeignKey value is not a Model")

        return self.pk_field.dumps( value.pk )

    # def loads() is not required because the Storage loader is probably
    # reading json strings and then using the Model.__init__() to feed
    # it key-value pairs. ie: we don't know that it's a ForeignKey on disk.

# TODO class OneToOneField

# TODO class ManyToManyField
