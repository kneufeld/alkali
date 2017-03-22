.. _history:

History
=======

When learning new software I find it helpful to know where it's coming
from. Although most software is the worst software ever written, maybe,
just maybe, it's not so bad if you know how it got to where it is.

Jrnl
----

There's a great app called jrnl_, it's a journal writing wrapper around
your editor. One of jrnl's killer features is that it writes out plain
text files, that means you can edit your journal file with your editor
of choice and use all those great Unix command line tools on it.

Jrnl is so great I use it at work and at home. However, it's really
annoying having two journals, it seems like the good info was always in
the other one. We have a pretty draconian firewall at work so that means
no Dropbox and no ssh. Thankfully, *POST*\s still work.

Long story short, I wanted jrnl to be able to sync its entries with
a website. So I started hacking away and before you know it I was
completely rewriting jrnl. But jrnl's main data structure was a list
of Entry objects. This worked, but was a bit cumbersome. It was very
cumbersome when trying to sync with a remote server.

So I decided that jrnl really needed to be a wrapper around a
*database*. So I started looking at some different Python databases and
a few looked promising, but after playing with them I found them all to
be lacking in some fashion or another.

And that's how alkali_ was born.

PS. my version of jrnl will hopefully be released not too long after alkali.

.. _jrnl: https://github.com/maebert/jrnl
.. _alkali: https://github.com/kneufeld/alkali

Django
------

I've used Django_ in the past and found its ORM (Object Relational
Mapper) to be easy and intuitive. So I decided that I'd write a light
weight database using the same syntax as Django.

This worked surprisingly well. If you're ever in doubt about alkali, go
read the fantastic Django docs and they'll probably point you in the
correct direction. The two relevant sections are about models_ and
queries_.

.. _Django: https://www.djangoproject.com
.. _models: https://docs.djangoproject.com/en/1.10/topics/db/models/
.. _queries: https://docs.djangoproject.com/en/1.10/topics/db/queries/

Goals
-----

Since my ultimate goal was a backwards compatible jrnl with webserver
syncing, everything in alkali had to support that.

So here is the list of non-negotiable features that alkali had to support:

* write data files in plain text (be compatible with existing journals)

Yep, that's basically it. *Other features like searching are implied*.

Alkali needed to allow a developer to control the on-disk
format of its data. And that was easy to accomplish,
just inherit from :class:`alkali.storage.Storage` and
override :func:`alkali.storage.IStorage.read` and
:func:`alkali.storage.IStorage.write`.

This simple pattern was so effective that I now have a REST storage
class and that's how jrnl now syncs with a webserver.
