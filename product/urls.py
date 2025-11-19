from django.urls import path
from . import views

urlpatterns = [
    # Product
    path("my-product/", views.my_product, name="my_product"),
    path("my-product/<int:pk>/edit/", views.edit_product, name="edit_product"),
    path("my-product/<int:pk>/delete/", views.delete_product, name="delete_product"),
    path("add-product/", views.add_product, name="add_product"),
    path("product-detail/<int:pk>/", views.product_detail, name="product_detail"),
    # Cart
    path("cart/", views.cart, name="cart"),
    path("cart/add/", views.add_to_cart, name="add_to_cart"),
    path("cart/update/", views.update_cart, name="update_cart"),
    path("cart/delete/", views.delete_cart, name="delete_cart"),
]
