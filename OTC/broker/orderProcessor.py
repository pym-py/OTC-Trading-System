from broker import Broker, BuyOrder, SellOrder, FragmentTransaction

import heapq




# 最小堆，适用于卖单（价格低的优先，如果价格相同，order_id小的优先）
heap_sell_orders = {}

# 最大堆，适用于买单（价格高的优先，如果价格相同，order_id小的优先）
# 注意：价格取负，但为了保持order_id的比较逻辑不变，我们不对order_id取负
heap_buy_orders= {}





def heap_add_sell_order(product_name, order:SellOrder):
    """
    向卖单堆中添加订单，卖单使用最小堆，优先处理价格低的订单。
    如果价格相同，则按照order_id的顺序处理。
    """
    if product_name not in heap_sell_orders:
        heap_sell_orders[product_name] = []
    # heap_entry = (order.price, order.order_id, (order.price, order.order_id))
    heap_entry = (order.price, order.order_id, order)
    heapq.heappush(heap_sell_orders[product_name], heap_entry)

def heap_add_buy_order(product_name, order:BuyOrder):
    """
    向买单堆中添加订单，买单使用最小堆模拟最大堆的行为，优先处理价格高的订单。
    为此，将价格取负。如果价格相同，则按照order_id的顺序处理。
    """
    if product_name not in heap_buy_orders:
        heap_buy_orders[product_name] = []

    heap_entry = (-order.price, order.order_id, order)
    heapq.heappush(heap_buy_orders[product_name], heap_entry)

def max_limit_buy_price_(broker: Broker,commodity_name):
    max_price = 0.0

    if commodity_name in broker.buy_orders:
    # 遍历这个商品的所有订单
        for order_id, order in broker.buy_orders[commodity_name].items():
            if order.order_type == 'limit' and order.is_done != True:
                max_price = max(max_price,order.price)
            
    return max_price


def min_limit_sell_price_(broker: Broker,commodity_name):
    min_price = float('inf')

    if commodity_name in broker.sell_orders:
    # 遍历这个商品的所有订单
        for order_id, order in broker.sell_orders[commodity_name].items():
            if order.order_type == 'limit' and order.is_done != True:
                min_price = min(min_price,order.price)
            
    return min_price

# def peek_order(order_heap):
#     # 查看堆顶元素（但不移除）
#     if order_heap:
#         _, _, order = order_heap[0]
#         return order
#     return None
#
def pop_order(product_name,order_heap):
    # 移除并返回堆顶元素
    if product_name not in order_heap:
        return None
    if order_heap[product_name]:
        _, _, order = heapq.heappop(order_heap[product_name])
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
        add_stop_buy_order(broker,buy_order)





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
        add_stop_sell_order(broker,sell_order)
    




    # 检查order_name是否已经在字典中



def add_stop_buy_order(broker:Broker,order:BuyOrder):
    if order.commodity_name not in broker.buy_orders:
        broker.buy_orders[order.commodity_name] = {}

    broker.buy_orders[order.commodity_name][order.order_id] = order

    if order.price <= min_limit_sell_price_(broker,order.commodity_name):
        deal_new_buy_market_order(order)
    else:
        heap_add_sell_order("stop",order)


def add_stop_sell_order(broker:Broker,order:SellOrder):
    if order.commodity_name not in broker.sell_orders:
        broker.sell_orders[order.commodity_name] = {}

    broker.sell_orders[order.commodity_name][order.order_id] = order

    if max_limit_buy_price_(broker,order.commodity_name) == 0.0:
        heap_add_buy_order("stop",order)
        return 
    if order.price >= max_limit_buy_price_(broker,order.commodity_name):
        deal_new_sell_market_order(order)
    else:
        heap_add_buy_order("stop",order)

def deal_new_buy_cancel_order(broker :Broker, commodity_name, order_id):
    broker.buy_orders[commodity_name][order_id].order_type = 'cancel'
