from django.conf.urls import url
from cart.views import *

urlpatterns = [
    # 添加购物车
    url(r"^add$", AddCartView.as_view(), name="add"),
    #　展示购物车数据
    url(r"^$", CartInfoView.as_view(), name="info"),
    # 更新购物车数据
    url(r"^update$", UpdateCartView.as_view(), name='update'),
    # 删除购物车数据
    url(r"^delete$", DeleteCartView.as_view(), name="delete")
]