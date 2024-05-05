import os
import logging
import requests
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.DEBUG,
    datefmt="%d/%m/%y %H:%M:%S",
    format="%(asctime)s [%(levelname)s]: %(message)s",
)


def main():
    pass

def get_auth_cookie():
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
        logging.info("Successfully authenticated.")

        return response.cookies

    else:
        logging.fatal(
            "Login failed. Make sure your URL is correct, in the .env config file."
        )
        exit(1)


if __name__ == "__main__":
    logging.info(f"The authentication cookie from the server was: {get_auth_cookie()}")
