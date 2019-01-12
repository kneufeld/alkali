import csv

from alkali.peekorator import Peekorator
from .file import FileStorage

import logging
logger = logging.getLogger(__name__)


class CSVStorage(FileStorage):
    """
    load models in csv format

    first line assumed to be column headers (aka: field names)

    use `remap_fieldnames` to change column headers into model field names
    """
    extension = 'csv'

    def read(self, model_class):
        self._fhandle.seek(0)
        reader = csv.DictReader(self._fhandle)

        for row in reader:
            row = self.remap_fieldnames(model_class, row)
            yield model_class(**row)

    def remap_fieldnames(self, model_class, row):
        """
        example of remap_fieldnames that could be defined
        in derived class or as a stand-alone function.

        warning: make sure your header row that contains field
        names has no spaces in it

        ::

            def remap_fieldnames(self, model_class, row):
                fields = model_class.Meta.fields.keys()

                for k in row.keys():
                    results_key = k.lower().replace(' ', '_')

                    if results_key not in fields:
                        if k == 'Some Wierd Name':
                            results_key = 'good_name'
                        else:
                            raise RuntimeError( "unknown field: {}".format(k) )

                    row[results_key] = row.pop(k)

                return row
        """
        return row

    def write(self, model_class, iterator):
        """
        warning: if ``remap_fieldnames`` changes names then saved file
        will have a different header line than original file
        """
        if iterator is None:
            return False

        f = self._fhandle
        f.seek(0)

        _peek = Peekorator(iter(iterator))
        writer = None

        for e in _peek:
            if _peek.is_first():
                fieldnames = e.Meta.fields.keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerow(e.dict)
            else:
                writer.writerow(e.dict)

        f.truncate()
        return True
