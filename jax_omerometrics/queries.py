import datetime
from omero.sys import Parameters
from omero.rtypes import rlong


def user_creation_time(conn, user_id):
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
    time = datetime.datetime.fromtimestamp(results[0][0].val / 1000)
    return time