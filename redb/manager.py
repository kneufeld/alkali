from zope.interface import Interface, Attribute, implements
from collections import OrderedDict
import os

from .model import Model
from .query import IQuery, Query

import logging
logger = logging.getLogger(__name__)

class IManager( Interface ):

    pass

class Manager(object):
    """
    main class for any database. this holds the actual data of the database.
    """
    implements(IManager)

    def __init__( self, model_class, *args, **kw ):
        self._model_class = model_class
        self._instances = {}
        self._modified = False

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
    def pks(self):
        "return all primary keys"
        return self._instances.keys()

    @property
    def instances(self):
        return self._instances

    @property
    def modified(self):
        if self._modified:
            return True

        return any( map( lambda e: e.modified, self.instances.values() ) )

    def save(self, instance, modify=True):
        #logger.debug( "saving model instance: %s", str(instance.pk) )

        assert instance.pk is not None
        self._instances[ instance.pk ] = instance

        if modify:
            self._modified = True

    def clear(self):
        logger.debug( "%s: clearing all models", self.name )

        self._modified = len(self._instances) > 0
        self._instances = {}

    def delete(self, instance):
        logger.debug( "deleting model instance: %s", str(instance.pk) )

        try:
            del self._instances[ instance.pk ]
            self._modified = True
        except KeyError:
            pass

    def store(self, storage, force=False):
        "save all our instances to storage"

        def dict_sorter( elements, **kw ):
            "yield elements in key order"
            keys = sorted( elements.keys(), **kw )
            for key in keys:
                yield elements[key]

        if force:
            self._modified = True

        if self.modified:
            logger.debug( "%s: has dirty records, saving", self.name )
            logger.debug( "%s: storing models via storage class: %s", self.name, storage.name )

            storage.write( dict_sorter(self._instances) )
        else:
            logger.debug( "%s: has no dirty records, not saving", self.name )

        self._modified = False


    def load(self, storage):
        "load all our instances from storage"

        self.clear()

        logger.debug( "%s: loading models via storage class: %s", self.name, storage.name )

        for elem in storage.read( self._model_class ):
            if isinstance(elem, dict):
                elem = self._model_class( **elem )

            if elem.pk in self._instances:
                raise RuntimeError('pk collision detected during load: %s' % elem.pk)

            # this adds elem to our internal list
            self.save(elem, modify=False)

        logger.debug( "%s: finished loading", self.name )


    def get(self, *args, **kw):
        """
        return an instance of a model
        """
        if len(args):
            kw['pk'] = args[0]

        results = Query(self).filter(**kw).instances

        if len(results) == 0:
            raise KeyError("got no results")

        if len(results) > 1:
            raise KeyError("got more than 1 result")

        return results[0]

    def filter(self, **kw):
        """
        return a Query, aka a subset of model instances
        """
        return Query(self).filter(**kw)

    def all(self):
        """
        return a full Query, aka list of ll model instances
        """
        return Query(self)
