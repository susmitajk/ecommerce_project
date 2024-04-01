
from django.urls import path
from accounts import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.registration, name='register'),
    path('login/', views.home_login, name='login'),
    path('verify-otp/',views.verify_otp, name='verify_otp'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),
    path('logout/', views.user_logout, name='logout'),
    path('forgotpassword/',views.forgot_password, name='forgot_password'),
    path('reset-password-otp/', views.reset_password_otp, name='forgot_password_otp'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('reset-password-resend-otp/', views.resend_password_reset_otp, name='reset_password_resend_otp'),
]