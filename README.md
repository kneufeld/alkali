# Alkali

![](https://readthedocs.org/projects/alkali/badge/?version=master)
![](https://travis-ci.org/kneufeld/alkali.svg?branch=master)
![](https://codecov.io/gh/kneufeld/alkali/branch/master/graph/badge.svg)
![](https://coveralls.io/repos/github/kneufeld/alkali/badge.svg?branch=master)

Alkali was featured on [PythonBytes](https://pythonbytes.fm/) episode
[#119](https://pythonbytes.fm/episodes/show/119/assorted-files-as-django-orm-backends-with-alkali)!

Alkali is a database engine, written in Python 3. It's raison d'être is
to provide a Django-like ORM while controlling the on disk format. If
you already have your data in a real database like Postgres then you'll
want SQLAlchemy, if however, your data is in json/yaml/csv/other/etc
files then Alkali might be exactly what you're looking for.

Full documentation at https://alkali.readthedocs.org

For some examples, please go straight to the quickstart guide:
https://alkali.readthedocs.io/en/master/quickstart.html

Here's a teaser to whet your appetite.

```python
import os
from alkali import Database, Model, fields, tznow

class Entry(Model):

   date    = fields.DateTimeField(primary_key = True)
   title   = fields.StringField()
   body    = fields.StringField()
   created = fields.DateTimeField(auto_now_add=True)

db = Database(models=[Entry], save_on_exit=True)

e = Entry(date=tznow(), title="my first entry", body="alkali is pretty good")
e.save()    # adds model instance to Entry.objects

title = Entry.objects.filter(date__le=tznow()).first().title
assert title == "my first entry"

db.store()
assert os.path.getsize('Entry.json')
```

## Installation

If you're reading this then you probably didn't install with `pip
install alkali` and get on with your life. You probably want to be able
edit the code and run tests and whatnot.

In that case run: `pip install -e .[dev]`


## Documentation

If you want to be able to build the docs then also run

```
pip install -e .[docs]
make html
```


## Testing

During development `pytest` was the runner of choice but any unit test
runner should work.

Examples:

* `pytest` run all tests
* `pytest -s` to see stdout (any print statements)
* `pytest --cov` to see test coverage
* `pytest -k test_1` to run all tests named *test_1*
* `pytest -k test_1 alkali/tests/test_fields.py` to run test_1 in test_fields.py