def deal_new_sell_cancel_order(broker, commodity_name, order_id):
    broker.sell_orders[commodity_name][order_id].order_type = 'cancel'


def deal_new_buy_market_order(broker, order:BuyOrder):
  
    if order.commodity_name not in broker.buy_orders:
        broker.buy_orders[order.commodity_name] = {}
    broker.buy_orders[order.commodity_name][order.order_id] = order


    # 将买单价格设置为float的最大值以确保与任何卖单都能匹配
    order.price = float('inf')

    while True:
        # 检查卖单堆是否为空
        
        if order.commodity_name not in heap_sell_orders:
            heap_sell_orders[order.commodity_name] = []
        if not heap_sell_orders[order.commodity_name]:
            if order.buy_vol != 0:
                heap_add_buy_order(order.commodity_name, order)
            break  

        min_limit_sell_price = min_limit_sell_price_(broker,order.commodity_name) 
        top_sell_order = pop_order(order.commodity_name,heap_sell_orders)

        if broker.sell_orders[top_sell_order.commodity_name][top_sell_order.order_id].order_type == 'cancel':
            continue
        
        
        # 市价买单逻辑，不需要检查order.order_type == 'market'，因为这是专门处理市价单的函数
        if order.buy_vol <= top_sell_order.sell_vol:
            
            quan = order.buy_vol
            top_sell_order.sell_vol -= order.buy_vol
            top_sell_order: SellOrder
            
                
            if top_sell_order.sell_vol != 0:
                heap_add_sell_order(order.commodity_name, top_sell_order)
            else:
                top_sell_order.is_done = True

            order.buy_vol = 0
            order.is_done = True

            

            tran = FragmentTransaction(order.commodity_name,top_sell_order.order_id,order.order_id,quan, min_limit_sell_price)
            broker.add_fragment_transaction(tran)
            broker.sell_orders[top_sell_order.commodity_name][top_sell_order.order_id] = top_sell_order
            
            broker.buy_orders[order.commodity_name][order.order_id] = order

            
            while True:
                buy_stop_order:BuyOrder = pop_order('stop',heap_sell_orders)
                if buy_stop_order is None:
                    break
                if buy_stop_order.price <= min_limit_sell_price_(broker,order.commodity_name):
                    deal_new_buy_market_order(broker,buy_stop_order)
                else:
                    heap_add_sell_order('stop',buy_stop_order)
                    break
            
            while True:
                
                sell_stop_order = pop_order('stop',heap_buy_orders)
                if sell_stop_order is None:
                    break
                if sell_stop_order.price >= max_limit_buy_price_(broker,order.commodity_name):
                    deal_new_sell_market_order(broker,sell_stop_order)
                else:
                    heap_add_buy_order('stop',sell_stop_order)
                    break
            # 此处应写入数据库以更新交易细节
            break
        else:
            quan = top_sell_order.sell_vol
            order.buy_vol -= top_sell_order.sell_vol
            top_sell_order.sell_vol = 0
            top_sell_order.is_done = True

            

            broker.sell_orders[top_sell_order.commodity_name][top_sell_order.order_id] = top_sell_order
            broker.buy_orders[order.commodity_name][order.order_id] = order

            
            tran = FragmentTransaction(order.commodity_name, top_sell_order.order_id, order.order_id, quan,
                                       min_limit_sell_price)
            broker.add_fragment_transaction(tran)
            # 移除已完全成交的卖单，继续处理剩余买单量
            # 此处应写入数据库以更新交易细节
            
            while True:
                buy_stop_order = pop_order('stop',heap_sell_orders)
                if buy_stop_order is None:
                    break
                if buy_stop_order.price <= min_limit_sell_price_(broker,order.commodity_name):
                    deal_new_buy_market_order(broker,buy_stop_order)
                else:
                    heap_add_sell_order('stop',buy_stop_order)
                    break
            
            while True:
                sell_stop_order = pop_order('stop',heap_buy_orders)
                if sell_stop_order is None:
                    break
                if sell_stop_order.price >= max_limit_buy_price_(broker,order.commodity_name):
                    deal_new_sell_market_order(broker,sell_stop_order)
                else:
                    heap_add_buy_order('stop',sell_stop_order)
                    break
        # 由于是市价买单，不会有价格不满足的情况，因此不需要处理买单是限价单的情况



