.. alkali documentation master file, created by
   sphinx-quickstart on Thu Sep  1 14:44:43 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. _README:

alkali |version|
****************

Alkali, or AlkaliDB, is a database engine. Code can be found on github_.

If you know anything about databases then you know that any real database
is *ACID* (Atomic, Consistent, Isolation, Durable). If you know anything
about chemistry then you know that an alkaline substance is the opposite
of an acidic one.

I think you can see where this is going.

So alkali is basically the opposite of an *ACID* database. Except
*Durable*. If alkali is not durable then we want to hear about it as
soon as possible.

So knowing this, why would you use alkali?

* If you need a simple, stand alone, database-like library
* If you need a document store
* Minimal disk io
* *"Advanced"* features like foreign keys
* You'd like a database but must control the on-disk format
* If a *list* of *dict* is a main data structure in your program
* You often search/filter your data
* You like Django and/or SqlAlchemy but don't need anything that heavy
* 100% test coverage

Plus alkali is really easy to use, if you've ever used the Django ORM or
SQlAlchemy then alkali's API will feel very familiar. Alkali's API was
based off of Django's.

.. _github: https://github.com/kneufeld/alkali

.. toctree::
   :maxdepth: 1

   history
   quickstart
   alkali

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
