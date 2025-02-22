import requests
from src.xauth.xauth import XAuth


class X:
    def __init__(self):
        self.xauth = XAuth()

    def create_post(self, post):
        access_token = None

        access_token = self.xauth.get_access_token()
        if not access_token:
            print("Authentication in progress. Complete it in your browser.")
            access_token = self.xauth.get_access_token()

        print("Posting!")
        response = requests.post(
            "https://api.x.com/2/tweets",
            json={"text": post},
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
        )

        return response
