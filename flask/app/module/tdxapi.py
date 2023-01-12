import requests, json, os
from dotenv import load_dotenv

load_dotenv()

auth_url = (
    "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
)

# Reference: https://github.com/tdxmotc/SampleCode


class Auth:
    def __init__(self):
        self.app_id = os.getenv("motcAPI_id")
        self.app_key = os.getenv("motcAPI_key")

    def get_auth_header(self):
        content_type = "application/x-www-form-urlencoded"
        grant_type = "client_credentials"

        return {
            "content-type": content_type,
            "grant_type": grant_type,
            "client_id": self.app_id,
            "client_secret": self.app_key,
        }


class Data:
    def __init__(self, auth_response):
        self.app_id = os.getenv("motcAPI_id")
        self.app_key = os.getenv("motcAPI_key")
        self.auth_response = auth_response

    def get_data_header(self):
        auth_JSON = json.loads(self.auth_response.text)
        access_token = auth_JSON.get("access_token")

        return {"authorization": "Bearer " + access_token}


def get_data(url):
    try:
        data_instance = Data(auth_response)
        return requests.get(url, headers=data_instance.get_data_header())
    except:
        auth_instance = Auth()
        auth_response = requests.post(auth_url, auth_instance.get_auth_header())
        data_instance = Data(auth_response)
        return requests.get(url, headers=data_instance.get_data_header())
