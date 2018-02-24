from django.conf.urls import url
from users.views import *

urlpatterns = [
    url(r"^register$", register, name="register"),
]