def deal_new_sell_market_order(broker, order:SellOrder):
    

    if order.commodity_name not in broker.sell_orders:
        broker.sell_orders[order.commodity_name] = {}


    broker.sell_orders[order.commodity_name][order.order_id] = order


    # 将买单价格设置为float的最大值以确保与任何卖单都能匹配
    order.price = -1

    while True:
        # 检查卖单堆是否为空
        if order.commodity_name not in heap_buy_orders:
            heap_buy_orders[order.commodity_name] = []
        if not heap_buy_orders[order.commodity_name]:
            # sell_orders为空，此处应写入数据库
            if order.sell_vol != 0:
                heap_add_sell_order(order.commodity_name, order)
            break  # 跳出循环
        max_limit_buy_price = max_limit_buy_price_(broker,order.commodity_name)
        top_buy_order = pop_order(order.commodity_name,heap_buy_orders)

        if broker.buy_orders[top_buy_order.commodity_name][top_buy_order.order_id].order_type == 'cancel':
            continue

        # 市价买单逻辑，不需要检查order.order_type == 'market'，因为这是专门处理市价单的函数
        if order.sell_vol <= top_buy_order.buy_vol:
            
            quan = order.sell_vol
            top_buy_order.buy_vol -= order.sell_vol
            top_buy_order: BuyOrder
            

            if top_buy_order.buy_vol != 0:
                heap_add_buy_order(order.commodity_name, top_buy_order)
            else:
                top_buy_order.is_done = True

            
            order.sell_vol = 0
            order.is_done = True

            broker.buy_orders[top_buy_order.commodity_name][top_buy_order.order_id] = top_buy_order
            broker.sell_orders[order.commodity_name][order.order_id] = order
            tran = FragmentTransaction(order.commodity_name,order.order_id,top_buy_order.order_id,quan, max_limit_buy_price)
            broker.add_fragment_transaction(tran)

            
            while True:
                buy_stop_order = pop_order('stop',heap_sell_orders)
                if buy_stop_order is None:
                    break
                if buy_stop_order.price <= min_limit_sell_price_(broker,order.commodity_name):
                    deal_new_buy_market_order(broker,buy_stop_order)
                else:
                    heap_add_sell_order('stop',buy_stop_order)
                    break
            
            while True:
                sell_stop_order = pop_order('stop',heap_buy_orders)
                if sell_stop_order is None:
                    break
                if sell_stop_order.price >= max_limit_buy_price_(broker,order.commodity_name):
                    deal_new_sell_market_order(broker,sell_stop_order)
                else:
                    heap_add_buy_order('stop',sell_stop_order)
                    break

            # 此处应写入数据库以更新交易细节
            break
        else:
            quan = top_buy_order.buy_vol
            order.sell_vol -= top_buy_order.buy_vol
            top_buy_order.buy_vol = 0
            top_buy_order.is_done = True

            

            broker.buy_orders[top_buy_order.commodity_name][top_buy_order.order_id] = top_buy_order
            broker.sell_orders[order.commodity_name][order.order_id] = order

            tran = FragmentTransaction(order.commodity_name, order.order_id, top_buy_order.order_id, quan,
                                       max_limit_buy_price)
            broker.add_fragment_transaction(tran)
            # 移除已完全成交的卖单，继续处理剩余买单量
            # 此处应写入数据库以更新交易细节
            
            while True:
                buy_stop_order = pop_order('stop',heap_sell_orders)
                if buy_stop_order is None:
                    break
                if buy_stop_order.price <= min_limit_sell_price_(broker,order.commodity_name):
                    deal_new_buy_market_order(broker,buy_stop_order)
                else:
                    heap_add_sell_order('stop',buy_stop_order)
                    break
            
            while True:
                sell_stop_order = pop_order('stop',heap_buy_orders)
                if sell_stop_order is None:
                    break
                if sell_stop_order.price >= max_limit_buy_price_(broker,order.commodity_name):
                    deal_new_sell_market_order(broker,sell_stop_order)
                else:
                    heap_add_buy_order('stop',sell_stop_order)
                    break
        # 由于是市价买单，不会有价格不满足的情况，因此不需要处理买单是限价单的情况




