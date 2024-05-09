import logging
import requests
import argparse
from datetime import datetime
from tabulate import tabulate
import pandas as pd

import login


logging.basicConfig(
    level=logging.DEBUG,
    datefmt="%d/%m/%y %H:%M:%S",
    format="%(asctime)s (%(filename)s) [%(levelname)s]: %(message)s",
)


def main():
    pass


def get_day_timetable(
    auth_cookies, tassweb_url, date=None
):  # Date is in YYYY-MM-DD format.

    logging.info(f"Using {tassweb_url} as the remote root.")

    # Send request to the protected URL
    if date is None:
        payload = {}

    else:

        payload = {
            "start": date,
        }

    params = {"do": "studentportal.timetable.main.todaysTimetable.grid"}

    protected_response = requests.post(
        tassweb_url + "/remote-json.cfm",
        data=payload,
        params=params,
        cookies=auth_cookies,
    )

    if protected_response.ok:
        logging.info("Successfully accessed timetable. Extracting info...")
        site_data = protected_response.json()
        debug_file = open("debug_data.py", "w")
        debug_file.write(str(site_data))
        debug_file.close()
        # print(site_data["HEADERLABEL"])

        df = pd.DataFrame(site_data["DATA"])
        df = df.T.drop("sub_code", errors="ignore")
        df = df.drop("room_code", errors="ignore")
        df = df.drop("allDay", errors="ignore")
        df = df.drop("currentperiod", errors="ignore")
        df = df.drop("tch_code", errors="ignore")
        df = df.drop("prd_code", errors="ignore")
        df = df.drop("day_code", errors="ignore")
        df = df.drop("start", errors="ignore")
        df = df.drop("end", errors="ignore")
        df = df.drop("id", errors="ignore")
        df = df.drop("display_tch_name", errors="ignore")
        df = df.drop(
            "diplay_tch_code", errors="ignore"
        )  # typo intentional, made on their backend lol
        df = df.drop("year_grp_desc", errors="ignore")
        df = df.drop("tt_id", errors="ignore")
        df = df.drop("title", errors="ignore")
        df = df.drop("description", errors="ignore")

        try:
            df = df.reindex(
                index=[
                    "prd_desc",
                    "start_time",
                    "end_time",
                    "sub_desc",
                    "class",
                    "year_grp",
                    "tch_name",
                    "room_desc",
                ]
            )
        except IndexError:
            pass

        try:
            df = df.T.rename(
                columns={
                    "prd_desc": "Period",
                    "start_time": "Start",
                    "end_time": "End",
                    "sub_desc": "Subject",
                    "class": "Class",
                    "year_grp": "Year Group",
                    "tch_name": "Teacher",
                    "room_desc": "Room",
                }
            )
        except IndexError:
            pass

        df["Year Group"] = df["Year Group"].infer_objects(copy=False).fillna(-1)
        df = df.fillna("")
        df["Year Group"] = df["Year Group"].astype(int)
        df["Year Group"] = df["Year Group"].replace(-1, "")

        return df, df.to_html(index=False), site_data["HEADERLABEL"], site_data

    else:
        logging.fatal(
            "Failed to access timetable. Make sure your URL or authentication is correct."
        )

        raise requests.exceptions.RequestException(
            "Failed to access timetable. Make sure your URL or authentication is correct."
        )
        exit(1)


def get_current_class(auth_cookies, tassweb_url, date=None, time=None):
    if time is None:
        specified_time = datetime.now().time()
    else:
        specified_time = datetime.today().strptime(time, "%H:%M")
        specified_time = specified_time.time()

    df = get_day_timetable(auth_cookies, tassweb_url, date)[0]

    # Convert time columns to datetime objects with specified format
    df["Start"] = pd.to_datetime(df["Start"], format="%I:%M %p").dt.time
    df["End"] = pd.to_datetime(df["End"], format="%I:%M %p").dt.time

    if date is None:
        date = datetime.today().strftime('%Y-%m-%d')

    # Loop through each row in the DataFrame
    for index, row in df.iterrows():
        start_time = row["Start"]
        end_time = row["End"]

        logging.debug(
            f"Start: {start_time} and time now: {specified_time} and end: {end_time}"
        )

        # Check if current time is within this period
        if start_time <= specified_time <= end_time:

            period = (
                date,
                row["Period"],
                row["Start"],
                row["End"],
                row["Subject"],
                row["Class"],
                row["Year Group"],
                row["Teacher"],
                row["Room"],
            )

            break
    else:
        period = None

    return period


