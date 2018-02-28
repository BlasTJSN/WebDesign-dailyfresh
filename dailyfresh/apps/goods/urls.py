from django.conf.urls import url
from goods.views import *

urlpatterns = [
    url(r"^index$", IndexView.as_view(), name="index"),

    # 详情: http://127.0.0.1:8000/detail/10
    url(r'^detail/(?P<sku_id>\d+)$', DetailView.as_view(), name='detail')

]