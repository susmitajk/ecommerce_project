from django.shortcuts import render
from .models import Product

# Create your views here.
def homepage(request):
     # Fetch some products to display on the homepage
    products = Product.objects.filter(is_deleted=False).prefetch_related('images', 'variants') 
    context = {
        'products': products
    }
    return render(request, 'user_side/home.html', context)