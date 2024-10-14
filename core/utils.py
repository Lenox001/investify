# utils.py
import requests
from django.conf import settings

def get_mpesa_access_token():
    consumer_key = settings.MPESA_CONSUMER_KEY
    consumer_secret = settings.MPESA_CONSUMER_SECRET
    api_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'

    response = requests.get(api_url, auth=(consumer_key, consumer_secret))
    access_token = response.json()['access_token']

    return access_token
