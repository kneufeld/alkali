from zope.interface import Interface, Attribute, implements
import copy
import operator

class IQuery( Interface ):

    def filter(**kw):
        "return a query object with multiple objects"

class Query(object):
    """
    main class for any database. this holds the actual data of the database.
    """
    implements(IQuery)

    def __init__( self, manager):
        self.manager = manager

        # shallow copy, new dict but same objects
        self._instances = copy.copy( manager.instances.values() )

    def __len__(self):
        return len(self._instances)

    @property
    def instances(self):
        return self._instances

    @property
    def fields(self):
        "helper to get dict of model fields"
        return self.model_class.Meta.fields

    @property
    def model_class(self):
        return self.manager._model_class

    @property
    def field_names(self):
        return self.fields.keys()

    def filter(self, **kw):
        def pk_fields(model_class):
            return [name for name,field in model_class.Meta.fields.items() if field.primary_key]

        if 'pk' in kw:
            query = kw.pop('pk')
            pk_field_name = pk_fields(self.model_class)[0]
            kw[pk_field_name] = query

        for field, query in kw.items():
            try:
                field, oper = field.split('__')
                oper = oper or 'eq'
            except ValueError:
                field = field
                oper = 'eq'

            self._instances = self._filter( field, oper, query, self._instances )

        return self

    def _filter(self, name, oper, value, instances):
        def func( oper, a, b ):
            return oper(a,b)

        oper = getattr(operator,oper)
        return filter( lambda e: func(oper, getattr(e,name), value), instances)
