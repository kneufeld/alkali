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
