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
    return JsonResponse({
        'msg': 'ok',
        'data': bb.get_all_fragment_transactions(),
    }, safe=False)


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


def make_order(request):
    order_info: dict = json.loads(request.body)
    order_type = order_info['orderType']
    is_buy_order = order_info['orderDst'] == 'buy'
    vol = order_info['qty']
    company_id = order_info['userid']
    price = order_info['price']
    commodity_name = order_info['productName']
    if is_buy_order:
        orderProcessor.add_buy_order(bb, company_id, commodity_name, vol, price, order_type)
    else:
        orderProcessor.add_sell_order(bb, company_id, commodity_name, vol, price, order_type)

    return JsonResponse({
        "msg": "ok"
    }, safe=False)


def get_finished_trade_list(request):
    user_info: dict = json.loads(request.body)
    user_id = user_info['userid']
    ret = bb.get_fragment_transactions_by_id(user_id)
    return JsonResponse({
        'msg': 'ok',
        'data': ret
    }, safe=False)


def get_stocker_order_hist(request):
    user_info: dict = json.loads(request.body)
    user_id = user_info['userid']
    ret = []
    for commodity in bb.buy_orders:
        for _, order in bb.buy_orders[commodity].items():
            if order.buyer_id == user_id:
                ret.append({
                    "company_id": order.buyer_id,
                    "orderId": order.order_id,
                    "orderDst": 'buy',
                    "orderType": order.order_type,
                    "qty": order.buy_vol,
                    "price": order.price if order.order_type != 'market' else 0,
                    "productName": order.commodity_name,
                    "orderIsDone": order.is_done,
                    "originVol": order.origin_vol
                })
    for commodity in bb.sell_orders:
        for _, order in bb.sell_orders[commodity].items():
            if order.seller_id == user_id:
                ret.append({
                    "company_id": order.seller_id,
                    "orderId": order.order_id,
                    "orderDst": 'sell',
                    "orderType": order.order_type,
                    "qty": order.sell_vol,
                    "price": order.price if order.order_type != 'market' else 0,
                    "productName": order.commodity_name,
                    "orderIsDone": order.is_done,
                    "originVol": order.origin_vol
                })
    return JsonResponse({
        'msg': "ok",
        'data': ret
    }, safe=False)


def get_pending_orders(request):
    user_info: dict = json.loads(request.body)
    user_id = user_info['userid']
    ret = {
        'msg': "ok",
        'data': []
    }
    for order in bb.get_all_orders():
        ret['data'].append({
            "stockerId": order['company_id'],
            "stockerName": bb.get_name_by_id(order['company_id']),
            "orderId": order['orderId'],
            "orderDst": order['orderDst'],
            "orderType": order['orderType'],
            "qty": order['qty'],
            "price": order['price'] if order['orderType'] != 'market' else 0,
            "productName": order['productName'],
            "originVol": order['originVol'],
            "orderIsDone": True if order['qty'] == 0 else False
         })
    return JsonResponse(ret, safe=False)




