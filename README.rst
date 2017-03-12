.. image:: https://readthedocs.org/projects/alkali/badge/?version=master
.. image:: https://travis-ci.org/kneufeld/alkali.svg?branch=master
.. image:: https://codecov.io/gh/kneufeld/alkali/branch/master/graph/badge.svg
.. image:: https://coveralls.io/repos/github/kneufeld/alkali/badge.svg?branch=master

README
======

Documentation at https://alkali.readthedocs.org

For some examples, please go straight to the quickstart guide:
https://alkali.readthedocs.io/en/master/quickstart.html

Installation
------------

If you're reading this then you probably didn't install with ``pip install alkali``
and get on with your life. You probably want to be able edit the code and run
tests and whatnot.

In that case run: ``pip install -e .[dev]``

If you want to be able to build the docs then also run ``pip install -e .[docs]``

Documentation
-------------

To build the docs run: ``sphinx-build -b html docs/ build/``

Testing
-------

During development ``pytest`` was the runner of choice but any unit test runner
should work.

Examples:

* ``pytest`` run all tests
* ``pytest -s`` to see stdout (any print statements)
* ``pytest --cov`` to see test coverage
* ``pytest -k test_1`` to run all tests named *test_1*
* ``pytest -k test_1 alkali/tests/test_fields.py`` to run test_1 in test_fields.py
