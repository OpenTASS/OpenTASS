# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import requests
import argparse
from tabulate import tabulate
from datetime import datetime
import pandas as pd

import login


def main():
    pass


# status is either tocomplete or completed
def list_curricular_activities(
    auth_cookies, tassweb_url, status="", year=datetime.today().year
):

    logging.info(f"Using {tassweb_url} as the remote root.")

    payload = {
        "lmsclass": "all",
        "assignmentstatus": status,
        "assign_year": year,
        "topicsubscribe": "activity.details,activity.onlinetest",  # don't know what this does
    }

    params = {"do": "studentportal.activities.main.lmsactivities.grid"}

    protected_response = requests.post(
        tassweb_url + "/remote-json.cfm",
        params=params,
        cookies=auth_cookies,
        data=payload,
    )

    site_data = protected_response.json()

    df = pd.DataFrame(site_data["data"])

    df = df.T.drop("ACTIVITY_ASSIGN_ID", errors="ignore")
    df = df.drop("DRAFT_FILE_LAST_SUBMIT_DATE", errors="ignore")
    df = df.drop("DT_PUBLISH_FINISH_DISPLAY", errors="ignore")
    df = df.drop("STUDENT_DT_PUBLISH_START", errors="ignore")
    df = df.drop("DUE_TODAY_FLG", errors="ignore")
    df = df.drop("ACTIVITY_ASSIGN_ID", errors="ignore")
    df = df.drop("DT_DRAFT_DISPLAY", errors="ignore")
    df = df.drop("isexempt_flg", errors="ignore")
    df = df.drop("STUDENT_DT_PUBLISH_FINISH", errors="ignore")
    df = df.drop("DT_PUBLISH_FINISH", errors="ignore")
    df = df.drop("FINAL_FILE_LAST_SUBMIT_DATE", errors="ignore")
    df = df.drop("DT_PUBLISH_START", errors="ignore")
    df = df.drop("id", errors="ignore")
    df = df.drop("STUDENT_STATUS_DESC_PENDING", errors="ignore")
    df = df.drop("STUDENT_DT_DRAFT", errors="ignore")
    df = df.drop("STUDENT_STATUS_DESC", errors="ignore")
    df = df.drop("DT_DRAFT", errors="ignore")

    df = df.T

    try:
        df = df.rename(
            columns={
                "ASSIGN_NAME": "Group",
                "ASSESSABLE": "Assessable?",
                "STATUS_DESC": "Status",
                "ACTIVITY_UUID": "UUID",
                "START_DATE_DESC": "Start Date",
                "DRAFT_OVERDUE_FLG": "Draft Overdue?",
                "extension_flg": "Extension?",
                "homework_flg": "Homework?",
                "DRAFT_DATE_DESC": "Draft Date",
                "object_name": "Activity Name",
                "DUE_DATE_DESC": "Due Date",
                "OVERDUE_FLG": "Overdue?",
            }
        )
    except IndexError:
        pass

    try:
        df = df.T.reindex(
            index=[
                "Activity Name",
                "Group",
                "Homework?",
                "Assessable?",
                "Start Date",
                "Draft Date",
                "Draft Overdue?",
                "Due Date",
                "Overdue?",
                "Extension?",
                "Status",
                "UUID",
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
        prog="curricular_activities.py",
        description="Direct interface, returns a curricular activities list from a supplied TASSweb URL, username and"
        " password.",
    )

    parser.add_argument("tassweb_url", help="TASSweb installation root URL")
    parser.add_argument("username", help="TASSweb username")
    parser.add_argument("password", help="TASSweb password")

    args = parser.parse_args()

    auth_cookies = login.get_auth_cookie(args.tassweb_url, args.username, args.password)

    curricular_activities = list_curricular_activities(auth_cookies, args.tassweb_url)

    activity_uuid = curricular_activities[0]["UUID"].iloc[0]

    print()
    print(tabulate(curricular_activities[0], headers="keys"))
