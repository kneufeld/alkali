from zope.interface import Interface, Attribute, implements
import datetime as dt

from . import tzadd

class IField( Interface ):

    field_type = Attribute("the type of the field, str, int, list, etc")
    value      = Attribute("the value of the field as self.type")


class Field(object):
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
