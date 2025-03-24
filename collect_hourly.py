"""Collect data that is relevant to be sampled once an hour."""
from jax_omerometrics import server_up
import timeit
import keyring
import argparse
import datetime
from pandas import DataFrame
from pathlib import Path


def collect_data(repeats, pwd, img_id, web_address, address):
    """Collect the actual data using different API calls."""

    web_status = server_up.check_web_response(web_address)
    if (not web_status):
        web_timing = 8
    else:
        web_timing = timeit.timeit(
                     lambda: server_up.check_web_response(web_address),
                     number=repeats, globals=globals(),
                                  ) / repeats
    web_timing = round(web_timing, 3)
    print("starting check json status")
    json_status = server_up.check_web_api('ratame', pwd, img_id, web_address)
    print(f"initial json status: {json_status}")
    if (not json_status):
        json_timing = 8
    else:
        json_timing = timeit.timeit(lambda: server_up.check_web_api(
                                    'ratame', pwd, img_id, web_address),
                                    number=repeats, globals=globals()
                                    ) / repeats
    json_timing = round(json_timing, 3)
    ldap_status = server_up.check_ldap_login('ratame', pwd, address)
    if (not ldap_status):
        ldap_timing = 8
    else:
        ldap_timing = timeit.timeit(lambda: server_up.check_ldap_login(
                                    'ratame', pwd, address),
                                    number=repeats, globals=globals()
                                    ) / repeats
    ldap_timing = round(ldap_timing, 3)
    blitz_status = server_up.check_img_return(img_id, 'ratame', pwd, address)
    if (not blitz_status):
        blitz_timing = 8
    else:
        blitz_timing = timeit.timeit(
                lambda: server_up.check_img_return(
                        img_id, 'ratame', pwd, address),
                number=repeats, globals=globals()
                ) / repeats
    blitz_timing = round(blitz_timing, 3)
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M")
    status_list = [timestamp, web_status,
                   json_status, ldap_status, blitz_status]
    timing_list = [timestamp, web_timing,
                   json_timing, ldap_timing, blitz_timing]
    color_status = [web_status,
                    json_status, ldap_status, blitz_status]
    if all(color_status):
        status_list.append("green")
    elif any(color_status):
        status_list.append("orange")
    else:
        status_list.append("red")
    status_headers = ['timestamp', 'webpage', 'json_api',
                      'ldap', 'blitz_api', 'color']
    timing_headers = ['timestamp', 'webpage', 'json_api', 'ldap', 'blitz_api']
    status = DataFrame([status_list], columns=status_headers)
    timing = DataFrame([timing_list], columns=timing_headers)
    return status, timing


def write_csvs(status, timing, folder):
    """Write the collected data into a CSV file for display."""
    if (Path(folder) / 'status.csv').exists():
        status.to_csv(Path(folder) / 'status.csv',
                      mode='a', index=False, header=False)
    else:
        status.to_csv(Path(folder) / 'status.csv', mode='a', index=False)
    if (Path(folder) / 'timings.csv').exists():
        timing.to_csv(Path(folder) / 'timings.csv',
                      mode='a', index=False, header=False)
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
    parser.add_argument('--img_id',
                        type=int,
                        default=87066,
                        help='Image ID to use for testing')
    parser.add_argument('--web_addr',
                        type=str,
                        default="https://omeroweb.jax.org",
                        help='Address for OMERO web instance')
    parser.add_argument('--addr',
                        type=str,
                        default="ctomero01lp.jax.org",
                        help='Address for OMERO server instance')
    args = parser.parse_args()
    repeats = 5
    print(args.img_id)
    pwd = keyring.get_password('omero', args.user)
    status, timing = collect_data(repeats, pwd, args.img_id,
                                  args.web_addr, args.addr)
    write_csvs(status, timing, args.folder)
