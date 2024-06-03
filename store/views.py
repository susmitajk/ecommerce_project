from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, ProductVariant
from category.models import Category
from django.http import JsonResponse
from cart.models import Cart, CartItem
from django.views.decorators.cache import never_cache


from django.db.models import Min, Max
from django.db.models.functions import Lower

# homepage
@never_cache
def homepage(request):
    products = Product.objects.filter(is_deleted=False, category__is_deleted=False)[:8]
    category = Category.objects.filter(is_deleted=False)
    total_cart_items = 0

    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_items = CartItem.objects.filter(cart=cart)
            total_cart_items = cart_items.count()
        except Cart.DoesNotExist:
            total_cart_items = 0  # Handle the case when Cart does not exist for the user

    context = {
        'products': products,
        'category': category,
        'cart_total': total_cart_items,
    }
    return render(request, 'user_side/home.html', context)


"""listing the product without category and product with category"""

def product_list(request, category_slug=None):
    categories = None
    products = None
    sort = request.GET.get('sort')

    total_cart_items = 0
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_items = CartItem.objects.filter(cart=cart)
            total_cart_items = cart_items.count()
        except Cart.DoesNotExist:
            total_cart_items = 0  # Handle the case when Cart does not exist for the user

    if category_slug:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_deleted=False)
    else:
        products = Product.objects.filter(is_deleted=False)
    
    # Sorting based on the selected option
    if sort == 'price_low_high':
        products = products.annotate(min_price=Min('variants__price')).order_by('min_price')
    elif sort == 'price_high_low':
        products = products.annotate(max_price=Max('variants__price')).order_by('-max_price')
    elif sort == 'name_a_z':
        products = products.annotate(lower_name=Lower('product_name')).order_by('lower_name')
    elif sort == 'name_z_a':
        products = products.annotate(lower_name=Lower('product_name')).order_by('-lower_name')
    elif sort == 'featured':
        products = products.filter(featured=True)
    elif sort == 'new_arrivals':
        products = products.order_by('-id')
    
    context = {
        'products': products,
        'cart_total': total_cart_items,
        'sort': sort,
    }
    return render(request, 'store/product_list.html', context)

def product_detail(request, product_id):
    try:
        variant = ProductVariant.objects.get(id=product_id, is_deleted=False)
        variants = ProductVariant.objects.filter(is_deleted=False)
        images = variant.images.filter(is_deleted=False)
        
        total_cart_items = 0
        if request.user.is_authenticated:
            try:
                cart = Cart.objects.get(user=request.user)
                cart_items = CartItem.objects.filter(cart=cart)
                total_cart_items = cart_items.count()
            except Cart.DoesNotExist:
                total_cart_items = 0  # Handle the case when Cart does not exist for the user


        # Calculate total stock of all variants
        all_variant_stock = sum(variant.stock for variant in variants)
        
    except ProductVariant.DoesNotExist:
        variant = None
        variants = None
        images = None
        all_variant_stock = 0
    
    context = {
        'variant': variant,
        'variants': variants,
        'images': images,
        'all_variant_stock': all_variant_stock,
        'cart_total': total_cart_items,
    }
    return render(request, 'store/product_detail.html', context)

# this for getting the variant according to the select option
def get_variant_details(request, variant_id):
    try:
        variant = ProductVariant.objects.get(id=variant_id)
        data = {
            'name': variant.name,
            'main_image_url': variant.images.first().image.url if variant.images.exists() else '',
            'original_price': float(variant.price),
            'discounted_price': float(variant.discounted_price),
            'stock': variant.stock,
            'age': variant.age,
            'proof': variant.proof,
            'volume': variant.volume,
        }
        return JsonResponse(data)
    except ProductVariant.DoesNotExist:
        return JsonResponse({'error': 'Variant not found'}, status=404)


