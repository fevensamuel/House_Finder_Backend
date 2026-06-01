import requests
from django.conf import settings

CHAPA_BASE_URL = "https://api.chapa.co/v1"

def initialize_payment(amount, email, tx_ref, callback_url, return_url):
    headers = {"Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"}
    data = {
        "amount": str(amount),
        "currency": "ETB",
        "email": email,
        "tx_ref": tx_ref,
        "callback_url": callback_url,
        "return_url": return_url,
    }
    response = requests.post(f"{CHAPA_BASE_URL}/transaction/initialize", json=data, headers=headers)
    return response.json()

def verify_payment(tx_ref):
    headers = {"Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"}
    response = requests.get(f"{CHAPA_BASE_URL}/transaction/verify/{tx_ref}", headers=headers)
    return response.json()