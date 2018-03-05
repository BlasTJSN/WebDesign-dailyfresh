from django.conf.urls import url
from orders.views import *

patterns = [
    # 订单确认
    url(r"^place$", PlaceOrderView.as_view(), name="place"),
    # 提交订单
    url(r"^commit$", CommitOrderView.as_view(), name="commit"),
    # 订单信息页面
    url(r'^(?P<page>\d+)$', UserOrdersView.as_view(), name='info')
]