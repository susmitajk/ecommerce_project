from django.urls import path
from .category_views import category_list,add_category,edit_category,deactivate_category,activate_category

urlpatterns = [
    path('category-list/', category_list, name='category_list'),
    path('add-category/', add_category, name='add_category'),
    path('edit-category/<int:category_id>/', edit_category, name='edit_category'),
    path('deactivate-category/<int:category_id>/', deactivate_category, name='deactivate_category'),
    path('activate-category/<int:category_id>/', activate_category, name='activate_category'),
]