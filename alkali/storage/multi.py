import json

from alkali.storage import FileStorage

import logging
logger = logging.getLogger(__name__)

class MultiStorage(FileStorage):
    """
    like a regular JSONStorage but this file can hold multiple
    different tables/models
    """

    def __init__(self, models, filename):
        self.models = models
        super().__init__(filename)

    def _model_name(self, model_class):
        return model_class.__name__.lower()

    def read(self, model_class):
        """
        read the entire file but only emit objects for the given model_class

        not the most effecient but by far the simplest
        """
        self._fhandle.seek(0)

        if os.path.isfile(self.filename) and os.path.getsize(self.filename):
            data = json.load(self._fhandle)
        else:
            data = {} # first time

        if not data:
            return None

        for value in data[self._model_name(model_class)]:
            yield value

    def write(self, model_class, values):
        """
        probably not the best way to do this but we load the file
        and then write it back out with the one updated key/value pair
        """
        self._fhandle.seek(0)

        if os.path.isfile(self.filename) and os.path.getsize(self.filename):
            data = json.load(self._fhandle)
        else:
            data = {} # first time

        data[self._model_name(model_class)] = [
            value.dict for value in model_class.objects._instances.values()
        ]

        # import pprint
        # pprint.pprint(data)

        # TODO needs to do this safetly, do we loose data on an encode error?
        self._fhandle.seek(0)
        json.dump(data, self._fhandle, indent='  ')
        self._fhandle.truncate()
        self._fhandle.flush()
