from zope.interface import Interface, Attribute, implements
import copy
import os

from .model import Model

class IManager( Interface ):

    pass
    # modified   = Attribute("are any fields dirty")
    # fields     = Attribute("the dict of fields")

class Manager(object):
    """
    main class for any database. this holds the actual data of the database.
    """
    implements(IManager)

    def __init__( self, model_class, *args, **kw ):
        self._model_class = model_class
        self._instances = {}

    def __str__(self):
        try:
            basename = ' ' + os.path.basename( self.filename )
        except AttributeError:
            basename = ''
        return "<{name}{fname}>".format(name=self.name, fname=basename)

    def __len__(self):
        return len(self._instances)

    @property
    def name(self):
        return "{}Manager".format(self._model_class.__name__)

    def get(self, pk):
        return self._instances[pk]

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
        storage.write( [m.dict for pk,m in self._instances.items()] )

    def load(self, storage):
        "load all our instances from storage"
        data = storage.read() # data is a list of dicts

        for elem in data:
            m = self._model_class( **elem )
            self.save(m)
