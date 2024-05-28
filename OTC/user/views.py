import json
from django.http import JsonResponse
from broker.broker import bb
# Create your views here.

user_for_test = {
    'test_user': {
        'id': 1,
        'password': '123',
        'type': 'company'
    },
    'test_user2': {
        'id': 2,
        'password': '123',
        'type': 'company'
    },
    'test_user3': {
        'id': 3,
        'password': "123",
        'type': 'company'
    }
}


def get_username_by_user_id(user_id):
    for username in user_for_test:
        if user_for_test[username]['id'] == user_id:
            return username
    return ""


def login(request):
    user_info: dict = json.loads(request.body)
    username = user_info['username']
    password = user_info['password']
    user_type = user_info['usertype']
    ret = {
        'status': "",
        'data': {
            'userid': -1
        }

    }
    if user_type == 'company':
        if user_for_test.get(username, {}) == {}:
            ret['status'] = '用户不存在'
        elif user_for_test.get(username)['password'] != password:
            ret['status'] = '密码错误'
        else:
            ret['status'] = 'ok'
            ret['data']['userid'] = user_for_test.get(username)['id']
    else:
        ret['status'] = 'ok'
        ret['data']['userid'] = 1
    return JsonResponse(ret)


def get_order_info_by_user_id(request):
    user_info: dict = json.loads(request.body)
    user_id = user_info['userid']
    user_name = get_username_by_user_id(user_id)
    ret = {
        'msg': 'ok',
        'data': []
    }
    all_sell_orders = bb.get_all_sell_orders()
    all_buy_orders = bb.get_all_buy_orders()
    for order in all_sell_orders:
        if order['seller_id'] == user_id:
            ret['data'].append({
                "stockerName": user_name,
                "orderId": order['order_id'],
                "orderDst": 'sell',
                "orderType": order['order_type'],
                "qty": order['sell_vol'],
                "price": order['price'],
                "productName": order['commodity_name'],
            })
    for order in all_buy_orders:
        if order['buyer_id'] == user_id:
            ret['data'].append({
                "stockerName": user_name,
                "orderId": order['order_id'],
                "orderDst": 'buy',
                "orderType": order['order_type'],
                "qty": order['buy_vol'],
                "price": order['price'],
                "productName": order['commodity_name'],
            })
    return JsonResponse(ret)

