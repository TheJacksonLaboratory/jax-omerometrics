from jax_omerometrics import queries
import keyring
import ezomero
import argparse
import datetime
from pandas import DataFrame
from pathlib import Path

def collect_data(user, pwd):
    conn = ezomero.connect(user, pwd, host='bhomero01lp.jax.org', port=4064, secure=True)
    yesterday = datetime.datetime.now() - datetime.timedelta(1)   
    timestamp = yesterday.strftime("%Y-%m-%d") 
    allsessions = queries.sessions_per_day(conn, timestamp)
    conn.close()
    total_users = len(allsessions)
    total_sessions = sum([i[1] for i in allsessions])
    sessions_list = [timestamp, total_sessions, total_users]
    sessions_headers = ['timestamp', 'sessions', 'users']
    sessions = DataFrame([sessions_list], columns=sessions_headers)
    print(sessions)
    return sessions

def write_csvs(sessions, folder):
    if (Path(folder) / 'sessions.csv').exists():
        sessions.to_csv(Path(folder) / 'sessions.csv', mode='a', index=False, header=False)
    else:
        sessions.to_csv(Path(folder) / 'sessions.csv', mode='a', index=False)
    




if __name__ == "__main__":
    description = 'Run this to collect data daily.'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('folder',
                        type=str,
                        help='Full path to folder where\
                              data will be saved')
    parser.add_argument('user',
                        type=str,
                        help='OMERO username')
    args = parser.parse_args()
    pwd = keyring.get_password('omero', args.user)
    sessions = collect_data(args.user, pwd)
    write_csvs(sessions, args.folder)
    