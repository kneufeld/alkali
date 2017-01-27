# Changelog

Here's what we all hope is an accurate list of things that have changed
between versions.

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
