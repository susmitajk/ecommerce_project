
from django.urls import path
from store import views

urlpatterns = [
    path('', views.homepage, name='home'),
    path('product_list/', views.product_list, name='product_list'),
    path('product_list/<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('product_list/<slug:category_slug>/<slug:product_slug>', views.product_detail, name='product_detail'),
]