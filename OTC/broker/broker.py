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
                 buy_vol: int,
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
        self.origin_vol = buy_vol

    def get_json_info(self):
        return {
            'order_id': self.order_id,
            'commodity_name': self.commodity_name,
            'buy_vol': self.buy_vol,
            'price': self.price if self.order_type != 'market' else 0,
            'buyer_id': self.buyer_id,
            'order_type': self.order_type,
            'is_done': self.is_done,
            'origin_vol': self.origin_vol
        }


class SellOrder:
    def __init__(self,
                 order_id: int,
                 commodity_name: str,
                 sell_vol: int,
                 price: float,  # market order 设置为-1
                 seller_id: int,
                 order_type: str,
                 is_done: bool = False):
        self.order_id = order_id
        self.commodity_name = commodity_name
        self.sell_vol = sell_vol
        self.price = price if order_type != 'market' else 0
        self.seller_id = seller_id
        self.order_type = order_type
        self.is_done = is_done
        self.origin_vol = sell_vol

    def get_json_info(self):
        return {
            'order_id': self.order_id,
            'commodity_name': self.commodity_name,
            'sell_vol': self.sell_vol,
            'price': self.price,
            'seller_id': self.seller_id,
            'order_type': self.order_type,
            'is_done': self.is_done,
            'origin_vol': self.origin_vol
        }


class FragmentTransaction:
    def __init__(self, commodity_name, sell_order_id, buy_order_id, qty, sold_price):
        self.commodity_name = commodity_name
        self.sell_order_id = sell_order_id
        self.buy_order_id = buy_order_id
        self.qty = qty
        self.sold_price = sold_price
        self.sold_time = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())  # 24小时制

    def get_json_info(self):
        return {
            'commodity_name': self.commodity_name,
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
                ret.append(order.get_json_info())
        return ret

    def get_sell_orders(self):
        ret = []
        for commodity in self.sell_orders:
            for order in self.sell_orders[commodity]:
                ret.append(order.get_json_info())
        return ret

    def get_fragment_transactions(self):
        ret = []
        for commodity in self.fragment_trans:
            for order in self.fragment_trans[commodity]:
                ret.append(order.get_json_info())
        return ret

    def get_name_by_id(self, id):
        from user.views import user_for_test
        for user in user_for_test:
            if user_for_test[user]['id'] == id:
                return user

    def get_id_by_buy_order_id(self, order_id):
        for commodity_name in self.buy_orders:
            for _, order in self.buy_orders[commodity_name].items():
                if order.order_id == order_id:
                    return order.buyer_id

    def get_id_by_sell_order_id(self, order_id):
        for commodity_name in self.sell_orders:
            for _, order in self.sell_orders[commodity_name].items():
                if order.order_id == order_id:
                    return order.seller_id

    def get_all_fragment_transactions(self):
        ret = []
        for commodity_name in self.fragment_trans:
            for tf in self.fragment_trans[commodity_name]:
                info = tf.get_json_info()
                buyer_id = self.get_id_by_buy_order_id(info['buy_id'])
                seller_id = self.get_id_by_sell_order_id(info['sell_id'])
                ret.append({
                    "buyOrderId": info['buy_id'],
                    "buyerName": self.get_name_by_id(buyer_id),
                    "buyerId": buyer_id,
                    "sellOrderId": info['sell_id'],
                    "sellerName": self.get_name_by_id(seller_id),
                    "sellerId": seller_id,
                    "qty": info['qty'],
                    "price": info['sold_price'],
                    "productName": info['commodity_name'],
                    "time": info['sold_time'],
                })
        return ret

    def get_fragment_transactions_by_id(self, id):
        sell_orders = []
        buy_orders = []
        for commodity_name in self.buy_orders:
            for _, order in self.buy_orders[commodity_name].items():
                if order.buyer_id == id:
                    buy_orders.append(order)
        for commodity_name in self.sell_orders:
            for _, order in self.sell_orders[commodity_name].items():
                if order.seller_id == id:
                    sell_orders.append(order)
        if len(sell_orders) > 0:
            print(sell_orders[0].get_json_info())
        if len(buy_orders) > 0:
            print(buy_orders[0].get_json_info())
        tfs = []
        for commodity_name in self.fragment_trans:
            for tf in self.fragment_trans[commodity_name]:
                for order in sell_orders:
                    if tf.sell_order_id == order.order_id:
                        tfs.append(tf)
                for order in buy_orders:
                    if tf.buy_order_id == order.order_id:
                        tfs.append(tf)
        print(len(tfs))
        ret = []
        for tf in tfs:
            info = tf.get_json_info()
            buyer_id = self.get_id_by_buy_order_id(info['buy_id'])
            seller_id = self.get_id_by_sell_order_id(info['sell_id'])
            ret.append({
                "buyOrderId": info['buy_id'],
                "buyerName": self.get_name_by_id(buyer_id),
                "buyerId": buyer_id,
                "sellOrderId": info['sell_id'],
                "sellerName": self.get_name_by_id(seller_id),
                "sellerId": seller_id,
                "qty": info['qty'],
                "price": info['sold_price'],
                "productName": info['commodity_name'],
                "time": info['sold_time'],
            })
        return ret

    def get_all_orders(self):
        ret = []
        for commodity in self.buy_orders:
            for _, order in self.buy_orders[commodity].items():
                ret.append({
                    "company_id": order.buyer_id,
                    "orderId": order.order_id,
                    "orderDst": 'buy',
                    "orderType": order.order_type,
                    "qty": order.buy_vol,
                    "price": order.price ,
                    "productName": order.commodity_name,
                    "orderIsDone": order.is_done,
                    "originVol": order.origin_vol
                })
        for commodity in self.sell_orders:
            for _, order in self.sell_orders[commodity].items():
                ret.append({
                    "company_id": order.seller_id,
                    "orderId": order.order_id,
                    "orderDst": 'sell',
                    "orderType": order.order_type,
                    "qty": order.sell_vol,
                    "price": order.price,
                    "productName": order.commodity_name,
                    "orderIsDone": order.is_done,
                    "originVol": order.origin_vol
                })
        return ret


bb = Broker('gold')
# bb.company_list.append({'id': 1, 'name': "A"})
# bb.company_list.append(({'id': 2, 'name': 'B'}))
# bb.buy_orders['gold'].append(BuyOrder(1, 'gold', 10, 100, 1, 'market'))
# bb.buy_orders['gold'].append(BuyOrder(2, 'gold', 20, 200, 1, 'limit'))
# bb.sell_orders['gold'].append(SellOrder(1, 'gold', 33, 100, 1, 'limit'))
# bb.sell_orders['gold'].append(SellOrder(2, 'gold', 35, 300, 2, 'market'))
# bb.sell_orders['oil'].append(SellOrder(1, 'oil', 100, 1000, 2, 'limit'))
# bb.add_fragment_transaction(FragmentTransaction('gold'