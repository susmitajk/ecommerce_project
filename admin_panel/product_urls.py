from django.urls import path
from .product_views import (brand_list,brand_create,brand_update,brand_delete,brand_restore,
                            type_list,type_create,type_update,type_restore,type_delete,
                            product_list, product_create, product_update,product_restore,product_delete,
                            product_variant_list,product_variant_create,product_variant_update,product_variant_restore,product_variant_delete,
                            product_image_list,product_image_create,product_image_update,product_image_delete,product_image_restore
                            )

urlpatterns = [
    #brand
    path('brands/', brand_list, name='brand_list'),
    path('brands/create/', brand_create, name='brand_create'),
    path('brands/<int:brand_id>/update/', brand_update, name='brand_update'),
    path('brands/<int:brand_id>/delete/', brand_delete, name='brand_delete'),
    path('brands/<int:brand_id>/restore/', brand_restore, name='brand_restore'),
    #type
    path('types/', type_list, name='type_list'),
    path('types/create/', type_create, name='type_create'),
    path('types/<int:type_id>/update/', type_update, name='type_update'),
    path('types/<int:type_id>/restore/', type_restore, name='type_restore'),
    path('types/<int:type_id>/delete/', type_delete, name='type_delete'),
    #product
    path('products/', product_list, name='product1_list'),
    path('products/create/', product_create, name='product_create'),
    path('products/<int:product_id>/update/', product_update, name='product_update'),
    path('products/<int:product_id>/restore/', product_restore, name='product_restore'),
    path('products/<int:product_id>/delete/', product_delete, name='product_delete'),
    #product Variant
    path('variants/', product_variant_list, name='product_variant_list'),
    path('variants/create/', product_variant_create, name='product_variant_create'),
    path('variants/<int:variant_id>/update/', product_variant_update, name='product_variant_update'),
    path('variants/<int:variant_id>/delete/', product_variant_delete, name='product_variant_delete'),
    path('variants/<int:variant_id>/restore/', product_variant_restore, name='product_variant_restore'),
    #Product variant images
    path('images/', product_image_list, name='product_image_list'),
    path('images/create/', product_image_create, name='product_image_create'),
    path('images/<int:image_id>/update/', product_image_update, name='product_image_update'),
    path('images/<int:image_id>/delete/', product_image_delete, name='product_image_delete'),
    path('images/<int:image_id>/restore/', product_image_restore, name='product_image_restore'),
]