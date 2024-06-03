from django.urls import path
from offers import views

urlpatterns = [
    # product Offer
    path('product_offer_list/', views.product_offer_list, name="product_offer_list"),
    path('product_offer/create', views.product_offer_create, name="product_offer_create"),
    path('product_offer/<int:product_id>/edit', views.product_offer_update, name="product_offer_update"),
    path('product_offer/<int:product_id>/delete', views.product_offer_delete, name="product_offer_delete"),
    # category Offer
    path('category_offer_list/', views.category_offer_list, name="category_offer_list"),
    path('category_offer/create', views.category_offer_create, name="category_offer_create"),
    path('category_offer/<int:category_id>/edit', views.category_offer_update, name="category_offer_update"),
    path('category_offer/<int:category_id>/delete', views.category_offer_delete, name="category_offer_delete"),
    # referral Offer
    path('referral_offer_list/', views.referral_offer_list, name="referral_offer_list"),
    path('referral_offer/create', views.referral_offer_create, name="referral_offer_create"),
    path('referral_offer/<int:referral_id>/edit', views.referral_offer_update, name="referral_offer_update"),
    path('referral_offer/<int:referral_id>/delete', views.referral_offer_delete, name="referral_offer_delete"),
]
