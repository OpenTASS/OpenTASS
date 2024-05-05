import os
import logging
import requests
from datetime import datetime
from dotenv import load_dotenv
from tabulate import tabulate
import pandas as pd

from login import login


def main():
    pass

def get_day_timetable(auth_cookies=login(), date=None):    # Date is in YYYY-MM-DD format.
    load_dotenv()

    tassweb_url = os.getenv("TASSWEB_REMOTE_URL")
    logging.info(f"Using {tassweb_url} as the remote root.")

    # Send request to the protected URL
    if date is None:

        today = datetime.now()

        if is_weekend(today.year, today.month, today.day):
            logging.info(
                "It is a weekend. Either run the program on a non-weekend,"
            )
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
        print(site_data["HEADERLABEL"])

        df = pd.DataFrame(site_data["DATA"])
        df = df.T.drop("sub_code", errors='ignore')
        df = df.drop("room_code", errors='ignore')
        df = df.drop("allDay", errors='ignore')
        df = df.drop("currentperiod", errors='ignore')
        df = df.drop("tch_code", errors='ignore')
        df = df.drop("prd_code", errors='ignore')
        df = df.drop("day_code", errors='ignore')
        df = df.drop("start", errors='ignore')
        df = df.drop("end", errors='ignore')
        df = df.drop("id", errors='ignore')
        df = df.drop("display_tch_name", errors='ignore')
        df = df.drop("diplay_tch_code", errors='ignore')    # typo intentional, made on their backend
        df = df.drop("year_grp_desc", errors='ignore')
        df = df.drop("tt_id", errors='ignore')
        df = df.drop("title", errors='ignore')
        df = df.drop("description", errors='ignore')

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

        df["Year Group"] = df["Year Group"].fillna(-1)
        df = df.fillna("")
        df["Year Group"] = df["Year Group"].astype(int)
        df["Year Group"] = df["Year Group"].replace(-1, "")

        return df.to_html(index=False), tabulate(df, headers="keys")

    else:
        logging.fatal(
            "Failed to access timetable. Make sure your URL is correct in the .env config file."
        )
        exit(1)


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
    pass
