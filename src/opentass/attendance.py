import logging
import requests
import argparse
from tabulate import tabulate
import pandas as pd

import login


def main():
    pass


# status is either tocomplete or completed
def list_events(auth_cookies, tassweb_url, filter_acceptable=""):

    if filter_acceptable is None:
        filter_acceptable = ""

    logging.info(f"Using {tassweb_url} as the remote root.")

    # Couldn't find anything for the request payload. Maybe there's just nothing ¯\_(ツ)_/¯

    params = {"do": "studentportal.classes.main.myAttendance.grid"}

    payload = {
        "accept_ind": filter_acceptable,
        "absent_type": "",
        "att_year": "",
    }

    protected_response = requests.post(
        tassweb_url + "/remote-json.cfm",
        params=params,
        cookies=auth_cookies,
        data=payload,
    )

    site_data = protected_response.json()

    df = pd.DataFrame(site_data["data"])

    df = df.T.drop("", errors="ignore")

    df = df.T

    try:
        df = df.rename(
            columns={
                "": "",
            }
        )
    except IndexError:
        pass

    try:
        df = df.T.reindex(
            index=[
                "",
            ]
        )
    except IndexError:
        pass

    return df.T, df.to_html(index=False), site_data


if __name__ == "__main__":

    logging.basicConfig(
        level=logging.WARN,
        datefmt="%d/%m/%y %H:%M:%S",
        format="%(asctime)s (%(filename)s) [%(levelname)s]: %(message)s",
    )

    parser = argparse.ArgumentParser(
        prog="attendance.py",
        description="Direct interface, returns an absences list from a supplied TASSweb URL, username and"
        " password.",
    )

    parser.add_argument("tassweb_url", help="TASSweb installation root URL")
    parser.add_argument("username", help="TASSweb username")
    parser.add_argument("password", help="TASSweb password")
    parser.add_argument(
        "-a",
        "--filter-acceptable",
        help='Whether to filter by acceptable reasons, as "Y" or "N" (leave blank for all absences). Default = Y.',
        required=False,
        default="",
    )

    args = parser.parse_args()

    auth_cookies = login.get_auth_cookie(
        args.tassweb_url,
        args.username,
        args.password,
    )

    events_table = list_events(
        auth_cookies,
        args.tassweb_url,
        filter_acceptable=args.filter_acceptable,
    )

    print()
    print(tabulate(events_table[0], headers="keys"))
