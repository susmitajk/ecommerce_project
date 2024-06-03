from django.forms import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from django.contrib import messages
from .models import Cart, CartItem
from store.models import ProductVariant
from coupon_management.models import Coupon
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import F
import json

@csrf_exempt
def add_to_cart(request, variant_id):
    if request.method == 'POST':
        variant = get_object_or_404(ProductVariant, id=variant_id)
        quantity = int(request.POST.get('quantity', 1))
        user = request.user

         # Check stock quantity
        if variant.stock < quantity:
            return JsonResponse({'success': False, 'message': 'Not enough stock available'})

        cart, created = Cart.objects.get_or_create(user=user)

        try:
            cart_item = cart.items.get(variant=variant)
            cart_item.quantity += quantity
            cart_item.save()
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(cart=cart, variant=variant, quantity=quantity)

        total_price = cart.get_total_price()

        # Check if the coupon still meets the criteria
        coupon_code = cart.coupon_code
        if coupon_code:
            coupon = Coupon.objects.get(code=coupon_code)
            if not (coupon.minimum_order_amount <= total_price <= coupon.maximum_order_amount):
                cart.coupon_code = None
                cart.discount_amount = 0
                cart.discounted_price = total_price
                cart.save()
                return JsonResponse({'success': True, 'message': 'Variant added to cart', 'total_price': total_price, 'coupon_removed': True})

        cart.discount_amount = (total_price * coupon.offer_percentage) / 100 if coupon_code else 0
        cart.discounted_price = total_price - cart.discount_amount
        cart.save()

        return JsonResponse({'success': True, 'message': 'Variant added to cart', 'total_price': total_price, 'discount_amount': cart.discount_amount, 'discounted_price': cart.discounted_price})

    return JsonResponse({'success': False, 'message': 'Invalid request'})

@csrf_exempt
def remove_from_cart(request, variant_id):
    try:
        variant = get_object_or_404(ProductVariant, id=variant_id)
        cart = Cart.objects.get(user=request.user)
        
        try:
            cart_item = CartItem.objects.get(cart=cart, variant=variant)
            cart_item.delete()
            total_price = cart.get_total_price()

            # Check if the coupon still meets the criteria
            coupon_code = cart.coupon_code
            if coupon_code:
                coupon = Coupon.objects.get(code=coupon_code)
                if not (coupon.minimum_order_amount <= total_price <= coupon.maximum_order_amount):
                    cart.coupon_code = None
                    cart.discount_amount = 0
                    cart.discounted_price = total_price
                    cart.save()
                    return JsonResponse({'success': True, 'message': f"{variant.product.product_name} removed from your cart.", 'total_price': total_price, 'coupon_removed': True})

            cart.discount_amount = (total_price * coupon.offer_percentage) / 100 if coupon_code else 0
            cart.discounted_price = total_price - cart.discount_amount
            cart.save()
            
            return JsonResponse({'success': True, 'message': f"{variant.product.product_name} removed from your cart.", 'total_price': total_price, 'discount_amount': cart.discount_amount, 'discounted_price': cart.discounted_price})
        except CartItem.DoesNotExist:
            total_price = cart.get_total_price()
            messages.error(request, "Item not found in your cart.")
            return JsonResponse({'success': False, 'message': "Item not found in your cart.", 'total_price': total_price})

    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'message': 'An error occurred while processing your request.'})

@csrf_exempt
def update_quantity(request, variant_id, quantity):
    if request.method == 'POST':
        variant = get_object_or_404(ProductVariant, id=variant_id)
        cart = Cart.objects.get(user=request.user)
        cart_item = CartItem.objects.get(cart=cart, variant=variant)

        # Check stock quantity
        if variant.stock < quantity:
            return JsonResponse({'success': False, 'message': 'Not enough stock available'})
        
        try:
            cart_item.quantity = quantity
            cart_item.save()
            total_price = cart.get_total_price()

            # Check if the coupon still meets the criteria
            coupon_code = cart.coupon_code
            if coupon_code:
                coupon = Coupon.objects.get(code=coupon_code)
                if not (coupon.minimum_order_amount <= total_price <= coupon.maximum_order_amount):
                    cart.coupon_code = None
                    cart.discount_amount = 0
                    cart.discounted_price = total_price
                    cart.save()
                    return JsonResponse({'success': True, 'quantity': quantity, 'total_price': total_price, 'coupon_removed': True})

            cart.discount_amount = (total_price * coupon.offer_percentage) / 100 if coupon_code else 0
            cart.discounted_price = total_price - cart.discount_amount
            cart.save()
            
            return JsonResponse({'success': True, 'quantity': quantity, 'total_price': total_price, 'discount_amount': cart.discount_amount, 'discounted_price': cart.discounted_price})
        except ValidationError as e:
            return JsonResponse({'success': False, 'message': str(e), 'quantity': cart_item.quantity})

    return JsonResponse({'success': False, 'message': 'Invalid request','quantity': None})


