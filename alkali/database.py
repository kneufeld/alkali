# -*- coding: utf-8 -*-

"""
::

    from alkali import Database, JSONStorage, Model, fields

    class MyModel( Model ):
        id = fields.IntField(primary_key=True)
        title = fields.StringField()

    db = Database(models=[MyModel], storage=JSONStorage, root_dir='/tmp', save_on_exit=True)

    m = MyModel(id=1,title='old title')
    m.save()                      # adds model instance to MyModel.objects
    db.store()                    # creates /tmp/MyModel.json

    db.load()                     # read /tmp/MyModel.json
    m = MyModel.objects.get(pk=1) # do a search on primary key
    m.title = "my new title"      # change the title
    # don't need to call m.save() since the database "knows" about m
    # db.store() is automatically called as db goes out of scope, save_on_exit==True
"""

from collections import OrderedDict
import types
import inspect
import os

from .storage import Storage, JSONStorage

import logging
logger = logging.getLogger(__name__)


class Database:
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

    def __init__( self, models=[], **kw ):
        """
        :param models: a list of :class:`alkali.model.Model` classes
        :param kw:
            * root_dir: default save path directory
            * save_on_exit: save all models to disk on exit
            * storage: default storage class for all models
        """

        logger.debug( "Database: creating database" )

        self._models  = OrderedDict()
        self._storage = OrderedDict()

        self._storage_type = kw.pop('storage', JSONStorage)
        self._save_on_exit = kw.pop('save_on_exit', False)

        self._root_dir = kw.pop('root_dir', '.')
        self._root_dir = os.path.expanduser(self._root_dir)
        self._root_dir = os.path.abspath(self._root_dir)

        assert len(kw) == 0, "unknown kwargs: {}".format(kw.keys())

        for model in models:
            assert inspect.isclass(model)
            logger.debug( "Database: adding model to database: %s", model.__name__ )
            self._models[model.__name__.lower()] = model
            self.set_storage(model)

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
        if isinstance(model, str):
            model = self.get_model(model)

        storage = storage or model.Meta.storage or self._storage_type

        if isinstance(storage, Storage): # not a class
            assert storage.filename, "storage instances must have filenames"
            return storage.filename

        filename = model.Meta.filename

        if not filename:
            filename = "{}.{}".format(model.__name__, storage.extension)

        # if filename is absolute, then self._root_dir gets filtered out
        return os.path.join( self._root_dir, filename )

    def set_storage(self, model, storage=None):
        """
        set the storage instance for the specified model

        precedence is:

        #. passed in storage class
        #. model defined storage class
        #. default storage class of database (JSONStorage)

        :param model: the model name or model class
        :param IStorage storage: override model storage class
        :rtype: :class:`alkali.storage.Storage` instance or None
        """
        if isinstance(model, str):
            model = self.get_model(model)

        storage = storage or model.Meta.storage or self._storage_type

        if isinstance(storage, Storage): # not a class
            self.get_filename(model, storage) # for 100% coverage
            self._storage[model] = storage
        else:
            assert inspect.isclass(storage)
            filename = self.get_filename(model, storage)
            self._storage[model] = storage(filename)

        return self._storage[model]

    def get_storage(self, model):
        """
        get the storage instance for the specified model

        :param model: the model name or model class
        :rtype: :class:`alkali.storage.Storage` instance or None
        """
        if isinstance(model, str):
            model = self.get_model(model)

        try:
            return self._storage[model]
        except KeyError:
            logger.error("no storage defined for model: %s", model.__name__)
            pass

        return None

    def store(self, force=False):
        """
        persistantly store all model data

        :param bool force: force store even if :class:`alkali.manager.Manager`
            thinks data is clean
        """
        for model in self.models:
            logger.debug( "Database: storing model: %s", model.__name__ )

            storage = self.get_storage(model)
            model.objects.store(storage, force=force)

        return True

    def load(self):
        """
        load all model data from disk

        :param IStorage storage: override model storage class
        """
        logger.debug( "Database: loading models" )

        for model in self.models:
            logger.debug( "Database: loading model: %s", model.__name__ )

            storage = self.get_storage(model)
            model.objects.load(storage)
