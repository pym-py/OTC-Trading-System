"""
buy表(order_id, commodity_name, buy_vol, price, buyer_id, order_type, is_done)
sell表(order_id, commodity_name, sell_vol, price, seller_id, order_type, is_done)
fragment_transaction(sell_order_id, buy_order_id, qty, sold_price, sold_time)
company(cid, name)
"""
import time


class BuyOrder:
    def __init__(self,
                 order_id: int,
                 commodity_name: str,
                 buy_vol: float,
                 price: float,  # market order 设置为-1
                 buyer_id: int,
                 order_type: str,
                 is_done: bool = False):
        self.order_id = order_id
        self.commodity_name = commodity_name
        self.buy_vol = buy_vol
        self.price = price
        self.buyer_id = buyer_id
        self.order_type = order_type
        self.is_done = is_done

    def get_info(self):
        return {
            'order_id': self.order_id,
            'commodity_name': self.commodity_name,
            'buy_vol': self.buy_vol,
            'price': self.price,
            'buyer_id': self.buyer_id,
            'order_type': self.order_type,
            'is_done': self.is_done
        }


class SellOrder:
    def __init__(self,
                 order_id: int,
                 commodity_name: str,
                 sell_vol: float,
                 price: float,  # market order 设置为-1
                 seller_id: int,
                 order_type: str,
                 is_done: bool = False):
        self.order_id = order_id
        self.commodity_name = commodity_name
        self.sell_vol = sell_vol
        self.price = price
        self.seller_id = seller_id
        self.order_type = order_type
        self.is_done = is_done

    def get_info(self):
        return {
            'order_id': self.order_id,
            'commodity_name': self.commodity_name,
            'buy_vol': self.sell_vol,
            'price': self.price,
            'buyer_id': self.seller_id,
            'order_type': self.order_type,
            'is_done': self.is_done
        }


class FragmentTransaction:
    def __init__(self, commodity_name,sell_order_id, buy_order_id, qty, sold_price):
        self.commodity_name = commodity_name
        self.sell_order_id = sell_order_id
        self.buy_order_id = buy_order_id
        self.qty = qty
        self.sold_price = sold_price
        self.sold_time = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())  # 24小时制

    def get_json_info(self):
        return {
            'sell_id': self.sell_order_id,
            'buy_id': self.buy_order_id,
            'qty': self.qty,
            'sold_price': self.sold_price,
            'sold_time': self.sold_time
        }


class Broker:
    def __init__(self, name):
        self.name = name
        self.company_list = []  # [{'id': 1, 'name': 'A'}, ]
        self.sell_orders = {}
        self.buy_orders = {}
        self.fragment_trans = {}
        self.buy_order_id = {}
        self.sell_order_id = {}

    def get_company_list(self):
        ret = []
        for c in self.company_list:
            ret.append(c)
        return ret

    def add_fragment_transaction(self, ft: FragmentTransaction):
        commodity_name = ft.commodity_name
        if self.fragment_trans.get(commodity_name, -1) == -1:
            self.fragment_trans[commodity_name] = [ft]
        else:
            self.fragment_trans[commodity_name].append(ft)

    def get_buy_orders(self):
        ret = []
        for commodity in self.buy_orders:
            for order in self.buy_orders[commodity]:
                ret.append(order.get_info())
        return ret

    def get_sell_orders(self):
        ret = []
        for commodity in self.sell_orders:
            for order in self.sell_orders[commodity]:
                ret.append(order.get_info())
        return ret

    def get_fragment_transactions(self):
        ret = []
        for commodity in self.fragment_trans:
            for order in self.fragment_trans[commodity]:
                ret.append(order.get_json_info())
        return ret

    # def add_buy_order(self,
    #                   buyer_id: int,
    #                   commodity_name: str,
    #                   buy_vol: float,
    #                   price: float,
    #                   order_type: str):
    #     self.buy_orders.append(buy_order)
    #     # TODO 处理新的order
    #
    # def add_sell_order(self,
    #                    seller_id: int,
    #                    commodity_name: str,
    #                    sell_vol: float,
    #                    price: float,
    #                    order_type: str):
    #     order_id = self.sell_order_id
    #     self.sell_order_id += 1
    #     sell_order = SellOrder(order_id, commodity_name, sell_vol, price, seller_id, order_type)
    #     self.sell_orders.append(sell_order)
    #     # TODO 处理新的order
        # vol = sell_order.sell_vol
        # for order in self.buy_orders:
        #     if order.order_type == 'limit':
        #         buy_id = order.order_id
        #         sell_id = sell_order.order_id
        #         sold_price = order.price
        #         if order.buy_vol >= vol:
        #             qty = vol
        #             order.buy_vol -= vol
        #             sell_order.sell_vol = 0
        #             sell_order.is_done = True
        #         else:
        #             qty = order.buy_vol
        #             vol -= order.buy_vol
        #             order.buy_vol = 0
        #             order.is_done = True
        #         fragment_transaction = FragmentTransaction(sell_id, buy_id, qty, sold_price)
        #         self.add_fragment_transaction(fragment_transaction)
        #         break




bb = Broker('gold')
bb.company_list.append({'id': 1, 'name': "A"})
bb.company_list.append(({'id': 2, 'name': 'B'}))

