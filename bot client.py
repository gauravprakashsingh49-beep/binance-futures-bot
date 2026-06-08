import time
import hmac
import hashlib
import requests
print("request installed successfully")
from urllib.parse import urlencode

class BinanceClient:

    def __init__(
        self,
        api_key,
        api_secret,
        base_url
    ):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url

    def _sign(self, params):

        query_string = urlencode(params)

        signature = hmac.new(
            self.api_secret.encode(),
            query_string.encode(),
            hashlib.sha256
        ).hexdigest()

        return signature

    def place_order(self, payload):

        endpoint = "/fapi/v1/order"

        payload["timestamp"] = int(
            time.time() * 1000
        )

        payload["signature"] = self._sign(
            payload
        )

        headers = {
            "X-MBX-APIKEY": self.api_key
        }

        response = requests.post(
            self.base_url + endpoint,
            params=payload,
            headers=headers,
            timeout=10
        )

        response.raise_for_status()

        return response.json()