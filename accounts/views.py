from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import SignUpForm,ProfileEditForm,AddressForm
from .models import Account,Address, Wallet,WalletTransaction
from cart.models import Cart, CartItem
# from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib.auth import authenticate, login, logout
from .utils import generate_otp, send_otp_email
from django.http import HttpResponseForbidden, JsonResponse
import time
from orders.models import Order

# Create your views here.
@never_cache
def registration(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password1 = form.cleaned_data.get('password1')
            password2 = form.cleaned_data.get('password2')

            # Check if email is already in use
            if Account.objects.filter(email=email).exists():
                messages.info(request, 'Email already used!')
                return redirect('accounts:register')
            
            # Checking password matching
            if password1 != password2:
                messages.info(request, "Entered passwords don't match")
                return redirect('accounts:register')

            # If additional checks pass, save the form
            user = form.save()
            user.set_password(form.cleaned_data['password1'])

            otp = generate_otp()
            send_otp_email(user.email, otp)
            request.session['otp'] = otp
            request.session['otp_creation_time'] = time.time()  # Store otp creation time
            request.session['user_id'] = user.id

            return render(request, 'accounts/user_otp_verify.html', {"email": user.email})
        else:
            # Registration failed, pass form data back to template
            context = {'form': form}
            messages.error(request, 'Registration failed. Please correct the errors below.')
            return render(request, 'accounts/user_signup.html', context)

    else: 
        form = SignUpForm()
        context = {'form': form}
    return render(request, 'accounts/user_signup.html', context)

@never_cache
def verify_otp(request):
    if request.method == 'POST':
        otp_entered = request.POST.get('otpEntered') 
        stored_otp = request.session.get('otp')
        otp_creation_time = request.session.get('otp_creation_time')
        if otp_entered == stored_otp:
            current_time = time.time()
            if current_time - otp_creation_time <= 120:  # OTP expires in 2 minutes (120 seconds)
                user_id = request.session.get('user_id')
                if user_id:
                    user = Account.objects.get(id=user_id)
                    user.is_verified = True
                    user.save()
                    user.activate_account()  # Activate the user account
                    del request.session['otp']
                    del request.session['otp_creation_time']
                    del request.session['user_id']
                    response_data = {'message': 'Your account has been verified successfully.'}
                    return JsonResponse(response_data)
                else:
                    response_data = {'error': 'User not found.'}
                    return JsonResponse(response_data, status=400)  # Return error response
            else:
                response_data = {'error': 'OTP has expired. Please request a new one.'}
                return JsonResponse(response_data, status=400)  # Return error response
        else:
            response_data = {'error': 'Invalid OTP. Please try again.'}
            return JsonResponse(response_data, status=400)  # Return error response
    else:
        response_data = {'error': 'Method not allowed.'}
        return JsonResponse(response_data, status=405)  # Return error response

@never_cache
def resend_otp(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        if user_id:
            user = Account.objects.get(id=user_id)
            otp = generate_otp()
            send_otp_email(user.email, otp)
            request.session['otp'] = otp
            request.session['otp_creation_time'] = time.time()  # Update OTP creation time
            response_data = {'message': 'OTP has been resent to your email.'}
            return JsonResponse(response_data)
        else:
            response_data = {'error': 'User not found.'}
            return JsonResponse(response_data, status=400)  # Return error response
    # If the request method is not POST, return error response
    response_data = {'error': 'Method not allowed.'}
    return JsonResponse(response_data, status=405)


@never_cache
def home_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            if user.is_active:
                if user.is_verified:
                    login(request, user)
                    # Redirect to a success page.
                    return redirect('home')
                else:
                    # User is not verified, show error message.
                    messages.error(request, 'Please verify your account before trying to login.')
            else:
                # User account is deactivated, prevent login
                messages.error(request, 'Your account is deactivated. Please contact support.')
        else:
            # Return an 'invalid login' error message.
            messages.error(request, 'Invalid email or password.')
    return render(request, 'accounts/user_login.html')

@never_cache
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = get_object_or_404(Account, email=email)
        
        # Generate OTP and send it to the user's email
        otp = generate_otp()
        send_otp_email(user.email, otp)
        
        # Store OTP and user ID in session for verification
        request.session['forgot_password_otp'] = otp
        request.session['forgot_password_otp_creation_time'] = time.time()
        request.session['forgot_password_user_id'] = user.id
        
        # Redirect to the OTP verification page
        return redirect('accounts:forgot_password_otp')
    
    return render(request, 'accounts/forgot_password.html')

@never_cache
def reset_password_otp(request):
    if request.method == 'POST':
        otp_entered = request.POST.get('otpEntered') 
        stored_otp = request.session.get('forgot_password_otp')
        otp_creation_time = request.session.get('forgot_password_otp_creation_time')
        if otp_entered == stored_otp:
            current_time = time.time()
            if current_time - otp_creation_time <= 120:  # OTP expires in 2 minutes (120 seconds)
                user_id = request.session.get('forgot_password_user_id')
                if user_id:
                    user = Account.objects.get(id=user_id)
                    if user.is_verified:
                        del request.session['forgot_password_otp']
                        del request.session['forgot_password_otp_creation_time']
                        response_data = {'message': 'OTP verified successfully.'}
                        return JsonResponse(response_data)
                    else:
                        response_data = {'error': 'User account is not verified.'}
                        return JsonResponse(response_data, status=400)  # Return error response
                else:
                    response_data = {'error': 'User not found.'}
                    return JsonResponse(response_data, status=400)  # Return error response
            else:
                response_data = {'error': 'OTP has expired. Please request a new one.'}
                return JsonResponse(response_data, status=400)  # Return error response
        else:
            response_data = {'error': 'Invalid OTP. Please try again.'}
            return JsonResponse(response_data, status=400)  # Return error response
    else:
        return render(request, 'accounts/reset_pass_otp.html')
        # response_data = {'error': 'Method not allowed.'}
        # return JsonResponse(response_data, status=405)

def resend_password_reset_otp(request):
    if request.method == 'POST':
        user_id = request.session.get('forgot_password_user_id')
        if user_id:
            user = Account.objects.get(id=user_id)
            otp = generate_otp()
            send_otp_email(user.email, otp)
            request.session['forgot_password_otp'] = otp
            request.session['forgot_password_otp_creation_time'] = time.time()  # Update OTP creation time
            response_data = {'message': 'OTP has been resent to your email.'}
            return JsonResponse(response_data)
        else:
            response_data = {'error': 'User not found.'}
            return JsonResponse(response_data, status=400)  # Return error response
    # If the request method is not POST, return error response
    response_data = {'error': 'Method not allowed.'}
    return JsonResponse(response_data, status=405)

@never_cache
def reset_password(request):
    if request.method == 'POST':
        user_id = request.session.get('forgot_password_user_id')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        print('\n\n\n\n\n ------------------------')
        print(user_id)
        print(password1)
        print(password2)
        # if user_id:
        try:
            user = Account.objects.get(id=user_id)
            if password1 == password2:
                user.set_password(password1)
                user.save()
                messages.success(request, 'Password reset successfully.')
                # Clear session data after password reset
                del request.session['forgot_password_otp']
                del request.session['forgot_password_user_id']
                return redirect('accounts:login')
            else:
                messages.error(request, 'Passwords do not match.')
                return redirect('accounts:reset_password')
        except:
            messages.error(request, 'User not found.')
            return redirect('accounts:login')
    
    return render(request, 'accounts/reset_password.html')

@never_cache
def user_logout(request):
    logout(request)
    messages.success(request, 'You have logged out')
    return redirect('home')  


# User Profile

@login_required
def account_dashboard(request):
    user = request.user   # captures the current user
    addresses = Address.objects.filter(user=user)
    
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)
        total_cart_items = cart_items.count()
    except Cart.DoesNotExist:
        cart = None
        total_cart_items = 0
    
    orders = Order.objects.filter(user=request.user).order_by('-created_at') # order sorting in user profile

    try:
        wallet = Wallet.objects.get(user=request.user)
        transactions = wallet.transactions.all()
    except Wallet.DoesNotExist:
        # Handle the case where Wallet doesn't exist for the user
        wallet = None
        transactions = []
        
    context = {
        'user': user,
        'addresses': addresses,
        'cart_total': total_cart_items,
        'orders': orders,
        'wallet': wallet,
        'transactions': transactions,
    }
    return render(request, 'user_profile/profile.html', context)


# Edit user profile
@login_required
def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        print("Form data received:", request.POST)  # Print form data for debugging
        form = ProfileEditForm(request.POST, instance=user)  # Initialize the form with request.POST data and instance=user
        
        if form.is_valid():
            form.save()  # Save the form data to update the user profile
            return redirect('accounts:account_dashboard')
        else:
            print(form.errors)      # debugging
    else:
        form = ProfileEditForm(instance=user)  # Initialize the form with the current user's data
    return render(request, 'user_profile/edit_profile.html', {'form': form})


# Address CRUD

# Address creation
@login_required
def create_address(request):
    next_url = request.GET.get('next', None)
    
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            if request.POST.get('is_default') == 'on':
                address.is_default = True
                Address.objects.filter(user=request.user).exclude(id=address.id).update(is_default=False)
            address.save()
            if next_url:
                return redirect(next_url)
            else:
                return redirect('accounts:account_dashboard')
    else:
        form = AddressForm()
    
    return render(request, 'user_profile/create_address.html', {'form': form})

# Address Updation
@login_required
def edit_address(request, address_id):
    next_url = request.GET.get('next', None)
    
    address = get_object_or_404(Address, id=address_id)
    
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            if request.POST.get('default_address') == 'on':
                address.is_default = True
                Address.objects.filter(user=request.user).exclude(id=address.id).update(is_default=False)
                address.save()
            else:
                address.is_default = False
                address.save()
            if next_url:
                return redirect(next_url)
            else:
                return redirect('accounts:account_dashboard')
    else:
        form = AddressForm(instance=address)
    
    return render(request, 'user_profile/edit_address.html', {'form': form, 'address': address})



# Address Deletion
@login_required
def delete_address(request, address_id):
    # Ensure the user is authenticated
    if not request.user.is_authenticated:
        return HttpResponseForbidden("Authentication required to delete the address.")

    # Retrieve the Address object from the Address model using the address_id
    address = get_object_or_404(Address, id=address_id)
    # Check if the user requesting the deletion is the owner of the address
    if address.user == request.user:
        # If the request method is POST, delete the address
        if request.method == 'POST':
            address.delete()
            # messages.success(request, 'Address deleted successfully.')
            return redirect('accounts:account_dashboard')
        else:
            # Handle unauthorized access (optional)
            return HttpResponseForbidden("You are not authorized to delete this address.")
    else:
        # Handle unauthorized access (optional)
        return HttpResponseForbidden("You are not authorized to delete this address.")