"""Collect data that is relevant to be sampled once an hour."""
from jax_omerometrics import server_up
import timeit
import argparse
import datetime
from pandas import DataFrame
from pathlib import Path
import smtplib
from email.message import EmailMessage
from config import OMERO_USER, OMERO_PASS, SMTP_HOST, SMTP_PORT, ALERTEES


def collect_data(repeats, user, pwd, img_id, web_address, address):
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
    # print("starting check json status")
    # json_status = server_up.check_web_api(user, pwd, img_id, web_address, verify=False)
    # print(f"initial json status: {json_status}")
    # if (not json_status):
    #     json_timing = 8
    # else:
    #     json_timing = timeit.timeit(lambda: server_up.check_web_api(
    #                                 user, pwd, img_id, web_address),
    #                                 number=repeats, globals=globals()
    #                                 ) / repeats
    # json_timing = round(json_timing, 3)
    ldap_status = server_up.check_ldap_login(user, pwd, address)
    if (not ldap_status):
        ldap_timing = 8
    else:
        ldap_timing = timeit.timeit(lambda: server_up.check_ldap_login(
                                    user, pwd, address),
                                    number=repeats, globals=globals()
                                    ) / repeats
    ldap_timing = round(ldap_timing, 3)
    blitz_status = server_up.check_img_return(img_id, user, pwd, address)
    if (not blitz_status):
        blitz_timing = 8
    else:
        blitz_timing = timeit.timeit(
                lambda: server_up.check_img_return(
                        img_id, user, pwd, address),
                number=repeats, globals=globals()
                ) / repeats
    blitz_timing = round(blitz_timing, 3)
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M")
    status_list = [timestamp, web_status,
                   # json_status, 
                   ldap_status, blitz_status]
    timing_list = [timestamp, web_timing,
                   # json_timing, 
                   ldap_timing, blitz_timing]
    color_status = [web_status,
                    # json_status,
                    ldap_status, blitz_status]
    if all(color_status):
        status_list.append("green")
    elif any(color_status):
        status_list.append("orange")
    else:
        status_list.append("red")
    status_headers = ['timestamp', 'webpage',# 'json_api',
                      'ldap', 'blitz_api', 'color']
    timing_headers = ['timestamp', 'webpage',# 'json_api',
                     'ldap', 'blitz_api']
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

def send_email(content):
    s = smtplib.SMTP(host=SMTP_HOST, port=SMTP_PORT)
    for alertee in ALERTEES:
        msg = EmailMessage()
        msg.set_content(content) # "OMERO Blitz connection time exceeded alert limit"
        msg['Subject'] = "TEST Alert from omerodashboard.jax.org TEST"
        msg['From'] = ALERTEES[0]
        msg['To'] = alertee
        s.send_message(msg)
    s.quit()

def send_alerts(status, timing):
    if not status["blitz_api"][0]:
        print("Sending emails for Blitz API alert unresponsive")
        send_email("THIS IS A TEST. Blitz api unresponsive")
    elif timing["blitz_api"][0] > 4:
        print("Sending emails for Blitz API alert slow")
        blitz_timing = timing["blitz_api"][0]
        send_email(f"THIS IS A TEST. Blitz API slow response time at {blitz_timing} seconds.")
    # if timing["json_api"][0] > 5:
    #     print("Sending emails for JSON API alert")
    #     json_timing = timing["json_api"][0]
    #     if json_timing == 8:
    #         send_email("THIS IS A TEST. JSON API unresponsive")
    #     else:
    #         send_email(f"THIS IS A TEST. JSON API slow response time at {json_timing} seconds.")

if __name__ == "__main__":
    description = 'Run this to collect data hourly.'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('folder',
                        type=str,
                        help='Full path to folder where\
                              data will be saved')
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
    repeats = 1
    print(args.img_id)
    status, timing = collect_data(repeats, OMERO_USER, OMERO_PASS, args.img_id,
                                  args.web_addr, args.addr)
    write_csvs(status, timing, args.folder)
    send_alerts(status, timing)
