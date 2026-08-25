from django.urls import path
from . import views

app_name = "catalog"

urlpatterns = [
    path("quotes/<int:quote_id>/print/", views.quote_print, name="quote_print"),
    path("", views.ProductListView.as_view(), name="product_list"),
    path("cart/add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/", views.cart_view, name="cart"),
    path("cart/update/<int:item_id>/", views.update_cart, name="update_cart"),
    path("cart/remove/<int:item_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("checkout/", views.checkout_view, name="checkout"),
    path("checkout/whatsapp/", views.whatsapp_checkout, name="whatsapp_checkout"),
    path("order/success/<int:order_id>/", views.order_success, name="order_success"),
    path("pos/", views.POSView.as_view(), name="pos"),
    path("<slug:slug>/", views.ProductDetailView.as_view(), name="product_detail"),
]
