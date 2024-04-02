import json
from django.http import JsonResponse
from broker.broker import bb
from broker import orderProcessor


def test(request):
    return JsonResponse({
        'name': 'OTC'
    })


def get_buy_orders(request):
    return JsonResponse(bb.get_buy_orders(), safe=False)


def get_sell_orders(requset):
    return JsonResponse(bb.get_sell_orders(), safe=False)


def get_fragment_transactions(request):
    return JsonResponse(bb.get_fragment_transactions(), safe=False)


def add_buy_order(request):
    ret = {}
    order_info: dict = json.loads(request.body)
    company_id = order_info['company_id']
    commodity_name = order_info['commodity_name']
    buy_vol = order_info['buy_vol']
    price = order_info['price']
    order_type = order_info['order_type']

    orderProcessor.add_buy_order(bb, company_id, commodity_name, buy_vol, price, order_type)

    ret['code'] = 1
    ret['msg'] = 'success'
    return JsonResponse(ret)


def add_sell_order(request):
    ret = {}
    order_info: dict = json.loads(request.body)
    company_id = order_info['company_id']
    commodity_name = order_info['commodity_name']
    sell_vol = order_info['sell_vol']
    price = order_info['price']
    order_type = order_info['order_type']

    orderProcessor.add_sell_order(bb, company_id, commodity_name, sell_vol, price, order_type)

    ret['code'] = 1
    ret['msg'] = 'success'
    return JsonResponse(ret)
