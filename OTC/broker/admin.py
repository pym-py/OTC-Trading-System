from django.contrib import admin

# Register your models here.
from broker.models import *

admin.site.register(BuyOrder)
admin.site.register(SellOrder)
admin.site.register(FragmentTransaction)
