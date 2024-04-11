#from django.test import TestCase

# Create your tests here.

from broker import Broker  # 假设Broker类在broker.py文件中
from broker import SellOrder
from broker import BuyOrder  # 假设SellOrder类在sell_order.py文件中
from orderProcessor import add_sell_order
from orderProcessor import add_buy_order
  # 假设add_sell_order函数在order_functions.py文件中


my_broker = Broker("Example Broker")
'''
# ================================================order1
seller_id = 3
commodity_name = "gold"
sell_vol = 5000

price = 350
order_type = "limit"

# 调用add_sell_order函数
add_sell_order(broker=my_broker,
               seller_id=seller_id,
               commodity_name=commodity_name,
               sell_vol=sell_vol,
               price=price,
               order_type=order_type)

# order2============================================
# 定义订单信息
seller_id = 5
commodity_name = "gold"
sell_vol = 10000
price = 340
order_type = "limit"

# 假设my_broker是之前已经创建好的Broker实例

# 调用add_sell_order函数来添加卖单
add_sell_order(broker=my_broker,
               seller_id=seller_id,
               commodity_name=commodity_name,
               sell_vol=sell_vol,
               price=price,
               order_type=order_type)


#========================================order3

seller_id = 2  # 这里假设company_id对应于seller_id
commodity_name = "gold"
sell_vol = 7000
price = 345
order_type = "limit"

add_sell_order(broker=my_broker,
               seller_id=seller_id,
               commodity_name=commodity_name,
               sell_vol=sell_vol,
               price=price,
               order_type=order_type)




# order4 ============================================

seller_id = 1
commodity_name = "gold"
sell_vol = 8000
price = 345
order_type = "limit"

# 假设my_broker是之前已经创建好的Broker实例

# 调用add_sell_order函数来添加卖单
add_sell_order(broker=my_broker,
               seller_id=seller_id,
               commodity_name=commodity_name,
               sell_vol=sell_vol,
               price=price,
               order_type=order_type)

#=================================order5
buyer_id = 4
commodity_name = 'gold'
buy_vol = 4000
price = 0
order_type = 'market'

add_buy_order(broker=my_broker,
               buyer_id=buyer_id,
               commodity_name=commodity_name,
               buy_vol=buy_vol,
               price=price,
               order_type=order_type)

# =================================order6

buyer_id = 4
commodity_name = 'gold'
buy_vol = 10000
price = 0
order_type = 'market'

add_buy_order(broker=my_broker,
               buyer_id=buyer_id,
               commodity_name=commodity_name,
               buy_vol=buy_vol,
               price=price,
               order_type=order_type)


#order7=======================
buyer_id = 4
commodity_name = 'gold'
buy_vol = 10000
price = 340
order_type = 'limit'

add_buy_order(broker=my_broker,
               buyer_id=buyer_id,
               commodity_name=commodity_name,
               buy_vol=buy_vol,
               price=price,
               order_type=order_type)


# order8 ==============================

buyer_id = 4
commodity_name = 'gold'
buy_vol = 10000
price = 330
order_type = 'limit'

add_buy_order(broker=my_broker,
               buyer_id=buyer_id,
               commodity_name=commodity_name,
               buy_vol=buy_vol,
               price=price,
               order_type=order_type)


# order8 ==============================

buyer_id = 4
commodity_name = 'gold'
buy_vol = 150000
price = 360
order_type = 'limit'

add_buy_order(broker=my_broker,
               buyer_id=buyer_id,
               commodity_name=commodity_name,
               buy_vol=buy_vol,
               price=price,
               order_type=order_type)

#================================order 9

'''
seller_id = 5
commodity_name = "gold"
sell_vol = 10000
price = 340
order_type = "limit"

# 假设my_broker是之前已经创建好的Broker实例

# 调用add_sell_order函数来添加卖单
add_sell_order(broker=my_broker,
               seller_id=seller_id,
               commodity_name=commodity_name,
               sell_vol=sell_vol,
               price=price,
               order_type=order_type)


buyer_id = 4
commodity_name = 'gold'
buy_vol = 15000
price = 360
order_type = 'limit'

add_buy_order(broker=my_broker,
               buyer_id=buyer_id,
               commodity_name=commodity_name,
               buy_vol=buy_vol,
               price=price,
               order_type=order_type)



#print(my_broker.get_buy_orders())
print(my_broker.get_buy_orders())

print(my_broker.get_sell_orders())
print(my_broker.get_fragment_transactions())


        

