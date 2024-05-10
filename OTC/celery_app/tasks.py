from __future__ import absolute_import
from celery import shared_task
import time
from broker.models import *


@shared_task
def ce_test():
    for i in range(10):
        print(i)
        time.sleep(1)
    return 1


@shared_task
def create_buy_order(
        order_id: int,
        commodity_name: str,
        buy_vol: int,
        price: float,
        buyer_id: int,
        order_type: str,
        is_done: bool = False
):
    order_obj = BuyOrder(order_id=order_id,
                         commodity_name=commodity_name,
                         buy_vol=buy_vol,
                         price=price,
                         buyer_id=buyer_id,
                         order_type=order_type,
                         is_done=is_done)
    order_obj.save()


@shared_task
def create_sell_order(
        order_id: int,
        commodity_name: str,
        sell_vol: int,
        price: float,
        seller_id: int,
        order_type: str,
        is_done: bool = False
):
    order_obj = SellOrder(order_id=order_id,
                          commodity_name=commodity_name,
                          sell_vol=sell_vol,
                          price=price,
                          seller_id=seller_id,
                          order_type=order_type,
                          is_done=is_done)
    order_obj.save()


@shared_task
def create_fragment_transaction(
        commodity_name: str,
        sell_order_id: int,
        buy_order_id: int,
        qty: int,
        sold_price: float,
):
    ft_obj = FragmentTransaction(commodity_name=commodity_name,
                                 sell_order_id=sell_order_id,
                                 buy_order_id=buy_order_id,
                                 qty=qty,
                                 sold_price=sold_price)
    ft_obj.save()


@shared_task
def modify_buy_order(
        order_id: int,
        commodity_name: str,
        buy_vol: int = None,
        price: float = None,
        buyer_id: int = None,
        order_type: str = None,
        is_done: bool = None
):
    order_obj = BuyOrder.objects.get(order_id=order_id, commodity_name=commodity_name)
    if buy_vol is not None:
        order_obj.buy_vol = buy_vol
    if price is not None:
        order_obj.buy_vol = price
    if buyer_id is not None:
        order_obj.buyer_id = buyer_id
    if price is not None:
        order_obj.order_type = order_type
    if price is not None:
        order_obj.is_done = is_done
    order_obj.save()


@shared_task
def modify_sell_order(
        order_id: int,
        commodity_name: str,
        sell_vol: int = None,
        price: float = None,
        seller_id: int = None,
        order_type: str = None,
        is_done: bool = None
):
    order_obj = SellOrder.objects.get(order_id=order_id, commodity_name=commodity_name)
    if sell_vol is not None:
        order_obj.sell_vol = sell_vol
    if price is not None:
        order_obj.price = price
    if seller_id is not None:
        order_obj.seller_id = seller_id
    if price is not None:
        order_obj.order_type = order_type
    if price is not None:
        order_obj.is_done = is_done
    order_obj.save()
