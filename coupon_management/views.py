from django.shortcuts import render,redirect,get_object_or_404
from coupon_management.models import Coupon
from admin_panel.forms import CouponForm
from django.http import JsonResponse
from django.utils import timezone

# Create your views here.
#list coupon
def list_coupons(request):
    coupons = Coupon.objects.all().order_by('-id')
    current_time = timezone.now()
    print("Current time:", current_time)
    for coupon in coupons:
        print(f"Coupon {coupon.code} is active: {coupon.is_active}")
        print(f"Coupon {coupon.code} expiry date: {coupon.expiry_date}")
        if coupon.is_active and coupon.is_expired():
            print(f"Coupon {coupon.code} is expired.")
            coupon.is_active = False
            coupon.save()
    return render(request, 'admin_panel/coupon/coupon_list.html', {'coupons': coupons})



#Create coupon
def create_coupon(request):
    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            instance = form.save()  # Save the form
            print("Coupon saved successfully:", instance)  
            return redirect('list_coupons')  
        else:
            print("Form errors:", form.errors)  # Print form errors for debugging
    else:
        form = CouponForm()
    return render(request, 'admin_panel/coupon/create_coupon.html', {'form': form})

# deactivate coupon
def deactivate_coupon(request):
    if request.method == 'POST':
        coupon_id = request.POST.get('coupon_id')
        coupon = get_object_or_404(Coupon, id=coupon_id)
        if not coupon.is_active:
            return JsonResponse({'message': 'Coupon is already inactive'}, status=400)
        coupon.is_active = False
        coupon.save()
        return JsonResponse({'message': 'Coupon deactivated successfully'})
    else:
        return JsonResponse({'message': 'Invalid request method'}, status=405)
    
# activate coupon
def activate_coupon(request):
    if request.method == 'POST':
        coupon_id = request.POST.get('coupon_id')
        coupon = get_object_or_404(Coupon, id=coupon_id)
        if coupon.is_active:
            return JsonResponse({'message': 'Coupon is already active'}, status=400)
        coupon.is_active = True
        coupon.save()
        return JsonResponse({'message': 'Coupon activated successfully'})
    else:
        return JsonResponse({'message': 'Invalid request method'}, status=405)
    
# edit coupon

def edit_coupon(request, coupon_id):
    coupon = get_object_or_404(Coupon, id=coupon_id)
    if request.method == 'POST':
        form = CouponForm(request.POST, instance = coupon)
        if form.is_valid():
            instance = form.save()  # Save the form
            print("Coupon saved successfully:", instance)  
            return redirect('list_coupons')  
        else:
            print("Form errors:", form.errors)  # Print form errors for debugging
    else:
        form = CouponForm(instance = coupon)
    return render(request, 'admin_panel/coupon/coupon_edit.html', {'form': form})


# Delete coupon
def delete_coupon(request, coupon_id):
    coupon = get_object_or_404(Coupon, id=coupon_id)
    if request.method == 'POST':
        coupon.delete()
        return redirect('list_coupons')