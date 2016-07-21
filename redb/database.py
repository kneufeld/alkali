from zope.interface import Interface, Attribute, implements
import datetime as dt
from collections import OrderedDict
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

        logger.debug( "creating database" )

        self._models = OrderedDict()
        for model in models:
            logger.debug( "adding model to database: %s", model.name )
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

    def get_filename(self, model):
        """
        allow models to specify their own filename or use
        storage extension default
        """
        ext = self.get_storage(model).extension
        filename = model.Meta.filename or "{}.{}".format(model.name,ext)
        return os.path.join( self._root_dir, filename )

    def get_storage(self, model):
        """
        allow models to specify their own storage or use
        database default
        """
        return model.Meta.storage or self._storage_type

    def store(self, filename=None, force=False):
        """
        save the data for each model
        """
        logger.debug( "storing models" )

        for model in self.models:
            logger.debug( "storing model: %s", model.name )

            filename = filename or self.get_filename(model)
            storage = self.get_storage(model)(filename)
            model.objects.store(storage, force=force)

    def load(self):
        """
        load the data for each model
        """
        logger.debug( "loading models" )

        for model in self.models:
            logger.debug( "loading model: %s", model.name )

            filename = self.get_filename(model)
            storage = self.get_storage(model)(filename)
            model.objects.load(storage)
