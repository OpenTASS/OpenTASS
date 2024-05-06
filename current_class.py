import logging
import argparse
from datetime import datetime
from tabulate import tabulate
import pandas as pd

import login
from timetable import get_day_timetable

logging.basicConfig(
    level=logging.DEBUG,
    datefmt="%d/%m/%y %H:%M:%S",
    format="%(asctime)s (%(filename)s) [%(levelname)s]: %(message)s",
)


def get_current_class(auth_cookies, tassweb_url, date=None, time=None):
    if time is None:
        specified_time = datetime.now()
    else:
        specified_time = datetime.strptime(time, "%H:%M")

    df = get_day_timetable(auth_cookies, tassweb_url, date)

    # Convert time columns to datetime objects with specified format
    df["Start"] = pd.to_datetime(df["Start"], format="%I:%M %p")
    df["End"] = pd.to_datetime(df["End"], format="%I:%M %p")

    # Loop through each row in the DataFrame
    for index, row in df.iterrows():
        start_time = row["Start"]
        end_time = row["End"]

        # Check if current time is within this period
        if start_time <= specified_time <= end_time:
            break
    else:
        row = "No period is currently in progress."
    return row


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
        help="Optional date specified, in YYYY-MM-DD format. (Example: -d 2024-09-02)",
        required=False,
    )
    parser.add_argument(
        "-t",
        "--time",
        help="Optional time specified, in 24hr HH:MM format. (Example: -t 15:30)",
        required=False,
    )

    args = parser.parse_args()

    print(
        tabulate(
            get_current_class(
                login.get_auth_cookie(args.tassweb_url, args.username, args.password),
                args.tassweb_url,
                args.date,
                args.time,
            )
        )
    )
