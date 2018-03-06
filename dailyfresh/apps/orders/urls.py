from django.conf.urls import url
from orders.views import *

patterns = [
    # 订单确认
    url(r"^place$", PlaceOrderView.as_view(), name="place"),
    # 提交订单
    url(r"^commit$", CommitOrderView.as_view(), name="commit"),
    # 订单信息页面
    url(r'^(?P<page>\d+)$', UserOrdersView.as_view(), name='info'),
    # 支付 : http://127.0.0.1:8000/orders/pay (需要传入的数据都在post请求的请求体中)
    url(r'^pay$', PayView.as_view(), name='pay'),
    # 查询订单 "http://127.0.0.1:8000/orders/checkpay?order_id="+order_id
    url(r"^checkpay$", CheckPayView.as_view(), name="checkpay"),
    # 评价信息
    url('^comment/(?P<order_id>\d+)$', CommentView.as_view(), name="comment")

]