# Changelog

Here's what we all hope is an accurate list of things that have changed
between versions.

## v0.7.3

* renamed AUTHORS.md to CONTRIBUTORS.md
* added missing folk to CONTRIBUTORS.md
* including `alkali.storage` submodule when building sdist

## v0.7.2

* updated docs, lots more work to do here
* pseudo_import in setup.py is more robust
* add an rss example
* fixed warnings, some types are in collections.abc
* fixed timezone bug during serializing of DateTimeField
* test Storage.NotImplemented
* import Storage objects into alkali for nicer importing
* database can now handle using a storage instance...
* removed more python 2 remnants (object from class definition)
* using python3 version of super()
* Storage.write() now takes model_class param
* adding new UUIDField
* moved Storage classes into submodule
* added new MultiStorage type, save mutliple models in one file
* added auto_now, auto_now_add to DateTimeField
* some minor refactorings

## v0.7.1

* updated requirements.txt
* made fake `fcntl` for windows users

## v0.7.0

* **Python 3 only**, this is a big breaking change
* cleaned up some tests
* refactored some code
* no actual functionality changes

## v0.6.0

* add group_by ability to Query
* added One2OneField type
* added .count property to RelManager
* added .first() function to Query
* allow model instance creation with pk keyword
* database now works with Storage instances, not classes
* added custom exceptions: DoesNotExist, EmptyPrimaryKey, MultipleObjectsReturned
* storage files now protected by a lock
* fix some pep8 whitespace issues
* fixed bug in valid_pk() regarding compound primary keys

## v0.5.5

* adding BoolField
* adding CSVStorage, load/save csv files
* queries are bit more effecient/fast, don't copy as many objects by default
* some doc cleanups

## v0.5.4

* updated docs and comments
* test coverage back up to 100%
* Query copies manager objects at creation time, less effiecient but
  less error prone
* implemented Query.distinct
* implemented Query.annotate

## v0.5.3

* implemented Query.aggregate functions: Sum, Count, Min, Max
* can access Field object via shortcut model.fieldname_field
* Fields are now descriptors on Model instance
* models now cascade delete when ForeignKey instance is deleted
* some minor speed ups

## v0.5.2

* no longer using IField as a zope interface, just have a Field class now
* IntField now has auto_increment property
* general work on ForeignKey fields, still not happy with implementation
* ForeignKey validation during save/load
* Fields now have more properties, links to model and meta class parents
* refactoring around how Model instances are created
* Query returns copies of Model instances
* Query speeds and Manager.get() are now faster
* general refactorings

## v0.5.1

* fix: model instances going to/from its manager are copied. this
  prevents changing the saved version without calling save().
* added ForeignKey field
* memoizing Model.pk property
* don't allow changing of pk field once set
* added signals on model creation/deleting/saving/etc
* removed `.name` property from several classes
* minor speedups after profiling
* fix: during load/save a multiple table db would reuse the same storage class
* several documentation cleanups

## v0.5.0

Initial commit. Starting at v0.5 since alkali can accomplish some real work.
