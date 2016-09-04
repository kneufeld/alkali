from zope.interface import Interface, Attribute, implementer
import copy
import types
import operator
import collections
import re

import logging
logger = logging.getLogger(__name__)

class IQuery( Interface ):

    def filter(**kw):
        "return a query object with multiple objects"

@implementer(IQuery)
class Query(object):
    """
    this class performs queries on manager instances
    returns lists of model instances
    """

    def __init__( self, manager):
        self.manager = manager

        # shallow copy, new list but same objects
        self._instances = copy.copy( manager.instances )

    def __len__(self):
        return len(self._instances)

    def __iter__(self):
        return iter(self._instances)

    def __getitem__(self, i):
        return self._instances[i]

    @property
    def name(self):
        return "{}Query".format(self.model_class.name)

    @property
    def count(self):
        return len(self)

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
        """
        based on **kw, return a subset of instances
        """

        #logger.debug( "%s: query: %s", self.name, str(kw) )

        for field, query in kw.items():
            try:
                field, oper = field.split('__')
                oper = oper or 'eq'
            except ValueError:
                field = field
                oper = 'eq'

            self._instances = self._filter( field, oper, query, self._instances )

        return self

    def _filter(self, field, oper, value, instances):
        """
        helper function that does the actual work of filtering out instances
        """

        def in_(coll, val):
            if not isinstance(coll, types.StringTypes) \
            and isinstance(coll, collections.Iterable):
                return bool( set(coll) & set(val) ) # intersection
            else:
                return coll in val

        def rin_(coll, val):
            if not isinstance(val, types.StringTypes) \
            and isinstance(val, collections.Iterable):
                return bool( set(coll) & set(val) ) # intersection
            else:
                return val in coll

        def regex(coll, val):
            return re.search(val, coll, re.UNICODE)

        def regexi(coll, val):
            return re.search(val, coll, re.UNICODE | re.IGNORECASE)

        if oper == 'in':
            assert isinstance(value, collections.Iterable)
            oper = in_
        elif oper == 'rin':
            assert isinstance(field, collections.Iterable)
            oper = rin_
        elif oper == 're':
            oper = regex
        elif oper == 'rei':
            oper = regexi
        else:
            oper = getattr(operator,oper)

        return filter( lambda e: oper(getattr(e,field), value), instances)

    def order_by(self, *args):
        """
        change order of self.instances, args should be field names
        with optional '-' to indicate reverse order

        warning: because this isn't a real database and we don't have
        grouping, passing in multiple fields will very possibly sort
        on the last field only. python sorting is stable however, so a
        multiple field sort may work as intended.
        """
        def _order_by( field ):
            "return reversed, field_name"
            if field.startswith('-'):
                return True, field[1:]
            else:
                return False, field

        for field in args:
            reverse, field = _order_by( field )
            key = operator.attrgetter(field)
            self._instances = sorted( self._instances, key=key, reverse=reverse)

        return self

    def limit(self, n):
        """
        return first(+) or last(-) n elements

        this has to be the last call during a query since it returns a
        list of instances and not a Query
        """
        if n > 0:
            return self._instances[:n]
        elif n < 0:
            return self._instances[n:]
        else: # n == 0, return all instead of [] because why not?
            return self._instances