def deal_new_buy_limit_order(broker, order:BuyOrder):
    
    if order.commodity_name not in broker.buy_orders:
        broker.buy_orders[order.commodity_name] = {}


    broker.buy_orders[order.commodity_name][order.order_id] = order

    while True:
        # 检查卖单堆是否为空
        if order.commodity_name not in heap_sell_orders:
            heap_sell_orders[order.commodity_name] = []
        if not heap_sell_orders[order.commodity_name]:
        
            if order.buy_vol != 0:
                heap_add_buy_order(order.commodity_name, order)
            break  # 跳出循环

        # 获取堆顶的卖单
        top_sell_order:SellOrder
        min_limit_sell_price = min_limit_sell_price_(broker,order.commodity_name)
        top_sell_order = pop_order(order.commodity_name,heap_sell_orders)

        if broker.sell_orders[top_sell_order.commodity_name][top_sell_order.order_id].order_type == 'cancel':
            continue
        
        if top_sell_order.order_type == 'market' or top_sell_order.order_type == 'stop':
            # 市价买单逻辑
            if order.buy_vol <= top_sell_order.sell_vol:
                quan = order.buy_vol
                
               
                top_sell_order.sell_vol -= order.buy_vol
                order.buy_vol = 0
                order.is_done = True

                if top_sell_order.sell_vol !=0:
                    heap_add_sell_order(order.commodity_name,top_sell_order)
                else:
                    top_sell_order.is_done = True

                broker.buy_orders[order.commodity_name][order.order_id] = order
                broker.sell_orders[top_sell_order.commodity_name][top_sell_order.order_id] = top_sell_order
                

                tran = FragmentTransaction(order.commodity_name, top_sell_order.order_id, order.order_id,
                                           quan,
                                           min_limit_sell_price)
                broker.add_fragment_transaction(tran)

                
                while True:
                    buy_stop_order = pop_order('stop',heap_sell_orders)
                    if buy_stop_order is None:
                        break
                    if buy_stop_order.price <= min_limit_sell_price_(broker,order.commodity_name):
                        deal_new_buy_market_order(broker,buy_stop_order)
                    else:
                        heap_add_sell_order('stop',buy_stop_order)
                        break
            
                while True:
                    sell_stop_order = pop_order('stop',heap_buy_orders)
                    if sell_stop_order is None:
                        break
                    if sell_stop_order.price >= max_limit_buy_price_(broker,order.commodity_name):
                        deal_new_sell_market_order(broker,sell_stop_order)
                    else:
                        heap_add_buy_order('stop',sell_stop_order)
                        break
                break
            else:
                quan = top_sell_order.sell_vol
                order.buy_vol -= top_sell_order.sell_vol
                top_sell_order.sell_vol = 0
                top_sell_order.is_done = True
                broker.buy_orders[order.commodity_name][order.order_id] = order
                broker.sell_orders[top_sell_order.commodity_name][top_sell_order.order_id] = top_sell_order

    

                if order.buy_vol == 0:
                    order.is_done = True


                broker.buy_orders[order.commodity_name][order.order_id] = order
                broker.sell_orders[top_sell_order.commodity_name][top_sell_order.order_id] = top_sell_order
                    
                
                
                tran = FragmentTransaction(order.commodity_name, top_sell_order.order_id, order.order_id,
                                           quan,
                                           min_limit_sell_price)
                broker.add_fragment_transaction(tran)

                
                while True:
                    buy_stop_order = pop_order('stop',heap_sell_orders)
                    if buy_stop_order is None:
                        break
                    if buy_stop_order.price <= min_limit_sell_price_(broker,order.commodity_name):
                        deal_new_buy_market_order(broker,buy_stop_order)
                    else:
                        heap_add_sell_order('stop',buy_stop_order)
                        break
            
                while True:
                    sell_stop_order = pop_order('stop',heap_buy_orders)
                    if sell_stop_order is None:
                        break
                    if sell_stop_order.price >= max_limit_buy_price_(broker,order.commodity_name):
                        deal_new_sell_market_order(broker,sell_stop_order)
                    else:
                        heap_add_buy_order('stop',sell_stop_order)
                        break                
                continue
                 # 移除已完全成交的卖单，继续处理剩余买单量
                # 这里也要写入order 数据库 更新两个委托单数据库
        elif order.price >= top_sell_order.price:
            # 限价买单逻辑
            if order.buy_vol <= top_sell_order.sell_vol:
                quan = order.buy_vol
            
                order.buy_vol = 0
                order.is_done = True
                
                top_sell_order.sell_vol -= quan
                
                if top_sell_order.sell_vol != 0:
                    heap_add_sell_order(order.commodity_name, top_sell_order)
                else:
                    top_sell_order.is_done = True

                broker.buy_orders[order.commodity_name][order.order_id] = order
                broker.sell_orders[top_sell_order.commodity_name][top_sell_order.order_id] = top_sell_order
                

                tran = FragmentTransaction(order.commodity_name, top_sell_order.order_id, order.order_id,
                                           quan,
                                           (min_limit_sell_price+max_limit_buy_price_(broker,order.commodity_name))/2)
                broker.add_fragment_transaction(tran)
                
                while True:
                    buy_stop_order = pop_order('stop',heap_sell_orders)
                    if buy_stop_order is None:
                        break
                    if buy_stop_order.price <= min_limit_sell_price_(broker,order.commodity_name):
                        deal_new_buy_market_order(broker,buy_stop_order)
                    else:
                        heap_add_sell_order('stop',buy_stop_order)
                        break
            
                while True:
                    sell_stop_order = pop_order('stop',heap_buy_orders)
                    if sell_stop_order is None:
                        break
                    if sell_stop_order.price >= max_limit_buy_price_(broker,order.commodity_name):
                        deal_new_sell_market_order(broker,sell_stop_order)
                    else:
                        heap_add_buy_order('stop',sell_stop_order)
                        break                
                
                break
            else:
                quan = top_sell_order.sell_vol
                order.buy_vol -= top_sell_order.sell_vol
                top_sell_order.sell_vol = 0
                top_sell_order.is_done = True
                broker.buy_orders[order.commodity_name][order.order_id] = order
                broker.sell_orders[top_sell_order.commodity_name][top_sell_order.order_id] = top_sell_order

                

                tran = FragmentTransaction(order.commodity_name, top_sell_order.order_id, order.order_id,
                                           quan,
                                           (min_limit_sell_price+max_limit_buy_price_(broker,order.commodity_name))/2)
                broker.add_fragment_transaction(tran)
               
                while True:
                    buy_stop_order = pop_order('stop',heap_sell_orders)
                    if buy_stop_order is None:
                        break
                    if buy_stop_order.price <= min_limit_sell_price_(broker,order.commodity_name):
                        deal_new_buy_market_order(broker,buy_stop_order)
                    else:
                        heap_add_sell_order('stop',buy_stop_order)
                        break
            
                while True:
                    sell_stop_order = pop_order('stop',heap_buy_orders)
                    if sell_stop_order is None:
                        break
                    if sell_stop_order .price>= max_limit_buy_price_(broker,order.commodity_name):
                        deal_new_sell_market_order(broker,sell_stop_order)
                    else:
                        heap_add_buy_order('stop',sell_stop_order)
                        break 
                continue
        else:
            
            

            heap_add_buy_order(order.commodity_name,order)
            heap_add_sell_order(order.commodity_name,top_sell_order)
            break


  