def cart(request):
    total_cart_items = 0
    total_price = 0
    cart = None
    cart_items = []

    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            cart_items = cart.items.all().order_by('-quantity')
            total_cart_items = cart_items.count()
            total_price = cart.get_total_price()
            # Get all coupons that meet the initial criteria
            available_coupons = Coupon.objects.filter(
                is_active=True,
                expiry_date__gt=timezone.now(),
                overall_usage_limit__gt=0,
                limit_per_user__gt=0,
                minimum_order_amount__lte=cart.get_total_price(),
                maximum_order_amount__gte=cart.get_total_price(),
                usage_count__lt=F('limit_per_user')  # Include only coupons with usage count less than limit_per_user
            )
            # Filter the coupons further based on remaining usage
            available_coupons = [coupon for coupon in available_coupons if coupon.remaining_usage() > 0]
            return render(request, 'cart/cart.html', {
                'cart': cart,
                'items': cart_items,
                'total_price': total_price,
                'cart_total': total_cart_items,
                'available_coupons': available_coupons,
            })
    else:
        messages.warning(request, "Your cart is empty.")
        out_of_stock_items = []
        return render(request, 'cart/cart.html', {
            'cart': cart,
            'items': cart_items,
            'total_price': total_price,
            'out_of_stock_items': out_of_stock_items,
            'cart_total': total_cart_items,
        })
    
    out_of_stock_items = [item for item in cart_items if item.quantity > item.variant.stock]
    
    return render(request, 'cart/cart.html', {
        'cart': cart,
        'items': cart_items,
        'total_price': total_price,
        'out_of_stock_items': out_of_stock_items,
        'cart_total': total_cart_items,
    })



def apply_coupon(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        coupon_code = data.get('coupon_code')
        print("coupon_code:", coupon_code)
        cart = Cart.objects.filter(user=request.user).first()

        if not cart:
            print("Cart not found")
            return JsonResponse({'success': False, 'message': 'Cart not found'})

        if not coupon_code:
            print("Coupon code is required")
            return JsonResponse({'success': False, 'message': 'Coupon code is required'})

        try:
            coupon = Coupon.objects.get(code=coupon_code)
        except Coupon.DoesNotExist:
            print("Invalid coupon code")
            return JsonResponse({'success': False, 'message': 'Invalid coupon code'})

        if not coupon.is_active:
            print("Coupon is not active")
            return JsonResponse({'success': False, 'message': 'Coupon is not active'})

        if coupon.is_expired():
            print("Coupon has expired")
            return JsonResponse({'success': False, 'message': 'Coupon has expired'})

        if coupon.remaining_usage() <= 0:
            print("Coupon usage limit exceeded")
            return JsonResponse({'success': False, 'message': 'Coupon usage limit exceeded'})

        if cart.get_total_price() < coupon.minimum_order_amount:
            print("Minimum order amount not met")
            return JsonResponse({'success': False, 'message': 'Minimum order amount not met'})

        # Apply the coupon
        cart.coupon_code = coupon_code
        cart.discount_amount = (cart.get_total_price() * coupon.offer_percentage) / 100
        cart.discounted_price = cart.get_total_price() - cart.discount_amount
        cart.save()

        print("Coupon applied successfully")
        return JsonResponse({
            'success': True,
            'message': 'Coupon applied successfully',
            'discount_amount': cart.discount_amount,
            'discounted_price': cart.discounted_price,
            'total_price': cart.get_total_price()
        })

    print("Invalid request")
    return JsonResponse({'success': False, 'message': 'Invalid request'})


def remove_coupon(request):
    if request.method == 'POST':
        cart = Cart.objects.filter(user=request.user).first()

        if not cart:
            return JsonResponse({'success': False, 'message': 'Cart not found'})

        if not cart.coupon_code:
            return JsonResponse({'success': False, 'message': 'No coupon applied'})

        # Remove the coupon
        cart.coupon_code = None
        cart.discount_amount = 0
        cart.discounted_price = 0
        cart.save()

        return JsonResponse({'success': True, 'message': 'Coupon removed successfully', 'total_price': cart.get_total_price()})

    return JsonResponse({'success': False, 'message': 'Invalid request'})


