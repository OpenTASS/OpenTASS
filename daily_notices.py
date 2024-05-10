import logging
import requests
import argparse
from datetime import datetime
from tabulate import tabulate
import pandas as pd
import login


def main():
    pass


def get_daily_notices(
    auth_cookies, tassweb_url, date=None
):  # Date is in YYYY-MM-DD format.

    logging.info(f"Using {tassweb_url} as the remote root.")

    # Send request to the protected URL
    if date is None:
        payload = {
            "start": datetime.today().strftime('%Y-%m-%d')
        }

    else:

        payload = {
            "start": date,
        }

    params = {"do": "studentportal.calendar.main.dailynotices.grid"}

    protected_response = requests.post(
        tassweb_url + "/remote-json.cfm",
        data=payload,
        params=params,
        cookies=auth_cookies,
    )

    site_data = protected_response.json()

    df = pd.DataFrame(site_data["DATA"])

    df = df.drop("editable", errors="ignore")
    df = df.drop("recur_id", errors="ignore")
    df = df.drop("id", errors="ignore")
    df = df.drop("cat_num", errors="ignore")
    df = df.drop("allDay", errors="ignore")
    df = df.drop("start_time", errors="ignore")
    df = df.drop("start_date", errors="ignore")
    df = df.drop("end_time", errors="ignore")
    df = df.drop("end_date", errors="ignore")
    df = df.drop("dayFlag", errors="ignore")
    df = df.drop("singleDay", errors="ignore")
    df = df.drop("source", errors="ignore")
    df = df.drop("wkdesc_flg", errors="ignore")
    df = df.drop("event_id", errors="ignore")
    df = df.drop("entry_code", errors="ignore")
    df = df.drop("start", errors="ignore")
    df = df.drop("end", errors="ignore")
    df = df.drop("when_time", errors="ignore")
    df = df.drop("has_attatchment", errors="ignore")
    df = df.drop("url_text", errors="ignore")

    try:
        df = df.T.reindex(
            index=[
                "title",
                "summary",
                "description",
                "day_time_desc",
                "cat_desc",
                "entry_name",
                "room_desc",
                "location",
                "url_link"
            ]
        )
    except IndexError:
        pass

    try:
        df = df.T.rename(
            columns={
                "title": "Title",
                "summary": "Summary",
                "description": "Description",
                "day_time_desc": "Date & Time",
                "cat_desc": "Category",
                "entry_name": "Name",
                "room_desc": "Room",
                "location": "Location",
                "url_link": "URL"
            }
        )
    except IndexError:
        pass

    return df, df.to_html(index=False), site_data["headerlabel"], site_data

if __name__ == "__main__":

    logging.basicConfig(
        level=logging.WARN,
        datefmt="%d/%m/%y %H:%M:%S",
        format="%(asctime)s (%(filename)s) [%(levelname)s]: %(message)s",
    )

    parser = argparse.ArgumentParser(
        prog="daily_notices.py",
        description="Direct interface, returns a notice list cookie from a supplied TASSweb URL, username and password.",
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

    daily_notices = get_daily_notices(login.get_auth_cookie(args.tassweb_url, args.username, args.password), args.tassweb_url, args.date)

    print()
    print(daily_notices[2])
    print()
    print(tabulate(daily_notices[0], headers="keys"))
