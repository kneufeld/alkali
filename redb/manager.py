from zope.interface import Interface, Attribute, implements
from collections import OrderedDict
import os

from .model import Model
from .query import IQuery, Query

class IManager( Interface ):

    pass

class Manager(object):
    """
    main class for any database. this holds the actual data of the database.
    """
    implements(IManager)

    def __init__( self, model_class, *args, **kw ):
        self._model_class = model_class
        self.clear()

    def __repr__(self):
        return "<{}>".format(self.name)

    def __len__(self):
        return len(self._instances)

    @property
    def count(self):
        return len(self)

    @property
    def name(self):
        return "{}Manager".format(self._model_class.__name__)

    @property
    def instances(self):
        return self._instances

    def save(self, instance):
        assert instance.pk is not None
        self._instances[ instance.pk ] = instance

    def clear(self):
        self._instances = {}

    def delete(self, instance):
        try:
            del self._instances[ instance.pk ]
        except KeyError:
            pass

    def store(self, storage):
        "save all our instances to storage"

        def dict_sorter( elements, **kw ):
            "yield elements in key order"
            keys = sorted( elements.keys(), **kw )
            for key in keys:
                yield elements[key]

        storage.write( dict_sorter(self._instances) )

    def load(self, storage):
        "load all our instances from storage"

        self.clear()

        for elem in storage.read( self._model_class ):
            if elem.pk in self._instances:
                raise RuntimeError('pk collision detected during load: %s' % elem.pk)

            self.save(elem)

        #print "loaded:",len(self._instances)

    def get(self, *args, **kw):
        if len(args):
            kw['pk'] = args[0]

        results = Query(self).filter(**kw).instances

        if len(results) > 1:
            raise KeyError("got more than 1 result")

        if not results:
            raise KeyError("got no results")

        return results[0]

    def filter(self, **kw):
        return Query(self).filter(**kw)
