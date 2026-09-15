"""Check OMERO logs at /opt/omero/server/OMERO.server/var/log in pods"""
import datetime
import difflib
import re
from pathlib import Path
import paramiko


LOG_DIR = "/opt/omero/server/OMERO.server/var/log"


def _run_remote_command(ssh_user, ssh_pwd, address, command):
    """Run a command on an OMERO server host over SSH and return its stdout."""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(address, username=ssh_user, password=ssh_pwd)
    try:
        _, stdout, _ = client.exec_command(command)
        output = stdout.read().decode()
    finally:
        client.close()
    return output


def check_last_hour(logfilename, ssh_user, ssh_pwd, ctrl_pln,
                    pod="omero-server", namespace="omero-dev"):
    """Return lines logged with ERROR in the last hour of an OMERO log file."""
    # get current time
    now = datetime.datetime.now()
    # set string variable to last hour in "2026-09-14 19:51:00" format
    last_hour = (now - datetime.timedelta(hours=1)).strftime("%Y-%m-%d %H")
    # log file path is /opt/omero/server/OMERO.server/var/log + logfilename
    logpath = f"{LOG_DIR}/{logfilename}"
    # ssh to servername.jax.org using password from config.py, running kubectl exec grep for last hour in logfile inside kubernetes pod omero-server
    command = (
        f"kubectl exec {pod} -n {namespace} -- "
        f"grep '{last_hour}' {logpath}"
    )
    output = _run_remote_command(ssh_user, ssh_pwd, ctrl_pln, command)
    # grep for lines with ERROR
    # known-noisy ERROR lines to drop; add more regex patterns here as needed
    ignored_patterns = [
        re.compile(r"IFD"),
        re.compile(r"invocation"),
    ]
    error_lines = [
        line for line in output.splitlines()
        if "ERROR" in line
        and not any(p.search(line) for p in ignored_patterns)
    ]
    # return error lines
    return error_lines


def check_master_err(prevfile, ssh_user, ssh_pwd, ctrl_pln,
                     pod="omero-server", namespace="omero-dev"):
    """Compare the current master.err against the last saved copy."""
    # master err path is /opt/omero/server/OMERO.server/var/log/master.err
    master_err_path = f"{LOG_DIR}/master.err"
    # ssh to servername.jax.org using password from config.py, running kubectl exec to get the contents of master.err inside kubernetes pod omero-server
    command = f"kubectl exec {pod} -n {namespace} -- cat {master_err_path}"
    current = _run_remote_command(ssh_user, ssh_pwd, ctrl_pln, command)
    # load local saved file of previous master.err
    prev_path = Path(prevfile)
    previous = prev_path.read_text() if prev_path.exists() else None
    # compare current and previous master.err
    if current != previous:
        # if different: return difference and save new as prev locally
        diff = list(difflib.unified_diff(
            (previous or "").splitlines(),
            current.splitlines(),
            lineterm="",
        ))
        added_lines = [line for line in diff
                      if line.startswith("+") and not line.startswith("+++")]
        removed_lines = [line for line in diff
                         if line.startswith("-") and not line.startswith("---")]
        # not used yet, but flags a master.err that only shrank/rotated
        only_removals = bool(removed_lines) and not added_lines
        prev_path.write_text(current)
        return diff
    # otherwise return all clear
    return None
