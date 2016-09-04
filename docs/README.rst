.. alkali documentation master file, created by
   sphinx-quickstart on Thu Sep  1 14:44:43 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

alkali |version|
================

Alkali, or AlkaliDB, is a database engine.

If you know anything about databases then you know that any real
database is *ACID* (Atomic, Consistent, Isolation, Durable). If you know
anything about chemistry then you know that an alkaline substance is the
opposite of an acidic one.

I think you can see where this is going.

So alkali is basically the opposite of an *ACID* database. Except
*Durable*. If alkali is not durable then we want to hear about it as
soon as possible.

So knowing this, why would you use alkali? If you need a simple
database-like library and especially if you want to control the on-disk
format of your database then alkali just might be for you. If a *list* of
*dict* is a main data structure in your program then make programming
fun again with alkali.

Plus alkali is really easy to use, if you've ever used the Django ORM or
SQlAlchemy then alkali's API will feel very familiar. Alkali's API was
based off of Django.

Contents:

.. toctree::
   :maxdepth: 1

   alkali

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
