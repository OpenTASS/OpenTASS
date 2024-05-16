import logging
import requests
import argparse
from tabulate import tabulate
import pandas as pd

import login


def main():
    pass


# status is either tocomplete or completed
def list_events(auth_cookies, tassweb_url):

    logging.info(f"Using {tassweb_url} as the remote root.")

    # Couldn't find anything for the request payload. Maybe there's just nothing ¯\_(ツ)_/¯

    params = {"do": "studentportal.activities.main.myTours.grid"}

    protected_response = requests.post(
        tassweb_url + "/remote-json.cfm",
        params=params,
        cookies=auth_cookies,
    )

    site_data = protected_response.json()

    df = pd.DataFrame(site_data["DATA"])

    # OK, there's a lot to filter out here, some of which is basically a duplicate of another column
    # If you need any use the raw json data or make a pull request if you think people will want it

    df = df.T.drop("paid_flg", errors="ignore")
    df = df.drop("stud_ack_flg", errors="ignore")
    df = df.drop("table_id", errors="ignore")
    df = df.drop("pctut_grp", errors="ignore")
    df = df.drop("boarder", errors="ignore")
    df = df.drop("record_id", errors="ignore")
    df = df.drop("id", errors="ignore")
    df = df.drop("doe", errors="ignore")
    df = df.drop("dol", errors="ignore")
    df = df.drop("given_name", errors="ignore")
    df = df.drop("stud_ack_by", errors="ignore")
    df = df.drop("preferred_surname", errors="ignore")
    df = df.drop("other_name", errors="ignore")
    df = df.drop("entry_code", errors="ignore")
    df = df.drop("start_time", errors="ignore")
    df = df.drop("sex", errors="ignore")  # don't even think about it-
    df = df.drop("first_name", errors="ignore")
    df = df.drop("stud_med_ack_by", errors="ignore")
    df = df.drop("alt_id", errors="ignore")
    df = df.drop("accept_flg", errors="ignore")
    df = df.drop("ack_by", errors="ignore")
    df = df.drop("stud_med_ack_flag", errors="ignore")
    df = df.drop("cart_num", errors="ignore")
    df = df.drop("paid_date", errors="ignore")
    df = df.drop("attach_id", errors="ignore")
    df = df.drop("surname", errors="ignore")
    df = df.drop("update_by", errors="ignore")
    df = df.drop("med_ack_by", errors="ignore")
    df = df.drop("usi", errors="ignore")
    df = df.drop("start_date", errors="ignore")
    df = df.drop("status_code", errors="ignore")
    df = df.drop("e_mail", errors="ignore")
    df = df.drop("link_url", errors="ignore")
    df = df.drop("ack_attach_id", errors="ignore")
    df = df.drop("stud_code", errors="ignore")
    df = df.drop("tour_comment", errors="ignore")
    df = df.drop("cmpy_code", errors="ignore")
    df = df.drop("form_cls", errors="ignore")
    df = df.drop("ack_flg", errors="ignore")
    df = df.drop("update_on", errors="ignore")
    df = df.drop("end_date", errors="ignore")
    df = df.drop("accept_date", errors="ignore")
    df = df.drop("end_time", errors="ignore")
    df = df.drop("invite_date", errors="ignore")
    df = df.drop("tour_num", errors="ignore")
    df = df.drop("preferred_name", errors="ignore")
    df = df.drop("date_formatted", errors="ignore")

    df = df.T

    try:
        df = df.rename(
            columns={
                "start_date_time": "Start",
                "end_date_time": "End",
                "support": "Department",
                "venue": "Venue",
                "contact_phone": "Contact Phone",
                "contact_email": "Contact Email",
                "contact_name": "Contact Name",
                "med_ack_flg": "Requires Medical Acknowledgement",
                "tch_name": "Teacher Name",
                "yr_grp": "Year Group",
                "tour_desc": "Event",
                "amount_paid": "Amount Paid",
                "stud_status_desc": "Student Attendance Status",
                "status_desc": "Event Status",
                "stud_name": "Student Name",
                "stud_med_ack_flg": "Medical Acknowledgement Given",
            }
        )
    except IndexError:
        pass

    try:
        df = df.T.reindex(
            index=[
                "Event",
                "Start",
                "End",
                "Venue",
                "Department",
                "Teacher Name",
                "Event Status",
                "Requires Medical Acknowledgement",
                "Medical Acknowledgement Given",
                "Student Attendence Status",
                "Amount Paid",
                "Contact Name",
                "Contact Email",
                "Contact Phone",
                "Year Group",
                "Student Name",
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

    events_table = list_events(auth_cookies, args.tassweb_url)

    print()
    print(tabulate(events_table[0], headers="keys"))
