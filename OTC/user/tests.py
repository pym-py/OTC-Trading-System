from django.test import TestCase

# Create your tests here.
import requests
import json
import random

url = 'http://127.0.0.1:8050/api/makeOrder/'

for i in range(1000):
    body = {
        'orderType': 'limit',
        'orderDst': 'buy',
        'qty': random.randint(80, 1000),
        'userid': 1,
        'price': random.randint(1000, 1010),
        'productName': 'gold'
    }
    requests.post(url, data=json.dumps(body))

for i in range(1000):
    body = {
        'orderType': 'limit',
        'orderDst': 'sell',
        'qty': random.randint(80, 1000),
        'userid': 2,
        'price': random.randint(1000, 1010),
        'productName': 'gold'
    }
    requests.post(url, data=json.dumps(body))


