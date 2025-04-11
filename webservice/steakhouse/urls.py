from django.urls import path

from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('order/success/<int:order_id>/', views.order_success, name='order_success'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:product_id>/', views.update_cart, name='update_cart'),
    path('clear-cart/', views.clear_cart, name='clear_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
]
