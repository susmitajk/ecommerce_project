
from django.urls import path
from . import views

urlpatterns = [
    path('add_to_cart/<int:variant_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:variant_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update_quantity/<int:variant_id>/<int:quantity>/', views.update_quantity, name='update_quantity'),
    path('', views.cart, name='cart'),
    # coupon apply and remove
    path('apply_coupon/', views.apply_coupon, name='apply_coupon'),
    path('remove_coupon/', views.remove_coupon, name='remove_coupon'),
    # Wishlist
    # path('wishlist/', views.wishlist, name='wishlist'),
    # path('add_to_wishlist/<int:variant_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    
]