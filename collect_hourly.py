from jax_omerometrics import server_up
import timeit
import keyring
import argparse
import datetime
from pandas import DataFrame
from pathlib import Path

def collect_data(repeats, pwd):
    web_status=server_up.check_web_response()
    web_timing=timeit.timeit("server_up.check_web_response()", 
                            number=repeats, globals=globals())/repeats
    web_timing = round(web_timing, 3)
    json_status = server_up.check_web_api('ratame', pwd, 87066)
    json_timing = timeit.timeit("server_up.check_web_api('ratame', pwd, 87066)",
                                number=repeats, globals=globals())/repeats
    json_timing = round(json_timing, 3)
    ldap_status = server_up.check_ldap_login('ratame', pwd)
    ldap_timing = timeit.timeit("server_up.check_ldap_login('ratame', pwd)",
                                number=repeats, globals=globals())/repeats
    ldap_timing = round(ldap_timing, 3)
    blitz_status = server_up.check_img_return(87066, 'ratame', pwd)
    blitz_timing = timeit.timeit("server_up.check_img_return(87066, 'ratame', pwd)",
                                number=repeats, globals=globals())/repeats
    blitz_timing = round(blitz_timing, 3)
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M")
    status_list = [timestamp, web_status, json_status, ldap_status, blitz_status]
    timing_list = [timestamp, web_timing, json_timing, ldap_timing, blitz_timing]
    if all(status_list):
        status_list.append("green")
    elif any(status_list):
        status_list.append("orange")
    else:
        status_list.append("red")
    status_headers = ['timestamp', 'webpage', 'json_api', 'ldap', 'blitz_api', 'color']
    timing_headers = ['timestamp', 'webpage', 'json_api', 'ldap', 'blitz_api']
    status = DataFrame([status_list], columns=status_headers)
    timing = DataFrame([timing_list], columns=timing_headers)
    return status, timing

def write_csvs(status, timing, folder):
    if (Path(folder) / 'status.csv').exists():
        status.to_csv(Path(folder) / 'status.csv', mode='a', index=False, header=False)
    else:
        status.to_csv(Path(folder) / 'status.csv', mode='a', index=False)
    if (Path(folder) / 'timings.csv').exists():
        timing.to_csv(Path(folder) / 'timings.csv', mode='a', index=False, header=False)
    else:
        timing.to_csv(Path(folder) / 'timings.csv', mode='a', index=False)




if __name__ == "__main__":
    description = 'Run this to collect data hourly.'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('folder',
                        type=str,
                        help='Full path to folder where\
                              data will be saved')
    parser.add_argument('user',
                        type=str,
                        help='OMERO username')
    args = parser.parse_args()
    repeats = 5
    pwd = keyring.get_password('omero', args.user)
    status, timing = collect_data(repeats, pwd)
    write_csvs(status, timing, args.folder)
    