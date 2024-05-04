import os
import logging
import requests
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.DEBUG,
    datefmt='%d/%m/%y %H:%M:%S',
    format='%(asctime)s [%(levelname)s]: %(message)s'
)


def main():
    load_dotenv()

    tassweb_url = os.getenv("TASSWEB_REMOTE_URL")
    logging.info(f"Using {tassweb_url} as the URL.")

    tassweb_username = os.getenv("TASSWEB_USERNAME")
    tassweb_password = os.getenv("TASSWEB_PASSWORD")
    payload = {
        'intent': 'save',
        'required': 'username,password',
        'viewstate': 'add',
        'username': tassweb_username,
        'username_previous': '',
        'password': tassweb_password
    }
    logging.info(f"""Authenticating using username {tassweb_username} and provided password.""")
    response = requests.post(tassweb_url, data=payload)

    # Check if login was successful
    if response.ok:
        logging.info("Successfully authenticated. Now getting timetable data...")
        # Now, you can access the protected URL
        protected_url = os.getenv("TASSWEB_HOME_URL")

        # Send request to the protected URL
        protected_response = requests.get(protected_url,
                                          cookies=response.cookies)

        if protected_response.ok:
            logging.info("Successfully accessed timetable. Extracting info...")
            site_html = protected_response.text

            # debug log to timetable file (comment out in prod)
            f = open("timetablepage.html", "w")
            f.write(site_html)
            f.close
        else:
            logging.fatal("""Failed to access timetable. Make sure your URL is correct in the .env config file.""")
    else:
        logging.fatal("""Login failed. Make sure your URL is correct, in the .env config file.""")


if (__name__ == "__main__"):
    try:
        main()
    except KeyboardInterrupt:
        print()
        logging.warning("KeyboardInterrupt received, stopping script!")
        exit(130)
