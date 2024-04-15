from broker import Broker, BuyOrder, SellOrder, FragmentTransaction

import heapq

# 最小堆，适用于卖单（价格低的优先，如果价格相同，order_id小的优先）
heap_sell_orders = []

# 最大堆，适用于买单（价格高的优先，如果价格相同，order_id小的优先）
# 注意：价格取负，但为了保持order_id的比较逻辑不变，我们不对order_id取负
heap_buy_orders = []

last_price = 1000.0  # 全局变量，用于跟踪最后的交易价格


def heap_add_sell_order(sell_heap, order:SellOrder):
    """
    向卖单堆中添加订单，卖单使用最小堆，优先处理价格低的订单。
    如果价格相同，则按照order_id的顺序处理。
    """
    heap_entry = (order.price, order.order_id, order)
    heapq.heappush(sell_heap, heap_entry)

def heap_add_buy_order(buy_heap, order:BuyOrder):
    """
    向买单堆中添加订单，买单使用最小堆模拟最大堆的行为，优先处理价格高的订单。
    为此，将价格取负。如果价格相同，则按照order_id的顺序处理。
    """
    heap_entry = (-order.price, order.order_id, order)
    heapq.heappush(buy_heap, heap_entry)

# def peek_order(order_heap):
#     # 查看堆顶元素（但不移除）
#     if order_heap:
#         _, _, order = order_heap[0]
#         return order
#     return None
#
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


def deal_new_buy_market_order(broker, order:BuyOrder):
    global last_price
    if order.commodity_name not in broker.buy_orders:
        broker.buy_orders[order.commodity_name] = {}


    broker.buy_orders[order.commodity_name][order.order_id] = order


    # 将买单价格设置为float的最大值以确保与任何卖单都能匹配
    order.price = float('inf')

    while True:
        # 检查卖单堆是否为空
        if not heap_sell_orders:
            # sell_orders为空，此处应写入数据库
            if order.buy_vol != 0:
                heap_add_buy_order(heap_buy_orders, order)
            break  # 跳出循环

        top_sell_order = pop_order(heap_sell_orders)

        # 市价买单逻辑，不需要检查order.order_type == 'market'，因为这是专门处理市价单的函数
        if order.buy_vol <= top_sell_order.sell_vol:
            # 完成交易，更新last_price
            quan = order.buy_vol
            top_sell_order.sell_vol -= order.buy_vol
            top_sell_order: SellOrder
            if top_sell_order.order_type != 'market':
                last_price = top_sell_order.price


            


            if top_sell_order.sell_vol != 0:
                heap_add_sell_order(heap_sell_orders, top_sell_order)
            else:
                top_sell_order.is_done = True

            order.buy_vol = 0
            order.is_done = True

            tran = FragmentTransaction(order.commodity_name,top_sell_order.order_id,order.order_id,quan, last_price)
            broker.add_fragment_transaction(tran)
            broker.sell_orders[top_sell_order.commodity_name][top_sell_order.order_id] = top_sell_order
            
            broker.buy_orders[order.commodity_name][order.order_id] = order

            # 此处应写入数据库以更新交易细节
            break
        else:
            quan = top_sell_order.sell_vol
            order.buy_vol -= top_sell_order.sell_vol
            top_sell_order.sell_vol = 0
            top_sell_order.is_done = True

            if top_sell_order.order_type != 'market':
                last_price = top_sell_order.price

            broker.sell_orders[top_sell_order.commodity_name][top_sell_order.order_id] = top_sell_order
            broker.buy_orders[order.commodity_name][order.order_id] = order

            tran = FragmentTransaction(order.commodity_name, top_sell_order.order_id, order.order_id, quan,
                                       last_price)
            broker.add_fragment_transaction(tran)
            # 移除已完全成交的卖单，继续处理剩余买单量
            # 此处应写入数据库以更新交易细节

        # 由于是市价买单，不会有价格不满足的情况，因此不需要处理买单是限价单的情况



