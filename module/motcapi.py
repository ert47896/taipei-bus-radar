from hashlib import sha1
import hmac, base64, os
from time import gmtime, strftime
from dotenv import load_dotenv
load_dotenv()

# Reference: https://github.com/ptxmotc/Sample-code
class Auth():
    def __init__(self):
        self.app_id = os.getenv("motcAPI_id")
        self.app_key = os.getenv("motcAPI_key")
    
    def authHeader(self):
        # FRC 1123 Time Format
        xdate = strftime("%a, %d %b %Y %H:%M:%S GMT", gmtime())
        hashed = hmac.new(self.app_key.encode("utf-8"), ("x-date: " + xdate).encode("utf8"), sha1)
        signature = base64.b64encode(hashed.digest()).decode()
        authorization = 'hmac username="' + self.app_id + '", ' + \
            'algorithm="hmac-sha1", ' + \
            'headers="x-date", ' + \
            'signature="' + signature + '"'
        return {
            "Authorization": authorization,
            "x-date": strftime("%a, %d %b %Y %H:%M:%S GMT", gmtime()),
            "Accept - Encoding": "gzip"
        }