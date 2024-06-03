from django.urls import path
from coupon_management import views

urlpatterns = [
   path('coupons_list/', views.list_coupons, name='list_coupons'),
   path('create/', views.create_coupon, name='create_coupon'),
   path('deactivate_coupon/', views.deactivate_coupon, name='deactivate_coupon'),
   path('activate_coupon/', views.activate_coupon, name='activate_coupon'),
   path('edit_coupon/<int:coupon_id>/', views.edit_coupon, name='edit_coupon'),
   path('delete_coupon/<int:coupon_id>/', views.delete_coupon, name='delete_coupon'),
]