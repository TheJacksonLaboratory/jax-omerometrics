"""Check OMERO logs at /opt/omero/server/OMERO.server/var/log in pods"""

def check_last_hour(logfilename, passfile):
    # get current time
    # set string variable to last hour in "2026-09-14 19:51:00" format
    # ssh exec grep for last hour in log filename
    # grep for errors excepting common
    # return errors

def check_master_err(passfile):
    # store all master err in string
    # load prev master err in string
    # compare
    # if different: alert and save new as prev

