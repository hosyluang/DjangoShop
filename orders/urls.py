from django.urls import path
from . import views

urlpatterns = [
    path("checkout/", views.checkout, name="checkout"),
    path("send-mail/", views.send_order_email, name="send_mail"),
]
