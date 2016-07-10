from zope.interface import Interface, Attribute, implements
import datetime as dt
from collections import OrderedDict
import os

from .storage import JSONStorage
from .model import Model
from .fields import Field

class IDatabase( Interface ):

    models   = Attribute("the dict of models")

class Database(object):
    """
    This is the glue object that owns and coordinates all the different
    classes and objects.
    """
    implements(IDatabase)

    def __init__( self, models=[], *args, **kw ):

        self._models = OrderedDict()
        for model in models:
            self._models[model.name] = model

        self._storage_type = kw.pop('storage', JSONStorage)
        self._root_dir = kw.pop('root_dir', '.')

    @property
    def models(self):
        return self._models.values()

    def get_model(self, model_name):
        return self._models[model_name]

    def get_filename(self, model):
        """
        allow models to specify their own filename or use
        storage extension default
        """
        ext = self._storage_type.extension
        filename = model.Meta.filename or "{}.{}".format(model.name,ext)
        return os.path.join( self._root_dir, filename )

    def get_storage(self, model):
        """
        allow models to specify their own storage or use
        database default
        """
        return model.storage or self._storage_type

    def load(self):
        """
        load the data for each model
        """
        records = OrderedDict()

        for model in self.models:
            storage = self.get_storage(model)
            for record in storage.read():
                instance = model.__class__(**record)
                records[ instance.pk ] = instance
