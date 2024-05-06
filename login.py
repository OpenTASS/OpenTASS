import logging
import requests
import argparse

logging.basicConfig(
    level=logging.DEBUG,
    datefmt="%d/%m/%y %H:%M:%S",
    format="%(asctime)s [%(levelname)s]: %(message)s",
)


def main():
    pass

def get_auth_cookie(tassweb_url, username, password):

    logging.info(f"Using {tassweb_url} as the remote root.")

    payload = {
        "intent": "save",
        "required": "username,password",
        "viewstate": "add",
        "username": username,
        "username_previous": "",
        "password": password,
    }

    params = {"do": "ui.web.user.loginAttempt"}

    logging.info(
        f"""Authenticating using username {username} and provided password."""
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
            "Login failed. Make sure your URL or login details are correct."
        )
        exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    prog='login.py',
                    description='Direct interface, returns a login cookie from a supplied TASSweb URL, username and password.')

    parser.add_argument('tassweb_url', help="TASSweb installation root URL")
    parser.add_argument('username', help="TASSweb username")
    parser.add_argument('password', help="TASSweb password")

    args = parser.parse_args()

    logging.info(f"The authentication cookie from the server was: {get_auth_cookie(args.tassweb_url, args.username, args.password)}")
