from broker.broker import Broker, BuyOrder, SellOrder, FragmentTransaction


def add_buy_order(broker: Broker,
                  buyer_id: int,
                  commodity_name: str,
                  buy_vol: float,
                  price: float,
                  order_type: str):
    order_id = broker.buy_order_id.get(commodity_name, 1)
    broker.buy_order_id[commodity_name] = broker.buy_order_id.get(commodity_name, 1) + 1
    buy_order = BuyOrder(order_id, commodity_name, buy_vol, price, buyer_id, order_type)
    if order_type == 'market':
        deal_new_buy_market_order(broker, buy_order)
    elif order_type == 'limit':
        deal_new_buy_limit_order(broker, buy_order)
    elif order_type == 'stop':
        pass
    elif order_type == 'cancel':
        pass


def add_sell_order(broker: Broker,
                   seller_id: int,
                   commodity_name: str,
                   sell_vol: float,
                   price: float,
                   order_type: str):
    order_id = broker.sell_order_id.get(commodity_name, 1)
    broker.sell_order_id[commodity_name] = broker.sell_order_id.get(commodity_name, 1) + 1
    sell_order = SellOrder(order_id, commodity_name, sell_vol, price, seller_id, order_type)
    if order_type == 'market':
        deal_new_sell_market_order(broker, sell_order)
    elif order_type == 'limit':
        deal_new_sell_limit_order(broker, sell_order)
    elif order_type == 'stop':
        pass
    elif order_type == 'cancel':
        pass


def deal_new_buy_market_order(broker: Broker, order: BuyOrder):
    commodity_name = order.commodity_name
    if broker.buy_orders.get(commodity_name, -1) == -1:
        broker.buy_orders[commodity_name] = [order]
    else:
        broker.buy_orders[commodity_name].append(order)


def deal_new_sell_market_order(broker: Broker, order: SellOrder):
    commodity_name = order.commodity_name
    if broker.sell_orders.get(commodity_name, -1) == -1:
        broker.sell_orders[commodity_name] = [order]
    else:
        broker.sell_orders[commodity_name].append(order)


def deal_new_buy_limit_order(broker: Broker, order: BuyOrder):
    commodity_name = order.commodity_name
    if broker.buy_orders.get(commodity_name, -1) == -1:
        broker.buy_orders[commodity_name] = [order]
    else:
        broker.buy_orders[commodity_name].append(order)


def deal_new_sell_limit_order(broker: Broker, order: SellOrder):
    commodity_name = order.commodity_name
    if broker.sell_orders.get(commodity_name, -1) == -1:
        broker.sell_orders[commodity_name] = [order]
    else:
        broker.sell_orders[commodity_name].append(order)


