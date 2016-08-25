from zope.interface import Interface, Attribute, implements
import datetime as dt
from collections import OrderedDict
import types
import inspect
import os

from .storage import JSONStorage
from .model import Model
from .fields import Field

import logging
logger = logging.getLogger(__name__)

class IDatabase( Interface ):

    models   = Attribute("the dict of models")

class Database(object):
    """
    This is the glue object that owns and coordinates all the different
    classes and objects.
    """
    implements(IDatabase)

    def __init__( self, models=[], *args, **kw ):

        logger.debug( "Database: creating database" )

        self._models = OrderedDict()
        for model in models:
            logger.debug( "Database: adding model to database: %s", model.name )
            self._models[model.name.lower()] = model

        self._storage_type = kw.pop('storage', JSONStorage)
        self._root_dir = kw.pop('root_dir', '.')
        self._save_on_exit = kw.pop('save_on_exit', False)

    def __del__(self):
        if self._save_on_exit:
            self.store()

    @property
    def models(self):
        return self._models.values()

    def get_model(self, model_name):
        try:
            return self._models[model_name.lower()]
        except KeyError:
            pass

        return None

    def get_filename(self, model, storage=None):
        """
        allow models to specify their own filename or use
        storage extension default
        """
        if isinstance(model, types.StringTypes):
            model = self.get_model(model)

        filename = model.Meta.filename

        if not filename:
            storage = storage or self.get_storage(model)
            filename = "{}.{}".format(model.name, storage.extension)

        return os.path.join( self._root_dir, filename )

    def get_storage(self, model, default=None, filename=None):
        """
        allow models to specify their own storage or use
        database default
        """
        if isinstance(model, types.StringTypes):
            model = self.get_model(model)

        storage = model.Meta.storage or default or self._storage_type

        if inspect.isclass(storage):
            filename = filename or self.get_filename(model, storage)
            storage = storage(filename)

        return storage

    def store(self, filename=None, storage=None, force=False):
        """
        save the data for each model
        """
        logger.debug( "Database: storing models" )

        # make sure storage is an instantiated class
        assert storage is None or not inspect.isclass(storage)

        for model in self.models:
            logger.debug( "Database: storing model: %s", model.name )

            storage = storage or self.get_storage(model, filename=filename)
            model.objects.store(storage, force=force)

    def load(self, filename=None, storage=None):
        """
        load the data for each model
        """
        logger.debug( "Database: loading models" )

        # make sure storage is an instantiated class
        assert storage is None or not inspect.isclass(storage)

        for model in self.models:
            logger.debug( "Database: loading model: %s", model.name )

            storage = storage or self.get_storage(model, filename=filename)
            model.objects.load(storage)
