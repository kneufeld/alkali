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

from .storage import JSONStorage

import logging
logger = logging.getLogger(__name__)


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
            assert inspect.isclass(model)
            logger.debug( "Database: adding model to database: %s", model.__name__ )
            self._models[model.__name__.lower()] = model

        self._storage_type = kw.pop('storage', JSONStorage)
        self._save_on_exit = kw.pop('save_on_exit', False)

        self._root_dir = kw.pop('root_dir', '.')
        self._root_dir = os.path.expanduser(self._root_dir)
        self._root_dir = os.path.abspath(self._root_dir)


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


    def get_filename(self, model):
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
            storage = self.get_storage(model)
            filename = "{}.{}".format(model.__name__, storage.extension)

        # if filename is absolute, then self._root_dir is gets filtered out
        return os.path.join( self._root_dir, filename )


    def get_storage(self, model):
        """
        get the storage class for the specified model

        precedence is:

        #. model defined storage class
        #. storage class defined in call
        #. storage class default of database

        :param model: the model name or model class
        :param storage: override database default storage class
        :rtype: :class:`alkali.storage.Storage` (not an instance)
        """
        if isinstance(model, types.StringTypes):
            model = self.get_model(model)

        storage = model.Meta.storage or self._storage_type
        return storage


    def store(self, _storage=None, force=False):
        """
        persistantly store all model data

        :param IStorage storage: override model storage class
        :param bool force: force store even if :class:`alkali.manager.Manager`
            thinks data is clean
        """
        logger.debug( "Database: storing models" )

        # you can't save more than one model with a single storage
        # instance because the file will get over written
        assert _storage is None or inspect.isclass(_storage)

        for model in self.models:
            storage = _storage or self.get_storage(model)

            if inspect.isclass(storage):
                filename = self.get_filename(model)
                storage = storage(filename)

            model.objects.store(storage, force=force)


    def load(self, _storage=None):
        """
        load all model data from disk

        :param storage: override model storage class
        """
        logger.debug( "Database: loading models" )

        # you can't load more than one model with a single storage
        # instance since only one file will get read
        assert _storage is None or inspect.isclass(_storage)

        for model in self.models:
            logger.debug( "Database: loading model: %s", model.__name__ )

            storage = _storage or self.get_storage(model)
            logger.debug( "Database: using storage: %s", storage.__name__ )

            if inspect.isclass(storage):
                filename = self.get_filename(model)
                storage = storage(filename)

            model.objects.load(storage)