def deal_new_sell_limit_order(broker, order:SellOrder):
  

    if order.commodity_name not in broker.sell_orders:
        broker.sell_orders[order.commodity_name] = {}


    broker.sell_orders[order.commodity_name][order.order_id] = order

    while True:
        # 检查买单堆是否为空
        if order.commodity_name not in heap_buy_orders:
            heap_buy_orders[order.commodity_name] = []
        if not heap_buy_orders[order.commodity_name]:
            # buy_orders为空，此处应写入数据库
            # 这里是一个伪操作，实际应用中需要替换为数据库写入操作
            if order.sell_vol != 0:
                heap_add_sell_order(order.commodity_name, order)
            break  # 跳出循环

        # 获取堆顶的买单
        max_limit_buy_price = max_limit_buy_price_(broker,order.commodity_name)
        top_buy_order = pop_order(order.commodity_name,heap_buy_orders)

        if broker.buy_orders[top_buy_order.commodity_name][top_buy_order.order_id].order_type == 'cancel':
            continue

        if top_buy_order.order_type == 'market' or top_buy_order.order_type == 'stop':
            # 市价卖单逻辑
            if order.sell_vol <= top_buy_order.buy_vol:
             
             
                quan = order.sell_vol
                top_buy_order.buy_vol -= order.sell_vol
                order.sell_vol = 0
                order.is_done = True

                if top_buy_order.buy_vol != 0:
                    heap_add_buy_order(order.commodity_name, top_buy_order)
                else:
                    top_buy_order.is_done = True


                broker.sell_orders[order.commodity_name][order.order_id] = order
                broker.buy_orders[top_buy_order.commodity_name][top_buy_order.order_id] = top_buy_order
                
                top_buy_order:BuyOrder
                tran = FragmentTransaction(order.commodity_name, order.order_id, top_buy_order.order_id, quan,
                                           max_limit_buy_price)
                broker.add_fragment_transaction(tran)
                min_limit_sell = min_limit_sell_price_(broker,order.commodity_name)
                max_limit_buy = max_limit_buy_price_(broker,order.commodity_name)
                while True:
                    buy_stop_order = pop_order('stop',heap_sell_orders)
                    if buy_stop_order is None:
                        break
                    if buy_stop_order.price <= min_limit_sell_price_(broker,order.commodity_name):
                        deal_new_buy_market_order(broker,buy_stop_order)
                    else:
                        heap_add_sell_order('stop',buy_stop_order)
                        break
            
                while True:
                    sell_stop_order = pop_order('stop',heap_buy_orders)
                    if sell_stop_order is None:
                        break
                    if sell_stop_order.price >= max_limit_buy_price_(broker,order.commodity_name):
                        deal_new_sell_market_order(broker,sell_stop_order)
                    else:
                        heap_add_buy_order('stop',sell_stop_order)
                        break 
                break
            else:
                quan = top_buy_order.buy_vol
                order.sell_vol -= top_buy_order.buy_vol
                top_buy_order.buy_vol = 0
                top_buy_order.is_done = True
                broker.sell_orders[order.commodity_name][order.order_id] = order
                broker.buy_orders[top_buy_order.commodity_name][top_buy_order.order_id] = top_buy_order

              

                if order.sell_vol == 0:
                    order.is_done = True
                    

                tran = FragmentTransaction(order.commodity_name, order.order_id, top_buy_order.order_id, quan,
                                           max_limit_buy_price)
                broker.add_fragment_transaction(tran)
               
                while True:
                    buy_stop_order = pop_order('stop',heap_sell_orders)
                    if buy_stop_order is None:
                        break
                    if buy_stop_order.price <= min_limit_sell_price_(broker,order.commodity_name):
                        deal_new_buy_market_order(broker,buy_stop_order)
                    else:
                        heap_add_sell_order('stop',buy_stop_order)
                        break
            
                while True:
                    sell_stop_order = pop_order('stop',heap_buy_orders)
                    if sell_stop_order is None:
                        break
                    if sell_stop_order.price >= max_limit_buy_price_(broker,order.commodity_name):
                        deal_new_sell_market_order(broker,sell_stop_order)
                    else:
                        heap_add_buy_order('stop',sell_stop_order)
                        break 
                continue
                # 移除已完全成交的买单，继续处理剩余卖单量
                # 这里也要写入order数据库，更新两个委托单数据库
        elif order.price <= top_buy_order.price:
            # 限价卖单逻辑
            if order.sell_vol <= top_buy_order.buy_vol:
                quan = order.sell_vol
                order.sell_vol = 0
                order.is_done = True
                
                
                top_buy_order.buy_vol -= quan
                
                if top_buy_order.buy_vol != 0:
                    heap_add_buy_order(order.commodity_name,top_buy_order)
                else:
                    top_buy_order.is_done = True

                broker.sell_orders[order.commodity_name][order.order_id] = order
                broker.buy_orders[top_buy_order.commodity_name][top_buy_order.order_id] = top_buy_order
                

                tran = FragmentTransaction(order.commodity_name, order.order_id, top_buy_order.order_id, quan,
                                           min_limit_sell_price_(broker,order.commodity_name) + max_limit_buy_price / 2)
                broker.add_fragment_transaction(tran)
              
                while True:
                    buy_stop_order = pop_order('stop',heap_sell_orders)
                    if buy_stop_order is None:
                        break
                    if buy_stop_order.price <= min_limit_sell_price_(broker,order.commodity_name):
                        deal_new_buy_market_order(broker,buy_stop_order)
                    else:
                        heap_add_sell_order('stop',buy_stop_order)
                        break
            
                while True:
                    sell_stop_order = pop_order('stop',heap_buy_orders)
                    if sell_stop_order is None:
                        break
                    if sell_stop_order.price >= max_limit_buy_price_(broker,order.commodity_name):
                        deal_new_sell_market_order(broker,sell_stop_order)
                    else:
                        heap_add_buy_order('stop',sell_stop_order)
                        break 
                break
            else:
                quan = top_buy_order.buy_vol
                order.sell_vol -= top_buy_order.buy_vol
                top_buy_order.buy_vol = 0
                top_buy_order.is_done = True
                broker.sell_orders[order.commodity_name][order.order_id] = order
                broker.buy_orders[top_buy_order.commodity_name][top_buy_order.order_id] = top_buy_order

               
                tran = FragmentTransaction(order.commodity_name, order.order_id, top_buy_order.order_id, quan,
                                           (min_limit_sell_price_(broker,order.commodity_name) + max_limit_buy_price) / 2)
                broker.add_fragment_transaction(tran)
                
                while True:
                    buy_stop_order = pop_order('stop',heap_sell_orders)
                    if buy_stop_order is None:
                        break
                    if buy_stop_order.price <= min_limit_sell_price_(broker,order.commodity_name):
                        deal_new_buy_market_order(broker,buy_stop_order)
                    else:
                        heap_add_sell_order('stop',buy_stop_order)
                        break
            
                while True:
                    sell_stop_order = pop_order('stop',heap_buy_orders)
                    if sell_stop_order is None:
                        break
                    if sell_stop_order.price >= max_limit_buy_price_(broker,order.commodity_name):
                        deal_new_sell_market_order(broker,sell_stop_order)
                    else:
                        heap_add_buy_order('stop',sell_stop_order)
                        break 
                continue
        else:
            # 如果卖单是限价单，但价格不满足条件，结束循环

            heap_add_sell_order(order.commodity_name, order)
            heap_add_buy_order(order.commodity_name,top_buy_order)
            break


