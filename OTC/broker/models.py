from django.db import models


class FragmentTransaction(models.Model):
    commodity_name = models.CharField(max_length=100)
    sell_order_id = models.IntegerField()
    buy_order_id = models.IntegerField()
    qty = models.IntegerField()
    sold_price = models.FloatField()
    sold_time = models.DateTimeField(auto_now=True)


class BuyOrder(models.Model):
    order_id = models.IntegerField()
    commodity_name = models.CharField(max_length=100)
    buy_vol = models.IntegerField()
    price = models.FloatField()
    buyer_id = models.IntegerField()
    order_type = models.CharField(max_length=100)
    is_done = models.BooleanField()


class SellOrder(models.Model):
    order_id = models.IntegerField()
    commodity_name = models.CharField(max_length=100)
    sell_vol = models.IntegerField()
    price = models.FloatField()
    seller_id = models.IntegerField()
    order_type = models.CharField(max_length=100)
    is_done = models.BooleanField()
