from django.conf.urls import url
from users.views import *

urlpatterns = [
    url(r"^register$", RegisterView.as_view(), name="register"),
    url(r"^active/(?P<token>.+)$", ActiveView.as_view(), name="active"),
    url(r"^login$", LoginView.as_view(), name="login"),
    url(r"^logout$", LogoutView.as_view(), name="logout"),
    url(r"^address$", AddressView.as_view(), name="address"),


]