def deal_new_sell_market_order(broker, order:SellOrder):
    global last_price

    if order.commodity_name not in broker.sell_orders:
        broker.sell_orders[order.commodity_name] = {}


    broker.sell_orders[order.commodity_name][order.order_id] = order


    # 将买单价格设置为float的最大值以确保与任何卖单都能匹配
    order.price = -1

    while True:
        # 检查卖单堆是否为空
        if not heap_buy_orders:
            # sell_orders为空，此处应写入数据库
            if order.sell_vol != 0:
                heap_add_sell_order(heap_sell_orders, order)
            break  # 跳出循环

        top_buy_order = pop_order(heap_buy_orders)

        # 市价买单逻辑，不需要检查order.order_type == 'market'，因为这是专门处理市价单的函数
        if order.sell_vol <= top_buy_order.buy_vol:
            # 完成交易，更新last_price
            quan = order.sell_vol
            top_buy_order.buy_vol -= order.sell_vol
            top_buy_order: BuyOrder
            if top_buy_order.order_type != 'market':
                last_price = top_buy_order.price

            if top_buy_order.buy_vol != 0:
                heap_add_buy_order(heap_buy_orders, top_buy_order)
            else:
                top_buy_order.is_done = True

            
            order.sell_vol = 0
            order.is_done = True

            broker.buy_orders[top_buy_order.commodity_name][top_buy_order.order_id] = top_buy_order
            broker.sell_orders[order.commodity_name][order.order_id] = order
            tran = FragmentTransaction(order.commodity_name,order.order_id,top_buy_order.order_id,quan, last_price)
            broker.add_fragment_transaction(tran)



            # 此处应写入数据库以更新交易细节
            break
        else:
            quan = top_buy_order.buy_vol
            order.sell_vol -= top_buy_order.buy_vol
            top_buy_order.buy_vol = 0
            top_buy_order.is_done = True

            if top_buy_order.order_type != 'market':
                last_price = top_buy_order.price

            broker.buy_orders[top_buy_order.commodity_name][top_buy_order.order_id] = top_buy_order
            broker.sell_orders[order.commodity_name][order.order_id] = order

            tran = FragmentTransaction(order.commodity_name, order.order_id, top_buy_order.order_id, quan,
                                       last_price)
            broker.add_fragment_transaction(tran)
            # 移除已完全成交的卖单，继续处理剩余买单量
            # 此处应写入数据库以更新交易细节

        # 由于是市价买单，不会有价格不满足的情况，因此不需要处理买单是限价单的情况




def deal_new_buy_limit_order(broker, order:BuyOrder):
    global last_price
    if order.commodity_name not in broker.buy_orders:
        broker.buy_orders[order.commodity_name] = {}


    broker.buy_orders[order.commodity_name][order.order_id] = order

    while True:
        # 检查卖单堆是否为空
        if not heap_sell_orders:
        
            if order.buy_vol != 0:
                heap_add_buy_order(heap_buy_orders, order)
            break  # 跳出循环

        # 获取堆顶的卖单
        top_sell_order:SellOrder
        top_sell_order = pop_order(heap_sell_orders)

        if top_sell_order.order_type == 'market':
            # 市价买单逻辑
            if order.buy_vol <= top_sell_order.sell_vol:
                quan = order.buy_vol
                
                last_price = order.price
                top_sell_order.sell_vol -= order.buy_vol
                order.buy_vol = 0
                order.is_done = True

                if top_sell_order.sell_vol !=0:
                    heap_add_sell_order(heap_sell_orders,top_sell_order)
                else:
                    top_sell_order.is_done = True

                broker.buy_orders[order.commodity_name][order.order_id] = order
                broker.sell_orders[top_sell_order.commodity_name][top_sell_order.order_id] = top_sell_order
                

                tran = FragmentTransaction(order.commodity_name, top_sell_order.order_id, order.order_id,
                                           quan,
                                           last_price)
                broker.add_fragment_transaction(tran)
                break
            else:
                quan = top_sell_order.sell_vol
                order.buy_vol -= top_sell_order.sell_vol
                top_sell_order.sell_vol = 0
                top_sell_order.is_done = True
                broker.buy_orders[order.commodity_name][order.order_id] = order
                broker.sell_orders[top_sell_order.commodity_name][top_sell_order.order_id] = top_sell_order

                last_price = order.price

                if order.buy_vol == 0:
                    order.is_done = True


                broker.buy_orders[order.commodity_name][order.order_id] = order
                broker.sell_orders[top_sell_order.commodity_name][top_sell_order.order_id] = top_sell_order
                    
                
                
                tran = FragmentTransaction(order.commodity_name, top_sell_order.order_id, order.order_id,
                                           quan,
                                           last_price)
                broker.add_fragment_transaction(tran)
                continue
                 # 移除已完全成交的卖单，继续处理剩余买单量
                # 这里也要写入order 数据库 更新两个委托单数据库
        elif top_sell_order.order_type == 'limit' and order.price >= top_sell_order.price:
            # 限价买单逻辑
            if order.buy_vol <= top_sell_order.sell_vol:
                quan = order.buy_vol
                # 完成交易，更新last_price
                order.buy_vol = 0
                order.is_done = True
                last_price = (order.price + top_sell_order.price) / 2
                top_sell_order.sell_vol -= quan
                
                if top_sell_order.sell_vol != 0:
                    heap_add_sell_order(heap_sell_orders, top_sell_order)
                else:
                    top_sell_order.is_done = True

                broker.buy_orders[order.commodity_name][order.order_id] = order
                broker.sell_orders[top_sell_order.commodity_name][top_sell_order.order_id] = top_sell_order
                

                tran = FragmentTransaction(order.commodity_name, top_sell_order.order_id, order.order_id,
                                           quan,
                                           last_price)
                broker.add_fragment_transaction(tran)
                break
            else:
                quan = top_sell_order.sell_vol
                order.buy_vol -= top_sell_order.sell_vol
                top_sell_order.sell_vol = 0
                top_sell_order.is_done = True
                broker.buy_orders[order.commodity_name][order.order_id] = order
                broker.sell_orders[top_sell_order.commodity_name][top_sell_order.order_id] = top_sell_order

                last_price = (order.price + top_sell_order.price) / 2

                tran = FragmentTransaction(order.commodity_name, top_sell_order.order_id, order.order_id,
                                           quan,
                                           last_price)
                broker.add_fragment_transaction(tran)
                continue
        else:
            
            

            heap_add_buy_order(heap_buy_orders,order)
            heap_add_sell_order(heap_sell_orders,top_sell_order)
            break


  


