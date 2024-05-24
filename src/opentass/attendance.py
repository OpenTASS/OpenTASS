import logging
import requests
import argparse
from tabulate import tabulate
import pandas as pd

import login


def main():
    pass


# status is either tocomplete or completed
def absence_list(auth_cookies, tassweb_url, filter_acceptable=""):

    if (filter_acceptable is None) or (filter_acceptable != "Y" or "N"):
        filter_acceptable = ""

    logging.info(f"Using {tassweb_url} as the remote root.")

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

    df = df.T.drop("absent_type", errors="ignore")
    df = df.drop("absent_date_desc", errors="ignore")
    df = df.drop("accept_ind_desc", errors="ignore")
    df = df.drop("att_year", errors="ignore")
    df = df.drop("dcert_flg_desc", errors="ignore")
    df = df.drop("reas_code", errors="ignore")
    df = df.drop("dcert_flg", errors="ignore")
    df = df.drop("prd_code", errors="ignore")
    df = df.drop("corr_date", errors="ignore")
    df = df.drop("accept_ind_description", errors="ignore")
    df = df.drop(
        "par_flg", errors="ignore"
    )  # can't find what this is, we'll ignore it for now
    df = df.drop("isplpending", errors="ignore")  # same with this
    df = df.drop("id", errors="ignore")
    df = df.drop("absent_type_hover", errors="ignore")
    df = df.drop("ref_num", errors="ignore")
    df = df.drop("key_num", errors="ignore")
    df = df.drop("att_desc", errors="ignore")
    df = df.drop("group_desc", errors="ignore")
    df = df.drop("par_flg_desc_full", errors="ignore")
    df = df.drop("absent_date_from", errors="ignore")
    df = df.drop("absent_date_to", errors="ignore")
    df = df.drop("recur_num", errors="ignore")
    df = df.drop("stud_code", errors="ignore")
    df = df.drop("corr_flg", errors="ignore")
    df = df.drop("abs_from_time", errors="ignore")
    df = df.drop("par_date", errors="ignore")
    df = df.drop("atype_desc_display", errors="ignore")
    df = df.drop("atype_detail", errors="ignore")
    df = df.drop("pl_key_num", errors="ignore")
    df = df.drop("tt_id", errors="ignore")

    df = df.T

    try:
        df = df.rename(
            columns={
                "absent_date": "Date",
                "semester": "Term/Semester",
                "absent_time": "Start Time",
                "accept_ind": "Acceptable?",
                "note_text": "Notes",
                "abs_to_time": "End Time",
                "par_flg_desc": "Parent Acknowledgement?",
                "prd_desc": "Period",
                "corr_flg_desc": "Parent Notified?",
                "atype_desc": "Absence Description",
                "areas_desc": "Reason",
            }
        )
    except IndexError:
        pass

    try:
        df = df.T.reindex(
            index=[
                "Date",
                "Term/Semester",
                "Start Time",
                "End Time",
                "Period",
                "Absence Description",
                "Reason",
                "Notes",
                "Acceptable?",
                "Parent Notified?",
                "Parent Acknowledgement?",
            ]
        )
    except IndexError:
        pass

    df = df.fillna("")
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
        help='Whether to filter if the reasons are acceptable, "Y" or "N" (for all absences, do not specify). Default = Y.',
        required=False,
        default="Y",
    )

    args = parser.parse_args()

    auth_cookies = login.get_auth_cookie(
        args.tassweb_url,
        args.username,
        args.password,
    )

    absence_table = absence_list(
        auth_cookies,
        args.tassweb_url,
        filter_acceptable=args.filter_acceptable,
    )

    print()
    print(tabulate(absence_table[0], headers="keys"))
