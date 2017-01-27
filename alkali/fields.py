import datetime as dt
import dateutil.parser
import itertools
import types

from .utils import tzadd, tznow

import logging
logger = logging.getLogger(__name__)


class Field(object):
    """
    base class for all field types. it tries to hold all the functionality
    so derived classes only need to override methods in special circumstances.

    Field objects are instantiated during model creation. ``i = IntField()``

    All Model instances share the same instantiated Field objects in their
    Meta class. ie: ``id(MyModel().Meta.fields['i']) == id(MyModel().Meta.fields['i'])``

    **Note**: the Field does not hold a value, only meta information about a
    value. The Model holds the value and is set via Model.__setattr__
    """

    _counter = itertools.count() # keeps track of declaration order in the Models

    def __init__(self, field_type, **kw):
        """
        :param field_type: the type this field should hold
        :type field_type: str/int/float/etc
        :param kw:
            * primary_key: is this field a primary key of parent model
        """
        self._order = Field._counter.next() # DO NOT TOUCH, deleted in MetaModel

        assert field_type is not None
        self._field_type = field_type

        self._primary_key = kw.pop('primary_key', False)

        # don't allow unhandeled kw args
        assert len(kw) == 0

    def __str__(self):
        return "<{}>".format(self.__class__.__name__)

    @property
    def field_type(self):
        """
        **property**: return ``type`` of this field
        """
        return self._field_type

    @property
    def primary_key(self):
        """
        **property**: return true/false if this field is a primary key
        """
        return self._primary_key

    def cast(self, value):
        if value is None:
            return None

        # simple cast, eg. int(value)
        if not isinstance(value, self._field_type):
            return self._field_type(value)

        return value

    def dumps(self, value):
        """
        by not changing value, it means that json.dumps can properly
        encode type(value)
        """
        return value

    def loads(self, value):
        """
        by not changing value, it means that json.loads can properly
        decode value into correct type
        """
        return value


class IntField(Field):

    def __init__(self, **kw):
        super(IntField, self).__init__(int, **kw)


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

    def cast(self, value):
        return value


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
        #     pass

        self.foreign_model = foreign_model

        # a Model is an instance of MetaModel so type(foreign_model) == MetaModel
        # an instance of a Model is of course a Model. type(Model()) == Model
        assert issubclass(self.foreign_model, Model), "foreign_model isn't a Model"

        # test for appropriate primary key
        assert len(self.foreign_model.Meta.pk_fields) == 1, \
                "compound foreign key is not currently allowed"

        super(ForeignKey, self).__init__(self.foreign_model, **kw)

    @property
    def pk_field(self):
        ":rtype: :func:`IField.field_type`, eg: IntField"
        pks = self.foreign_model.Meta.pk_fields.values()
        return pks[0]

    def cast(self, value):
        if value is None:
            return None

        if isinstance(value, self.foreign_model):
            value = value.pk
        elif isinstance(value, self.pk_field.field_type):
            pass
        else:
            value = self.pk_field.cast(value)

        return value

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
