import json
import time

from django.http import JsonResponse
from broker.broker import bb
from broker import orderProcessor
from user.views import get_username_by_user_id
from broker.publicSettings import *


def test(request):
    return JsonResponse({
        'name': 'OTC'
    })


def get_buy_orders(request):
    return JsonResponse(bb.get_all_buy_orders(), safe=False)


def get_sell_orders(requset):
    return JsonResponse(bb.get_all_sell_orders(), safe=False)


def get_fragment_transactions(request):
    ret = {
        'mag': 'ok',
        'data': []
    }

    tfs = bb.get_all_fragment_transactions()

    for tf in tfs:
        buyer_id = bb.get_user_id_by_buy_order_id_and_commodity_name(tf.buy_order_id, tf.commodity_name)
        seller_id = bb.get_user_id_by_sell_order_id_and_commodity_name(tf.sell_order_id, tf.commodity_name)
        ret['data'].append({
            "buyOrderId": tf.buy_order_id,
            "buyerName": get_username_by_user_id(buyer_id),
            "buyerId": buyer_id,
            "sellOrderId": tf.sell_order_id,
            "sellerName": get_username_by_user_id(seller_id),
            "sellerId": seller_id,
            "qty": tf.qty,
            "price": tf.sold_price,
            "productName": tf.commodity_name,
            "time": tf.sold_time,
        })
    return JsonResponse(ret, safe=False)


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

    tfs = bb.get_fragment_transactions_by_user_id(user_id)

    ret = []
    for tf in tfs:
        buyer_id = bb.get_user_id_by_buy_order_id_and_commodity_name(tf.buy_order_id, tf.commodity_name)
        seller_id = bb.get_user_id_by_sell_order_id_and_commodity_name(tf.sell_order_id, tf.commodity_name)
        ret.append({
            "buyOrderId": tf.buy_order_id,
            "buyerName": get_username_by_user_id(buyer_id),
            "buyerId": buyer_id,
            "sellOrderId": tf.sell_order_id,
            "sellerName": get_username_by_user_id(seller_id),
            "sellerId": seller_id,
            "qty": tf.qty,
            "price": tf.sold_price,
            "productName": tf.commodity_name,
            "time": tf.sold_time,
        })
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
    for order in bb.get_all_buy_orders():
        ret['data'].append({
            "stockerId": order.buyer_id,
            "stockerName": get_username_by_user_id(order.buyer_id),
            "orderId": order.order_id,
            "orderDst": 'buy',
            "orderType": order.order_type,
            "qty": order.buy_vol,
            "price": order.price if order.order_type != 'market' else 0,
            "productName": order.commodity_name,
            "originVol": order.origin_vol,
            "orderIsDone": True if order.buy_vol == 0 else False
        })
    for order in bb.get_all_sell_orders():
        ret['data'].append({
            "stockerId": order.seller_id,
            "stockerName": get_username_by_user_id(order.buyer_id),
            "orderId": order.order_id,
            "orderDst": 'sell',
            "orderType": order.order_type,
            "qty": order.sell_vol,
            "price": order.price if order.order_type != 'market' else 0,
            "productName": order.commodity_name,
            "originVol": order.origin_vol,
            "orderIsDone": True if order.sell_vol == 0 else False
        })
    return JsonResponse(ret, safe=False)


def get_market_depth_by_commodity_name(request):
    info: dict = json.loads(request.body)
    commodity_name = info['name']

    buy_orders = []
    sell_orders = []
    for order in bb.get_all_buy_orders():
        if order.commodity_name == commodity_name and order.buy_vol != 0:
            buy_orders.append(order)
    for order in bb.get_all_sell_orders():
        if order.commodity_name == commodity_name and order.sell_vol != 0:
            sell_orders.append(order)

    buy_depth = {}
    sell_depth = {}
    for order in buy_orders:
        buy_depth[order.price] = buy_depth.get(order.price, 0) + order.buy_vol
    for order in sell_orders:
        sell_depth[order.price] = sell_depth.get(order.price, 0) + order.sell_vol
    buy_depth = [{'price': price, 'buy_vol': buy_depth[price]} for price in buy_depth]
    buy_depth.sort(key=lambda i: -i['price'])
    sell_depth = [{'price': price, 'sell_vol': sell_depth[price]} for price in sell_depth]
    sell_depth.sort(key=lambda i: i['price'])

    ret = {
        'sellDepth': [],
        'buyDepth': []
    }
    for i in range(len(buy_depth)):
        ret['buyDepth'].append({
            'price': buy_depth[i]['price'],
            'buyVol': buy_depth[i]['buy_vol'],
            'level': i + 1
        })
    for i in range(len(sell_depth)):
        ret['sellDepth'].append({
            'price': sell_depth[i]['price'],
            'sellVol': sell_depth[i]['sell_vol'],
            'level': i + 1
        })
    return JsonResponse({
        'msg': 'ok',
        'data': ret
    }, safe=False)


def get_price_trend(request):
    info: dict = json.loads(request.body)
    commodity_name = info['name']
    time_format = TIME_FORMAT
    begin_time = time.mktime(time.strptime(info['beginTime'], time_format))
    end_time = time.mktime(time.strptime(info['endTime'], time_format))
    tfs_info = []
    for tf in bb.get_all_fragment_transactions():
        if tf.commodity_name == commodity_name and begin_time <= time.mktime(
                time.strptime(tf.sold_time, time_format)) <= end_time:
            tfs_info.append({
                'price': tf.sold_price,
                'time': tf.sold_time,
                'qty': tf.qty
            })
    tfs_info.sort(key=lambda i: i['time'])
    return JsonResponse({
        'msg': "ok",
        'data': tfs_info
    }, safe=False)
