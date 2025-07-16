from django.urls import path
from . import views

urlpatterns = [
    path("create-order/", views.create_order, name="create_order"),
    path("pink-interest/", views.submit_pink_interest, name="submit_pink_interest"),
    path("create-checkout-session/", views.create_checkout_session, name="create_checkout_session"),
    path("orders/", views.list_orders, name="list_orders"),
]
