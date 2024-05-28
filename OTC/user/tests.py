import requests
import json
import random
import time

url = 'http://127.0.0.1:8050/api/makeOrder/'

for i in range(1000):
    body = {
        'orderType': 'limit',
        'orderDst': 'buy',
        'qty': random.randint(80, 200),
        'userid': 1,
        'price': random.randint(450, 500),
        'productName': 'gold'
    }
    requests.post(url, data=json.dumps(body))

for i in range(1000):
    body = {
        'orderType': 'limit',
        'orderDst': 'sell',
        'qty': random.randint(80, 200),
        'userid': 2,
        'price': random.randint(500, 550),
        'productName': 'gold'
    }
    requests.post(url, data=json.dumps(body))

# for i in range(1000):
#     body = {
#         'orderType': 'limit',
#         'orderDst': 'buy',
#         'qty': random.randint(8, 20),
#         'userid': 1,
#         'price': random.randint(490, 520),
#         'productName': 'gold'
#     }
#     requests.post(url, data=json.dumps(body))
#     time.sleep(0.5)

