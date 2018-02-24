from django.conf.urls import url
from users.views import *

urlpatterns = [
    url(r"^register$", RegisterView.as_view(), name="register"),
    url(r"^active/(?P<token>.+)$", ActiveView, name="active"),

]