def deal_new_sell_limit_order(broker, order:SellOrder):
    global last_price

    if order.commodity_name not in broker.sell_orders:
        broker.sell_orders[order.commodity_name] = {}


    broker.sell_orders[order.commodity_name][order.order_id] = order

    while True:
        # 检查买单堆是否为空
        if not heap_buy_orders:
            # buy_orders为空，此处应写入数据库
            # 这里是一个伪操作，实际应用中需要替换为数据库写入操作
            if order.sell_vol != 0:
                heap_add_sell_order(heap_sell_orders, order)
            break  # 跳出循环

        # 获取堆顶的买单
        top_buy_order = pop_order(heap_buy_orders)

        if top_buy_order.order_type == 'market':
            # 市价卖单逻辑
            if order.sell_vol <= top_buy_order.buy_vol:
                # 完成交易，更新last_price
                last_price = order.price
                quan = order.sell_vol
                top_buy_order.buy_vol -= order.sell_vol
                order.sell_vol = 0
                order.is_done = True

                if top_buy_order.buy_vol != 0:
                    heap_add_buy_order(heap_buy_orders, top_buy_order)
                else:
                    top_buy_order.is_done = True


                broker.sell_orders[order.commodity_name][order.order_id] = order
                broker.buy_orders[top_buy_order.commodity_name][top_buy_order.order_id] = top_buy_order
                
                top_buy_order:BuyOrder
                tran = FragmentTransaction(order.commodity_name, order.order_id, top_buy_order.order_id, quan,
                                           last_price)
                broker.add_fragment_transaction(tran)
                break
            else:
                quan = top_buy_order.buy_vol
                order.sell_vol -= top_buy_order.buy_vol
                top_buy_order.buy_vol = 0
                top_buy_order.is_done = True
                broker.sell_orders[order.commodity_name][order.order_id] = order
                broker.buy_orders[top_buy_order.commodity_name][top_buy_order.order_id] = top_buy_order

                last_price = order.price

                if order.sell_vol == 0:
                    order.is_done = True
                    

                tran = FragmentTransaction(order.commodity_name, order.order_id, top_buy_order.order_id, quan,
                                           last_price)
                broker.add_fragment_transaction(tran)
                continue
                # 移除已完全成交的买单，继续处理剩余卖单量
                # 这里也要写入order数据库，更新两个委托单数据库
        elif top_buy_order.order_type == 'limit' and order.price <= top_buy_order.price:
            # 限价卖单逻辑
            if order.sell_vol <= top_buy_order.buy_vol:
                quan = order.sell_vol
                order.sell_vol = 0
                order.is_done = True
                last_price = (order.price + top_buy_order.price) / 2
                
                top_buy_order.buy_vol -= quan
                
                if top_buy_order.buy_vol != 0:
                    heap_add_buy_order(heap_buy_orders,top_buy_order)
                else:
                    top_buy_order.is_done = True

                broker.sell_orders[order.commodity_name][order.order_id] = order
                broker.buy_orders[top_buy_order.commodity_name][top_buy_order.order_id] = top_buy_order
                

                tran = FragmentTransaction(order.commodity_name, order.order_id, top_buy_order.order_id, quan,
                                           last_price)
                broker.add_fragment_transaction(tran)
                break
            else:
                quan = top_buy_order.buy_vol
                order.sell_vol -= top_buy_order.buy_vol
                top_buy_order.buy_vol = 0
                top_buy_order.is_done = True
                broker.sell_orders[order.commodity_name][order.order_id] = order
                broker.buy_orders[top_buy_order.commodity_name][top_buy_order.order_id] = top_buy_order

                last_price = (order.price + top_buy_order.price) / 2

                tran = FragmentTransaction(order.commodity_name, order.order_id, top_buy_order.order_id, quan,
                                           last_price)
                broker.add_fragment_transaction(tran)
                continue
        else:
            # 如果卖单是限价单，但价格不满足条件，结束循环

            heap_add_sell_order(heap_sell_orders, order)
            heap_add_buy_order(heap_buy_orders,top_buy_order)
            break



