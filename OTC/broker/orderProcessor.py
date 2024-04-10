from broker.broker import Broker, BuyOrder, SellOrder, FragmentTransaction
import heapq

# 最小堆，适用于卖单（价格低的优先，如果价格相同，order_id小的优先）
sell_orders = []

# 最大堆，适用于买单（价格高的优先，如果价格相同，order_id小的优先）
# 注意：价格取负，但为了保持order_id的比较逻辑不变，我们不对order_id取负
buy_orders = []

last_price = 1000  # 全局变量，用于跟踪最后的交易价格


def add_sell_order(sell_heap, order):
    """
    向卖单堆中添加订单，卖单使用最小堆，优先处理价格低的订单。
    如果价格相同，则按照order_id的顺序处理。
    """
    heap_entry = (order.price, order.order_id, order)
    heapq.heappush(sell_heap, heap_entry)

def add_buy_order(buy_heap, order):
    """
    向买单堆中添加订单，买单使用最小堆模拟最大堆的行为，优先处理价格高的订单。
    为此，将价格取负。如果价格相同，则按照order_id的顺序处理。
    """
    heap_entry = (-order.price, order.order_id, order)
    heapq.heappush(buy_heap, heap_entry)

def peek_order(order_heap):
    # 查看堆顶元素（但不移除）
    if order_heap:
        _, _, order = order_heap[0]
        return order
    return None

def pop_order(order_heap):
    # 移除并返回堆顶元素
    if order_heap:
        _, _, order = heapq.heappop(order_heap)
        return order
    return None



def add_buy_order(broker: Broker,
                  buyer_id: int,
                  commodity_name: str,
                  buy_vol: int,
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
                   sell_vol: int,
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


def deal_new_buy_market_order(broker, order):
    global last_price

    # 将买单价格设置为float的最大值以确保与任何卖单都能匹配
    order.price = float('inf')

    while True:
        # 检查卖单堆是否为空
        if not sell_orders:
            # sell_orders为空，此处应写入数据库
            print("写入数据库")
            break  # 跳出循环

        _, _, top_sell_order = peek_order(sell_orders)

        # 市价买单逻辑，不需要检查order.order_type == 'market'，因为这是专门处理市价单的函数
        if order.buy_vol <= top_sell_order.sell_vol:
            # 完成交易，更新last_price
            top_sell_order.sell_vol -= order.buy_vol
            last_price = top_sell_order.price
            if top_sell_order.sell_vol == 0:
                pop_order(sell_orders)  # 如果卖单已完全成交，将其从堆中移除
            # 此处应写入数据库以更新交易细节
            break
        else:
            order.buy_vol -= top_sell_order.sell_vol
            last_price = top_sell_order.price
            pop_order(sell_orders)  # 移除已完全成交的卖单，继续处理剩余买单量
            # 此处应写入数据库以更新交易细节

        # 由于是市价买单，不会有价格不满足的情况，因此不需要处理买单是限价单的情况



def deal_new_sell_market_order(broker, order):
    global last_price

    # 将卖单价格设置为0以确保与任何买单都能匹配
    order.price = 0

    while True:
        if not buy_orders:
            print("写入数据库")  # 买单堆为空，此处应写入数据库
            break

        _, _, top_buy_order = peek_order(buy_orders)

        if order.sell_vol <= top_buy_order.buy_vol:
            # 完成交易，更新last_price
            top_buy_order.buy_vol -= order.sell_vol
            last_price = top_buy_order.price  # 更新最后成交价
            if top_buy_order.buy_vol == 0:
                pop_order(buy_orders)  # 如果买单已完全成交，将其从堆中移除
            # 此处应写入数据库以更新交易细节
            break
        else:
            order.sell_vol -= top_buy_order.buy_vol
            last_price = top_buy_order.price
            pop_order(buy_orders)  # 移除已完全成交的买单，继续处理剩余卖单量
            # 此处应写入数据库以更新交易细节

        # 对于市价卖单，无需担心价格不匹配的情况




def deal_new_buy_limit_order(broker, order):
    global last_price

    while True:
        # 检查卖单堆是否为空
        if not sell_orders:
            # sell_orders为空，此处应写入数据库
            # 这里是一个伪操作，实际应用中需要替换为数据库写入操作
            print("写入数据库")
            break  # 跳出循环

        # 获取堆顶的卖单
        _, _, top_sell_order = peek_order(sell_orders)

        if order.order_type == 'market':
            # 市价买单逻辑
            if order.buy_vol <= top_sell_order.sell_vol:
                # 完成交易，更新last_price
                top_sell_order.sell_vol -= order.buy_vol
                last_price = top_sell_order.price
                if top_sell_order.sell_vol == 0:
                    pop_order(sell_orders)  # 如果卖单已完全成交，将其从堆中移除
                #更新数据库
                break
            else:
                order.buy_vol -= top_sell_order.sell_vol
                last_price = top_sell_order.price
                pop_order(sell_orders)  # 移除已完全成交的卖单，继续处理剩余买单量
                # 这里也要写入order 数据库 更新两个委托单数据库
        elif order.order_type == 'limit' and order.price >= top_sell_order.price:
            # 限价买单逻辑
            if order.buy_vol <= top_sell_order.sell_vol:
                top_sell_order.sell_vol -= order.buy_vol
                last_price = top_sell_order.price# 更新价格
                if top_sell_order.sell_vol == 0:
                    pop_order(sell_orders)
                break
            else:
                order.buy_vol -= top_sell_order.sell_vol
                last_price = top_sell_order.price
                pop_order(sell_orders)
        else:
            # 如果买单是限价单，但价格不满足条件，结束循环
            
            add_buy_order(buy_orders, order)
            break


  


def deal_new_sell_limit_order(broker, order):
    global last_price

    # 尝试在买单堆中找到可以匹配的买单
    while True:
        if not buy_orders:
            # 如果买单堆为空，此时可能需要将卖单存储起来等待未来匹配
            # 这里假设你有一个按商品名称分类存储的卖单结构
            if broker.sell_orders.get(order.commodity_name, None) is None:
                broker.sell_orders[order.commodity_name] = []
            broker.sell_orders[order.commodity_name].append(order)
            print("没有匹配的买单，卖单已存储")
            break

        # 获取买单堆中的最高价买单
        _, _, top_buy_order = peek_order(buy_orders)

        if order.order_type == 'limit' and order.price <= top_buy_order.price:
            # 处理匹配逻辑
            # 此处省略详细匹配逻辑，包括成交量的计算和买卖双方订单的更新
            # 成功匹配后，需要更新last_price，并从买单堆中移除已完全成交的买单
            pass
        else:
            # 如果当前最高价买单的价格低于卖单的限价，说明没有匹配的买单
            if broker.sell_orders.get(order.commodity_name, None) is None:
                broker.sell_orders[order.commodity_name] = []
            broker.sell_orders[order.commodity_name].append(order)
            print("当前最高价买单的价格低于卖单的限价，卖单已存储")
            break


