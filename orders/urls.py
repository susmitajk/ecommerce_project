
from django.urls import path
from orders import views

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('place-order/', views.place_order, name='place_order'),
    path('order-summary/<int:order_id>/', views.order_summary, name='order_summary'),
    path('confirm-order/', views.confirm_order, name='confirm_order'),
    path('retry_payment/', views.retry_payment, name='retry_payment'),
    path('order/<uuid:order_id>/', views.order_detail, name='order_detail'),
    path('order/<uuid:order_id>/cancel/', views.cancel_order, name='cancel_order'),
    path('order/<uuid:order_id>/return/', views.return_order, name='return_order'),
    # sales report
    path('sales_report/', views.generate_sales_report, name='sales_report'),
     path('download_pdf_report/', views.download_pdf_report, name='download_pdf_report'),
    path('download_excel_report/',views.download_excel_report, name='download_excel_report'),
    # razorpay
    path('create-razorpay-order/', views.create_razorpay_order, name='create_razorpay_order'),
    # download invoice
    path('order/<uuid:order_id>/invoice/', views.download_invoice, name='download_invoice'),

]