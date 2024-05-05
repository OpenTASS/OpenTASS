import os
import logging
import requests
from datetime import datetime
from dotenv import load_dotenv
from tabulate import tabulate
import pandas as pd

logging.basicConfig(
    level=logging.DEBUG,
    datefmt="%d/%m/%y %H:%M:%S",
    format="%(asctime)s [%(levelname)s]: %(message)s",
)


def main():
    load_dotenv()

    tassweb_url = os.getenv("TASSWEB_REMOTE_URL")
    logging.info(f"Using {tassweb_url} as the remote root.")

    tassweb_username = os.getenv("TASSWEB_USERNAME")
    tassweb_password = os.getenv("TASSWEB_PASSWORD")

    payload = {
        "intent": "save",
        "required": "username,password",
        "viewstate": "add",
        "username": tassweb_username,
        "username_previous": "",
        "password": tassweb_password,
    }

    params = {"do": "ui.web.user.loginAttempt"}

    logging.info(
        f"""Authenticating using username {tassweb_username} and provided password."""
    )
    response = requests.post(
        tassweb_url + "/remote-json.cfm", data=payload, params=params
    )

    # Check if login was successful
    if response.ok:
        logging.info("Successfully authenticated. Now getting timetable data...")
        # Now, you can access the protected URL

        # Send request to the protected URL
        if os.getenv("REQUESTED_DATE") is None or os.getenv("REQUESTED_DATE") == "":

            today = datetime.now()

            if is_weekend(today.year, today.month, today.day):
                logging.info(
                    "It is a weekend. Either run the program on a non-weekend,"
                )
                logging.info("or specify REQUESTED_DATE in the environment.")
                logging.info("Exiting.")
                exit(1)

            payload = {}

        else:

            payload = {
                "start": os.getenv("REQUESTED_DATE"),
            }

        params = {"do": "studentportal.timetable.main.todaysTimetable.grid"}

        protected_response = requests.post(
            tassweb_url + "/remote-json.cfm",
            data=payload,
            params=params,
            cookies=response.cookies,
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
            df = df.drop("diplay_tch_code", errors='ignore')  # typo intentional, made on their backend
            df = df.drop("year_grp_desc", errors='ignore')
            df = df.drop("tt_id", errors='ignore')
            df = df.drop("title", errors='ignore')
            df = df.drop("description", errors='ignore')

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
                ],
                errors='ignore'
            )

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
                },
                errors='report'
            )

            df["Year Group"] = df["Year Group"].fillna(-1)
            df = df.fillna("")
            df["Year Group"] = df["Year Group"].astype(int)
            df["Year Group"] = df["Year Group"].replace(-1, "")

            print(tabulate(df, headers="keys"))

            df.to_html("output.html", index=False)

        else:
            logging.fatal(
                "Failed to access timetable. Make sure your URL is correct in the .env config file."
            )
    else:
        logging.fatal(
            "Login failed. Make sure your URL is correct, in the .env config file."
        )


def is_weekend(year, month, day):

    # Create a datetime object for the given date
    given_date = datetime(year, month, day)

    # Use isoweekday() to get the weekday (Monday is 1 and Sunday is 7)
    day_of_week = given_date.isoweekday() % 7  # Convert Sunday from 7 to 0

    # Determine if it's a weekday or a weekend
    if day_of_week < 5:
        return False
    else:
        return True


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        logging.warning("KeyboardInterrupt received, stopping script!")
        exit(130)
