from datetime import datetime
from omero.sys import Parameters
from omero.rtypes import rlong


def user_creation_time(conn, user_id):
    """Return creation date of Experimenter

    """
    q = conn.getQueryService()
    params = Parameters()
    params.map = {"userid": rlong(user_id)}
    results = q.projection(
        "SELECT e.event.time"
        " FROM EventLog e"
        " WHERE e.action='INSERT' and"
        " e.entityType='ome.model.meta.Experimenter' and"
        " e.entityId=:userid",
        params,
        conn.SERVICE_OPTS
        )
    time = datetime.fromtimestamp(results[0][0].val / 1000)
    return time


def originalfile_size_date(conn, originalfile_id):
    """Return size of OriginalFile in bytes, with date stamp

    Note: OriginalFile doesn't necessarily have an associated size.
          Needs to be part of an image fileset

    """
    q = conn.getQueryService()
    params = Parameters()
    params.map = {"fid": rlong(originalfile_id)}
    results = q.projection(
        "SELECT f.size, ce.time"
        " FROM OriginalFile f"
        " JOIN f.details.creationEvent ce"
        " WHERE f.id=:fid",
        params,
        conn.SERVICE_OPTS
        )
    return [(x[0].val, datetime.fromtimestamp(x[1].val / 1000)) for x in results]


def all_originalfiles(conn):
    """Return a list of all OriginalFile ids associated with Images

    """
    q = conn.getQueryService()
    params = Parameters()
    results = q.projection(
        "SELECT f.id"
        " FROM Image i"
        " JOIN i.fileset fs"
        " JOIN fs.usedFiles fe"
        " JOIN fe.originalFile f",
        params,
        conn.SERVICE_OPTS
        )
    return [x[0].val for x in results]


def sessions_per_day(conn, date):
    """Return a list of tuples with users who started sessions on a 
        certain date and the number of sessions per user

        Note: date should be a string formatted YYYY-MM-DD

    """
    q = conn.getQueryService()
    params = Parameters()
    query = "SELECT s.owner.omeName, count(s)" + \
            " FROM Session s" + \
            " WHERE s.started > cast('" + date + " 00:00', timestamp)" + \
            " AND s.started < cast('" + date + " 23:59', timestamp)" + \
            " GROUP by s.owner.omeName"
    results = q.projection(
        query,
        params,
        conn.SERVICE_OPTS
        )
    return [(x[0].val, x[1].val) for x in results]