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
        data = json.load(self._fhandle)

        if not data:
            return None

        for value in data[self._model_name(model_class)]:
            yield value

    def write(self, model_class, values):
        """
        this saves all models (warning!) but only when called
        with the "first_model" (warning!) as determined alphabetically
        """
        first_model = sorted([self._model_name(model) for model in self.models])[0]

        if self._model_name(model_class) != first_model:
            logger.debug("since we always save all models, only write once")
            return

        data = {
            self._model_name(model):
            [value.dict for value in model.objects._instances.values()]

            for model in self.models
        }

        # import pprint
        # pprint.pprint(data)

        json.dump(data, self._fhandle, indent='  ')
        self._fhandle.truncate()
        self._fhandle.flush()
