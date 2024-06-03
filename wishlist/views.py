from django.shortcuts import render, get_object_or_404, redirect
from wishlist.models import Wishlist, WishlistItem
from store.models import ProductVariant
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from cart.views import add_to_cart as cart_add_to_cart

# Display wishlist
def wishlist(request):
    if request.method == 'POST':
        variant_id = request.POST.get('variant_id')
        action = request.POST.get('action')

        if action == 'add_to_cart':
            # Call the add_to_cart view function from cart app with the variant_id
            return cart_add_to_cart(request, variant_id)

        elif action == 'remove_from_wishlist':
            # Remove the variant from the wishlist
            user_wishlist, created = Wishlist.objects.get_or_create(user=request.user)
            variant = get_object_or_404(ProductVariant, id=variant_id)
            try:
                wishlist_item = WishlistItem.objects.get(wishlist=user_wishlist, variant=variant)
                wishlist_item.delete()
                messages.success(request, 'Product removed from wishlist.')
                # Optionally, you can redirect the user back to the wishlist page
                return redirect('wishlist')
            except WishlistItem.DoesNotExist:
                messages.error(request, 'Product not found in wishlist.')

    # Fetch the user's wishlist
    user_wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    wishlist_items = user_wishlist.items.all()
    context = {
        'wishlist_items': wishlist_items,
    }
    return render(request, 'wishlist/wishlist.html', context)

# Add to wishlist
@csrf_exempt
def add_to_wishlist(request, variant_id):
    if request.method == 'POST':
        # Get or create the user's wishlist
        user_wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        variant = get_object_or_404(ProductVariant, id=variant_id)

        # Check if the variant already exists in the wishlist
        if user_wishlist.items.filter(variant=variant).exists():
            return JsonResponse({'success': False, 'message': 'Product already exists in the wishlist.'})

        # Add the variant to the wishlist
        wishlist_item = WishlistItem.objects.create(wishlist=user_wishlist, variant=variant)
        return JsonResponse({'success': True, 'message': 'Product added to wishlist.'})

    return JsonResponse({'success': False, 'message': 'Invalid request'})

# Remove from wishlist
@csrf_exempt
def remove_from_wishlist(request, variant_id):
    if request.method == 'POST':
        # Get the variant and wishlist item
        variant = get_object_or_404(ProductVariant, id=variant_id)
        user_wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        wishlist_item = get_object_or_404(WishlistItem, wishlist=user_wishlist, variant=variant)

        # Delete the wishlist item
        wishlist_item.delete()

        return JsonResponse({'success': True, 'message': 'Product removed from wishlist.'})

    return JsonResponse({'success': False, 'message': 'Invalid request'})
