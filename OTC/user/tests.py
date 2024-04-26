from django.test import TestCase

# Create your tests here.
import requests
import json
url = 'http://127.0.0.1:8050/api/makeOrder/'


# print(requests.post(url, data=json.dumps(body)))
for i in range(10):
    body = {
        'orderType': 'limit',
        'orderDst': 'buy',
        'qty': 80,
        'userid': 1,
        'price': i,
        'productName': 'gold'
    }
    requests.post(url, data=json.dumps(body))
