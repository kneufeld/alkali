__title__ = 'redb'
__version__ = '0.0.1'
__author__ = 'Kurt Neufeld'
__author_email__ = 'kneufeld@burgundywall.com'
__license__ = 'MIT License'
__copyright__ = 'Copyright 2016 - 2016 Kurt Neufeld'

import datetime as dt
from dateutil.tz import tzlocal

def tznow( tzinfo = None ):
    if tzinfo is None:
        tzinfo = tzlocal()
    return dt.datetime.now( tzinfo )

def tzadd( dtstamp, tzinfo=None ):
    # add, don't replace
    if dtstamp.tzinfo is not None:
        return dtstamp

    if tzinfo is None:
        tzinfo = tzlocal()

    return dtstamp.replace( tzinfo=tzinfo )

def fromts( ts ):
    return tzadd( dt.datetime.fromtimestamp(ts) )


from .database import Database
from .storage import IStorage, Storage, JSONStorage
from .manager import Manager
from .model import IModel, Model
from .query import Query
from . import fields
