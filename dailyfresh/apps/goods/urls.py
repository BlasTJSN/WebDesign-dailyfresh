from django.conf.urls import url
from goods.views import *

urlpatterns = [
    url(r"^index$", IndexView.as_view(), name="index"),

    # 详情: http://127.0.0.1:8000/detail/10
    url(r'^detail/(?P<sku_id>\d+)$', DetailView.as_view(), name='detail'),

    # 商品列表页面 http://127.0.0.1:8000/list/category_id/page_num?sort=default
    url(r"^list/(?P<category_id>\d+)/(?P<page_num>\d+)", ListView.as_view(), name="list")

]