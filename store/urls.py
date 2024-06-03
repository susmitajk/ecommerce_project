
from django.urls import path
from store import views

urlpatterns = [
    path('', views.homepage, name='home'),
    path('product_list/', views.product_list, name='product_list'),
    path('product_list/<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('product_details/<int:product_id>/', views.product_detail, name='product_detail'),
    path('get_variant_details/<int:variant_id>/', views.get_variant_details, name='get_variant_details'),
    
]