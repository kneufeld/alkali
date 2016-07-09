from zope.interface import Interface, Attribute, implements
import datetime as dt
import dateutil.parser

from . import tzadd

class IField( Interface ):

    field_type = Attribute("the type of the field, str, int, list, etc")
    value      = Attribute("a json serializable version of current value")

    def dumps(value):
        "method to serialize the value"

    def loads(value):
        "method to load the value"

class Field(object):
    """
    base class for all field types. it tries to hold all the functionality
    so derived classes only need to override methods in special circumstances.
    """
    implements(IField)

    def __init__(self, field_type, value=None, *args, **kw):
        assert field_type is not None
        self.field_type = field_type

        if value is not None:
            self.value = value
        else:
            self._value = None

        self._primary_key = kw.pop('primary_key', False)

        # if we're a primary key then we must have a value
        # unfortunately we can't enforce this otherwise we could not
        # make an empty object
        #
        # assert not self.primary_key or self.value is not None

        self._modified = False

    def __str__(self):
        return "<{}{} {}>".format(
                self.__class__.__name__,
                '*' if self.modified else '',
                str(self.value) )

    @property
    def modified(self):
        return self._modified

    @property
    def field_type(self):
        return self._field_type

    @field_type.setter
    def field_type(self, field_type):
        self._field_type = field_type

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        """
        allow non field_type to come in, but cast to desired type
        """
        value = self.field_type(value)
        self._value = value
        self._modified = True

    @property
    def primary_key(self):
        return self._primary_key

    @classmethod
    def dumps(cls, value):
        return value

    @classmethod
    def loads(cls, value):
        return value

class IntField(Field):

    def __init__(self, value=None, *args, **kw):
        super(IntField, self).__init__(int, value, *args, **kw)


class StringField(Field):

    def __init__(self, value=None, *args, **kw):
        super(StringField, self).__init__(str, value, *args, **kw)


class DateField(Field):

    def __init__(self, value=None, *args, **kw):
        super(DateField, self).__init__(dt.datetime, value, *args, **kw)

    @Field.value.setter
    def value(self, value):
        """
        make sure date always has a time zone
        """
        if type(value) is not self.field_type:
            value = self.field_type(value)
        value = tzadd( value )
        self._value = value

        self._modified = True

    @classmethod
    def dumps(cls, value):
        if value is None:
            return 'null'
        return value.isoformat()

    @classmethod
    def loads(cls, date):
        if date is None or date == 'null':
            return None

        # assume date is in isoformat, this preserves timezone info
        if type(date) in [unicode,str]:
            date = dateutil.parser.parse(date)

        if date.tzinfo is None:
            date = tzadd( date )

        return date
