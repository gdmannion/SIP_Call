# call_functions.py

import json
import requests
from requests.auth import HTTPDigestAuth

def make_call(ip_address, cam_user, cam_pass, destination):
    auth = HTTPDigestAuth(cam_user, cam_pass)
    url = f"http://{ip_address}/vapix/call"

    payload = json.dumps({
        "axcall:Call": {
            "To": destination,
            "SIPAccountId": "sip_account_1"
        }
    })

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(url, auth=auth, headers=headers, data=payload)
    return response
