# -*- coding: utf-8 -*-

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

    models   = Attribute("the ``dict`` of models")

class Database(object):
    """
    This is the parent object that owns and coordinates all the different
    classes and objects defined in this module.

    :ivar _storage_type:
        default storage type for all models, defaults to :class:`alkali.storage.JSONStorage`

    :ivar _root_dir:
        directory where all models are stored, defaults to current working directory

    :ivar _save_on_exit:
        automatically save all models before Database object is destroyed. call
        :func:`Database.store` explicitly if ``_save_on_exit`` is false.
    """
    implements(IDatabase)

    def __init__( self, models=[], **kw ):
        """
        :param models: a list of :class:`alkali.model.Model` classes
        :param kw:
            * storage: default storage class for all models
            * root_dir: default save path directory
            * save_on_exit: save all models to disk on exit
        """

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
        """
        **property**: return ``list`` of models in the database
        """
        return self._models.values()

    def get_model(self, model_name):
        """
        :param model_name: the name of the model, **note**: all model names are
            converted to lowercase
        :rtype: :class:`alkali.model.Model`
        """
        try:
            return self._models[model_name.lower()]
        except KeyError:
            pass

        return None

    def get_filename(self, model, storage=None):
        """
        get the filename for the specified model. allow models to
        specify their own filename or generate one based on storage
        class. prepend Database._root_dir.

        eg. <_root_dir>/<model name>.<storage.extension>

        :param model: the model name or model class
        :param storage: the storage class, uses the database default if None
        :return: returns a filename path
        :rtype: str
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
        get the storage class for the specified model. allow models to
        specify their own storage or use database default.

        :param model: the model name or model class
        :param default: override database default storage class
        :param filename: override database default filename
        """
        # FIXME this should return a class not instance

        if isinstance(model, types.StringTypes):
            model = self.get_model(model)

        storage = model.Meta.storage or default or self._storage_type

        if inspect.isclass(storage):
            filename = filename or self.get_filename(model, storage)
            storage = storage(filename)

        return storage

    def store(self, filename=None, storage=None, force=False):
        """
        write all model data to disk

        :param filename: override model filename
        :param storage: override model storage class
        :param force: force store even if :class:`alkali.manager.Manager`
            thinks data is clean
        """
        # FIXME can't specify filename if more than one model in database

        logger.debug( "Database: storing models" )

        # make sure storage is an instantiated class
        assert storage is None or not inspect.isclass(storage)

        for model in self.models:
            logger.debug( "Database: storing model: %s", model.name )

            storage = storage or self.get_storage(model, filename=filename)
            model.objects.store(storage, force=force)

    def load(self, filename=None, storage=None):
        """
        load all model data from disk

        :param filename: override model filename
        :param storage: override model storage class
        """
        # FIXME can't specify filename if more than one model in database
        logger.debug( "Database: loading models" )

        # make sure storage is an instantiated class
        assert storage is None or not inspect.isclass(storage)

        for model in self.models:
            logger.debug( "Database: loading model: %s", model.name )

            storage = storage or self.get_storage(model, filename=filename)
            model.objects.load(storage)
