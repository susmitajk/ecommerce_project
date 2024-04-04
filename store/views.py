from django.shortcuts import render,get_object_or_404
from .models import Product,ProductVariant
from category.models import Category

# Create your views here.

# homepage
def homepage(request):
     # Fetch some non deleted products to display on the homepage 
    products = Product.objects.filter(is_deleted=False)[:8]
    category = Category.objects.filter(is_deleted=False)
    context = {
        'products': products,
        'category': category
    }
    return render(request, 'user_side/home.html', context)

# listing the product without category and product with category
def product_list(request, category_slug=None):
    categories = None
    products = None

    if category_slug:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_deleted=False)
    else:
        products = Product.objects.filter(is_deleted=False)

    context = {
        'products': products,
    }
    return render(request, 'store/product_list.html', context)

def product_detail(request, category_slug, product_slug):
    product = get_object_or_404(Product, category__slug=category_slug, slug=product_slug)
    variants = ProductVariant.objects.filter(product=product)
    
    context = {
        'product': product,
        'variants': variants,  # Pass the serialized data to the template
    }
    return render(request, 'store/product_detail.html', context)