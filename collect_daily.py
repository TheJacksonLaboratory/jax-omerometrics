"""Collect data that is relevant to be sampled once a day."""
from jax_omerometrics import queries
import ezomero
import argparse
import datetime
from pandas import DataFrame
from pathlib import Path
from config import OMERO_USER, OMERO_PASS, SMTP_HOST, SMTP_PORT, ALERTEES


def collect_data(user, pwd, address):
    """Collect the actual data using HQL queries."""
    conn = ezomero.connect(user, pwd, group='',
                           host=address, port=4064, secure=True)
    yesterday = datetime.datetime.now() - datetime.timedelta(1)
    timestamp = yesterday.strftime("%Y-%m-%d")
    allsessions = queries.sessions_per_day(conn, timestamp)
    conn.close()
    total_users = len(allsessions)
    total_sessions = sum([i[1] for i in allsessions])
    sessions_list = [timestamp, total_sessions, total_users]
    sessions_headers = ['timestamp', 'sessions', 'users']
    sessions = DataFrame([sessions_list], columns=sessions_headers)
    return sessions


def write_csvs(sessions, folder):
    """Write the collected data into a CSV file for display."""
    if (Path(folder) / 'sessions.csv').exists():
        sessions.to_csv(Path(folder) / 'sessions.csv',
                        mode='a', index=False, header=False)
    else:
        sessions.to_csv(Path(folder) / 'sessions.csv', mode='a', index=False)


if __name__ == "__main__":
    description = 'Run this to collect data daily.'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('folder',
                        type=str,
                        help='Full path to folder where\
                              data will be saved')
    parser.add_argument('--addr',
                        type=str,
                        default="ctomero01lp.jax.org",
                        help='Address for OMERO server instance')
    args = parser.parse_args()
    sessions = collect_data(OMERO_USER, OMERO_PASS, args.addr)
    write_csvs(sessions, args.folder)
