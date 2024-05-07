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

        today = datetime.now()

        if is_weekend(today.year, today.month, today.day):
            logging.info("It is a weekend. Either run the program on a non-weekend,")
            logging.info("or specify a date.")
            logging.info("Exiting.")
            exit(1)

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

        return df, df.to_html(index=False)

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
        specified_time = datetime.now().replace(year=1900, month=1, day=1)
    else:
        specified_time = datetime.strptime(time, "%H:%M")

    df = get_day_timetable(auth_cookies, tassweb_url, date)[0]

    # Convert time columns to datetime objects with specified format
    df["Start"] = pd.to_datetime(df["Start"], format="%I:%M %p")
    df["End"] = pd.to_datetime(df["End"], format="%I:%M %p")

    # Loop through each row in the DataFrame
    for index, row in df.iterrows():
        start_time = row["Start"]
        end_time = row["End"]

        logging.debug(
            f"Start: {start_time} and time now: {specified_time} and end: {end_time}"
        )

        # Check if current time is within this period
        if start_time <= specified_time <= end_time:

            period = row["Period"], row["Start"], row["End"], row["Subject"], row["Class"], row["Year Group"], row["Teacher"], row["Room"]
            break
    else:
        period = None

    return period


def is_weekend(year, month, day):

    # Create datetime object for the input date
    given_date = datetime(year, month, day)
    day_of_week = given_date.isoweekday()

    # Return if it is a weekday or a weekend
    if day_of_week < 5:
        return False
    else:
        return True


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

    args = parser.parse_args()

    print(
        tabulate(
            get_day_timetable(
                login.get_auth_cookie(args.tassweb_url, args.username, args.password),
                args.tassweb_url,
                args.date,
            )[0],
            headers="keys",
        )
    )
