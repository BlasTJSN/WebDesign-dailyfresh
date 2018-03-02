from django.conf.urls import url
from cart.views import *

urlpatterns = [
    # 添加购物车
    url(r"^add$", AddCartView.as_view(), name="add"),
]