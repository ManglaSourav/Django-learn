from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Orders
    path('', views.OrderListView.as_view(), name='order-list'),
    path('<int:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('<int:order_id>/status-history/', views.OrderStatusHistoryView.as_view(), name='order-status-history'),
    
    # Cart
    path('cart/', views.CartView.as_view(), name='cart'),
    path('cart/items/', views.CartItemListView.as_view(), name='cart-item-list'),
    path('cart/items/<int:pk>/', views.CartItemDetailView.as_view(), name='cart-item-detail'),
    path('cart/add/', views.add_to_cart, name='add-to-cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove-from-cart'),
    path('cart/update-quantity/<int:item_id>/', views.update_cart_item_quantity, name='update-cart-item-quantity'),
    path('cart/clear/', views.clear_cart, name='clear-cart'),
    path('checkout/', views.checkout, name='checkout'),
]
