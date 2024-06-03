from django.urls import path,include
from . import views

urlpatterns = [
    path('admin_dashboard/', views.DashboardView, name='dashboard'),
    # best selling
    path('best_selling/', views.best_selling, name='best_selling'),
    # user management
    path('admin-panel/users/', views.user_list, name='user_list'),
    path('deactivate_user/<int:user_id>/', views.deactivate_user, name='deactivate_user'),
    path('activate_user/<int:user_id>/', views.activate_user, name='activate_user'),
    # order management
    path('orders/', views.order_list, name='order_list'),
    path('orders/<uuid:order_id>/edit/', views.edit_order, name='edit_order'),
    path('order/<uuid:order_id>/', views.view_order, name='view_order'),
    path('review_return/<uuid:order_id>/', views.review_return, name='review_return'),
    #coupon management
    path('coupons/', include('coupon_management.urls')),
    #offer management
    path('offers/', include('offers.urls')),

]
