# payments/nowpayments_client.py
import requests
from django.conf import settings
from django.utils.timezone import now


class NowPaymentsClient:
    BASE_URL = settings.NOWPAYMENTS_API_URL
    # BASE_URL = "https://api-sandbox.nowpayments.io/v1"
    API_KEY = settings.NOWPAYMENTS_API_KEY

    @classmethod
    def create_invoice(
        cls,
        amount,
        currency,
        order_id,
        description,
        callback_url,
        success_url,
        cancel_url,
    ):
        print("starting_invoice")
        url = f"{cls.BASE_URL}/invoice"
  
        payload = {
            "price_amount": amount,
            "price_currency": currency,
            "order_id": order_id,
            "order_description": description,
            "ipn_callback_url": callback_url,
            "success_url": success_url,
            "cancel_url": cancel_url,
        }
        headers = {"x-api-key": cls.API_KEY, "Content-Type": "application/json"}

        response = requests.post(url, headers=headers, json=payload,timeout=5)

        try:
            return response.json()
        except Exception as e:
            print("JSON Parse Error:", e)
    @classmethod
    def get_invoice(cls, payment_id):
        url = f"{cls.BASE_URL}/payment/{payment_id}"
        headers = {"x-api-key": cls.API_KEY}

        response = requests.get(url, headers=headers,timeout=5)
        print(response.json())
        try:
            return response.json()
        except Exception as e:
            print("JSON Parse Error:", e)
            return None

