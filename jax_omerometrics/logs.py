"""Check OMERO logs at /opt/omero/server/OMERO.server/var/log in pods"""
import datetime
import difflib
import re
from pathlib import Path
import paramiko


LOG_DIR = "/opt/omero/server/OMERO.server/var/log"
IGNORED_ERRORS = [
        re.compile(r"IFD"),
        re.compile(r"invocation")
    ]


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


def check_last_hour(logfilenames, ssh_user, ssh_pwd, ctrl_pln,
                    pod="omero-server", namespace="omero-dev"):
    """Return {logfilename: [ERROR lines]} for the last hour, across
    all of logfilenames, using a single SSH session."""
    # get current time
    now = datetime.datetime.now(datetime.timezone.utc) # pods use UTC time
    # set string variable to last hour in "2026-09-14 19:51:00" format
    last_hour = (now - datetime.timedelta(hours=1)).strftime("%Y-%m-%d %H")
    # log file path is /opt/omero/server/OMERO.server/var/log + logfilename
    logpaths = {f"{LOG_DIR}/{name}": name for name in logfilenames}
    # ssh to servername.jax.org using password from config.py, running kubectl exec grep for last hour in each logfile inside kubernetes pod omero-server, in one session
    command = (
        f"kubectl exec {pod} -n {namespace} -- "
        f"grep -H '{last_hour}' " + " ".join(logpaths)
    )
    output = _run_remote_command(ssh_user, ssh_pwd, ctrl_pln, command)
    # grep for lines with ERROR, ignoring common errors, grouped by logfile
    results = {name: [] for name in logfilenames}
    for line in output.splitlines():
        path, _, content = line.partition(":")
        name = logpaths.get(path)
        if name is None:
            continue
        if "ERROR" in content and not any(p.search(content) for p in IGNORED_ERRORS):
            results[name].append(content)
    # return error lines by logfile
    return results


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
    if prev_path.exists():
        previous = prev_path.read_text()
    else:
        previous = ""
    # compare current and previous master.err
    if current != previous:
        # if different: return difference and save new as prev locally
        diff = list(difflib.unified_diff(
            previous.splitlines(),
            current.splitlines(),
            lineterm="",
        ))
        # TODO: (optional) use following commented lines to not alert if master.err has only decreased (e.g. for pod restart)
        # added_lines = [line for line in diff
        #               if line.startswith("+") and not line.startswith("+++")]
        # removed_lines = [line for line in diff
        #                  if line.startswith("-") and not line.startswith("---")]
        # only_removals = bool(removed_lines) and not added_lines
        prev_path.write_text(current)
        return diff
    # otherwise return all clear
    return None
