import json

from alkali.peekorator import Peekorator
from .file import FileStorage

class JSONStorage(FileStorage):
    """
    save models in json format
    """
    extension = 'json'

    def read(self, model_class):
        data = super().read(model_class)

        if not data:
            return

        for elem in json.loads(data):
            yield elem

    def write(self, model_class, iterator):

        if iterator is None:
            return False

        f = self._fhandle
        f.seek(0)

        f.write('[\n')

        _peek = Peekorator(iter(iterator))
        for e in _peek:
            data = json.dumps(e.dict, indent='  ')
            f.write(data)

            if not _peek.is_last():
                f.write(',\n')

        f.write('\n]')

        # since the file may shrink (we've deleted records) then
        # we must truncate the file at our current position to avoid
        # stale data being present on the next load
        f.truncate()
        f.flush()

        return True
