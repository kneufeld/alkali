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

        try:
            data = json.load(self._fhandle)
        except json.decoder.JSONDecodeError:
            data = {} # first time
        except Exception as e: # pragma: nocover
            logger.exception(e)
            data = {}

        if not data:
            return None

        try:
            for value in data[self._model_name(model_class)]:
                yield value
        except KeyError: # pragma: nocover
            logger.warning("model '%s' not in datafile: %s",
                           self._model_name(model_class),
                           self.filename
                           )

    def write(self, model_class, iterator):
        """
        probably not the best way to do this but we load the file
        and then write it back out with the one updated key/value pair
        """
        if iterator is None:
            return False

        self._fhandle.seek(0)

        try:
            data = json.load(self._fhandle)
        except json.decoder.JSONDecodeError:
            data = {} # first time
        except Exception as e: # pragma: nocover
            logger.exception(e)
            data = {}

        data[self._model_name(model_class)] = [
            value.dict for value in iterator
        ]

        # import pprint
        # pprint.pprint(data)

        # TODO needs to do this safely, do we loose data on an encode error?
        self._fhandle.seek(0)
        json.dump(data, self._fhandle, indent='  ')
        self._fhandle.truncate()
        self._fhandle.flush()

        return True
