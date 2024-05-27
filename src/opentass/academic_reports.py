# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import requests
import argparse
from tabulate import tabulate
import pandas as pd

import login


def main():
    pass


def list_academic_reports(auth_cookies, tassweb_url):

    logging.info(f"Using {tassweb_url} as the remote root.")

    params = {"do": "studentportal.classes.main.myAcademicReports.grid"}

    protected_response = requests.post(
        tassweb_url + "/remote-json.cfm",
        params=params,
        cookies=auth_cookies,
    )

    site_data = protected_response.json()

    df = pd.DataFrame(site_data["DATA"])

    df = df.T.drop("PL_ANALYTICS_COUNT", errors="ignore")
    df = df.drop("PERIOD_NUM_DESC", errors="ignore")
    df = df.drop("AR_DRAFT_FLG", errors="ignore")
    df = df.drop("YEAR_PERIOD_MULTI", errors="ignore")
    df = df.drop("PERIOD_NUM", errors="ignore")
    df = df.drop("PERIOD_NUM_SORT", errors="ignore")
    df = df.drop("ISDRAFTREPORT", errors="ignore")
    df = df.drop("YEAR_NUM", errors="ignore")
    df = df.drop("YEAR_PERIOD", errors="ignore")
    df = df.drop("IA_LOCK_FLG", errors="ignore")

    df = df.T

    try:
        df = df.rename(
            columns={
                "PRD_DESC": "Year / Period",
                "SAR_DESC": "Description",
                "id": "ID",
            }
        )
    except IndexError:
        pass

    return df, df.to_html(index=False), site_data


def dl_report(auth_cookies, tassweb_url, id):

    logging.info(f"Using {tassweb_url} as the remote root.")

    params = {"do": "studentportal.classes.main.myAcademicReports.file", "id": id}

    protected_response = requests.post(
        tassweb_url + "/inline-file.cfm",
        params=params,
        cookies=auth_cookies,
    )

    site_data = protected_response.content

    return site_data


if __name__ == "__main__":

    logging.basicConfig(
        level=logging.WARN,
        datefmt="%d/%m/%y %H:%M:%S",
        format="%(asctime)s (%(filename)s) [%(levelname)s]: %(message)s",
    )

    parser = argparse.ArgumentParser(
        prog="daily_notices.py",
        description="Direct interface, returns an academic reports list from a supplied TASSweb URL, username and password.",
    )

    parser.add_argument("tassweb_url", help="TASSweb installation root URL")
    parser.add_argument("username", help="TASSweb username")
    parser.add_argument("password", help="TASSweb password")

    args = parser.parse_args()

    auth_cookies = login.get_auth_cookie(args.tassweb_url, args.username, args.password)

    academic_reports = list_academic_reports(auth_cookies, args.tassweb_url)

    report_id = academic_reports[0]["ID"].iloc[0]

    print()
    print(tabulate(academic_reports[0], headers="keys"))

    pdf_file = open("academic.pdf", "wb")
    pdf_file.write(dl_report(auth_cookies, args.tassweb_url, report_id))
    pdf_file.close()
