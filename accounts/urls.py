
from django.urls import path
from accounts import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.registration, name='register'),
    path('login/', views.home_login, name='login'),
    #user verification
    path('verify-otp/',views.verify_otp, name='verify_otp'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),
    path('logout/', views.user_logout, name='logout'),
    # forgot password
    path('forgotpassword/',views.forgot_password, name='forgot_password'),
    path('reset-password-otp/', views.reset_password_otp, name='forgot_password_otp'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('reset-password-resend-otp/', views.resend_password_reset_otp, name='reset_password_resend_otp'),
    # user profile
    path('account_dashboard/', views.account_dashboard, name='account_dashboard'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    # Address Management
    path('create_address/', views.create_address, name='create_address'),
    path('edit_address/<int:address_id>/', views.edit_address, name='edit_address'),
    path('delete_address/<int:address_id>/', views.delete_address, name='delete_address'),
]