def get_next_class(auth_cookies, tassweb_url, date=None, time=None, offset=0):

    if time is None:
        specified_time = datetime.now().time()
    else:
        specified_time = datetime.today().strptime(time, "%H:%M")
        specified_time = specified_time.time()

    df = get_day_timetable(auth_cookies, tassweb_url, date)[0]

    # Convert time columns to datetime objects with specified format
    df["Start"] = pd.to_datetime(df["Start"], format="%I:%M %p").dt.time
    df["End"] = pd.to_datetime(df["End"], format="%I:%M %p").dt.time

    if date is None:
        date = datetime.today().strftime('%Y-%m-%d')

    # Loop through each row in the DataFrame
    for index, row in df.iterrows():
        start_time = row["Start"]
        end_time = row["End"]

        logging.debug(
            f"Start: {start_time} and time now: {specified_time} and end: {end_time}"
        )

        # Check if current time is within this period
        if start_time <= specified_time <= end_time:

            next_index = index + 1 + offset

            if next_index >= len(df.index) - 1:
                return None

            while df.loc[next_index]["Subject"] == '' and df.loc[next_index]["Class"] == '' and df.loc[next_index]["Year Group"] == '' and df.loc[next_index]["Teacher"] == '' and df.loc[next_index]["Room"] == '':
                print(next_index)
                if next_index == len(df.index) - 1:
                    break
                next_index = next_index + 1

            period = (
                date,
                df.loc[next_index]["Period"],
                df.loc[next_index]["Start"],
                df.loc[next_index]["End"],
                df.loc[next_index]["Subject"],
                df.loc[next_index]["Class"],
                df.loc[next_index]["Year Group"],
                df.loc[next_index]["Teacher"],
                df.loc[next_index]["Room"]
            )
            break
    else:
        period = None

    return period


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        prog="login.py",
        description="Direct interface, returns a text-mode timetable from a supplied TASSweb URL, username and password.",
    )

    parser.add_argument("tassweb_url", help="TASSweb installation root URL")
    parser.add_argument("username", help="TASSweb username")
    parser.add_argument("password", help="TASSweb password")
    parser.add_argument(
        "-d",
        "--date",
        help="Optional date specified, in YYYY-MM-DD format",
        required=False,
    )
    parser.add_argument(
        "-t",
        "--time",
        help="Optional time specified, in HH:MM (24h) format",
        required=False,
    )

    args = parser.parse_args()

    auth_cookie = login.get_auth_cookie(args.tassweb_url, args.username, args.password)

    timetable = get_day_timetable(
                auth_cookie,
                args.tassweb_url,
                args.date,
            )
    current = get_current_class(
                auth_cookie,
                args.tassweb_url,
                args.date,
                args.time
            )
    next = get_next_class(
                auth_cookie,
                args.tassweb_url,
                args.date,
                args.time
            )

    print()
    print(timetable[2])
    print()

    print(
        tabulate(
            timetable[0],
            headers="keys"
        )
    )

    if args.time is None:
        args.time = datetime.now().time().strftime('%H:%M:%S')

    if current is None:
        print()
        print("No period is currently in progress.")
        if next is None:
            print()
            print("No period is next up.")
        exit(0)

    print()
    print(f"Current Class ({current[0]}, {args.time}):")

    if current[4] == '' and current[5] == '' and current[6] == '' and current[7] == '' and current[8] == '':
        print(f"In {current[1]}, from {current[2]} to {current[3]}, you have no class.")

    else:
        print(
            f"In {current[1]}, from {current[2]} to {current[3]}, you have {current[4]} with the class {current[5]} and year group {current[6]} with teacher {current[7]} in room {current[8]}."
        )

    if next is None:
        print()
        print("No period is next up.")
        exit(0)

    print()
    print(f"Next Class ({next[0]}, {args.time}):")

    if next[4] == '' and next[5] == '' and next[6] == '' and next[7] == '' and next[8] == '':
        print(f"In {next[1]}, from {next[2]} to {next[3]}, you have no class.")

    else:
        print(
            f"In {next[1]}, from {next[2]} to {next[3]}, you have {next[4]} with the class {next[5]} and year group {next[6]} with teacher {next[7]} in room {next[8]}."
        )
