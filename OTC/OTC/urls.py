"""
URL configuration for OTC project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from broker.views import (test,
                          get_buy_orders,
                          add_buy_order,
                          get_sell_orders,
                          add_sell_order,
                          get_fragment_transactions,
                          make_order,
                          get_finished_trade_list,
                          get_stocker_order_hist,
                          get_pending_orders,
                          get_market_depth_by_commodity_name,
                          get_price_trend,
                          cancel_order,
                          get_product_unit
                          )
from user.views import get_order_info_by_user_id, login

urlpatterns = [
    path('admin/', admin.site.urls),
    path('test/', test),
    path('get_buy_orders/', get_buy_orders),
    path('get_sell_orders/', get_sell_orders),
    path('get_fragment_transactions/', get_fragment_transactions),
    path('add_buy_order/', add_buy_order),
    path('add_sell_order/', add_sell_order),
    path('get_order_info_by_user_id/', get_order_info_by_user_id),

    path('api/makeOrder/', make_order),
    path('api/finishedTradeList/', get_finished_trade_list),
    path('api/stockerOrderHist/', get_stocker_order_hist),
    path('api/pendingOrderList/', get_pending_orders),
    path('api/allFinishedTradeList/', get_fragment_transactions),
    path('api/getMarketDepthByName/', get_market_depth_by_commodity_name),
    path('api/getPriceTrend/', get_price_trend),
    path('api/cancelOrder/', cancel_order),
    path('api/getProductInfo/', get_product_unit),
    path('api/login/', login),
]