
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    #  user management
    path('accounts/',include('accounts.urls', namespace='accounts')),
    # store (homepage, products)
    path('',include('store.urls')),
    # cart
    path('cart/', include('cart.urls')),
    #wishlist
    path('wishlist/', include('wishlist.urls')),
    # checkout/ orders
    path('orders/', include('orders.urls')),
    
    # admin_panel
    path('admin_panel/', include('admin_panel.urls')),
    # category management in admin_panel
    path('admin-panel/category/', include('admin_panel.category_urls')),
    # product management in admin_panel
    path('admin-panel/product/', include('admin_panel.product_urls')),
    
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)