import json
from decimal import Decimal, getcontext
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
import requests
from cart.models import Cart, CartItem
from accounts.models import Address,Wallet,WalletTransaction
from .models import Order, OrderItem
from django.db.models import Sum,F
from django.db import transaction
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from .forms import SalesReportFilterForm
from django.utils import timezone
from datetime import datetime, timedelta
from coupon_management.models import Coupon
from fpdf import FPDF
import pandas as pd
from io import BytesIO
from django.template.loader import render_to_string
from django.http import HttpResponse, JsonResponse
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import hmac
import hashlib
# Set the precision for Decimal operations
getcontext().prec = 28

# Create your views here.

# checkout
@login_required
def checkout(request):
    cart = Cart.objects.get(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    total_cart_items = cart_items.count()

    total_price = cart.get_total_price()
    coupon_discount_amount = cart.discount_amount if cart.coupon_code else 0
    discounted_price = cart.discounted_price if cart.coupon_code else total_price

    addresses = Address.objects.filter(user=request.user).order_by('-is_default')
    

    context = {
        'cart_total': total_cart_items,
        'addresses': addresses,
        'cart': cart,
        'total_price': total_price,
        'coupon_discount_amount': coupon_discount_amount,
        'discounted_price': discounted_price,
        'razorpay_key': settings.RAZORPAY_KEY_ID, 
      
    }
    return render(request, 'order/checkout.html', context)


def handle_online_payment(order, razorpay_order_id, razorpay_payment_id, razorpay_signature):
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    if not (razorpay_order_id and razorpay_payment_id and razorpay_signature):
        print("Razorpay payment details are missing")  # Debug print
        return False, "Razorpay payment details are missing."

    try:
        # Verify signature
        generated_signature = hmac.new(
            bytes(settings.RAZORPAY_KEY_SECRET, 'utf-8'),
            bytes(razorpay_order_id + "|" + razorpay_payment_id, 'utf-8'),
            hashlib.sha256
        ).hexdigest()

        if generated_signature != razorpay_signature:
            return False, "Razorpay signature verification failed."

        response = client.payment.fetch(razorpay_payment_id)
        print("Razorpay API response:", response)  # Debug print
        if response['status'] == 'captured':
            order.status = 'Confirmed'
            order.save()
            return True, "Payment successful."
        else:
            return False, f"Payment status is {response['status']}."
    except razorpay.errors.BadRequestError as e:
        print(f"BadRequestError: {e}")  # Debug print
        return False, "Invalid request to Razorpay API."
    except razorpay.errors.ServerError as e:
        print(f"ServerError: {e}")  # Debug print
        return False, "Server error occurred while fetching payment details from Razorpay."
    except Exception as e:
        print(f"Error fetching payment: {e}")  # Debug print
        return False, "An error occurred while fetching payment details."


@login_required
def place_order(request):
    if request.method == 'POST':
        address_id = request.POST.get('address')
        payment_method = request.POST.get('payment_method')
        razorpay_order_id = request.POST.get('razorpay_order_id', None)
        razorpay_payment_id = request.POST.get('razorpay_payment_id', None)
        razorpay_signature = request.POST.get('razorpay_signature', None)
        payment_status = request.POST.get('payment_status', 'Pending')
        print(f"Received razorpay_order_id: {razorpay_order_id}, razorpay_payment_id: {razorpay_payment_id}, razorpay_signature: {razorpay_signature}")  # Debug print
        cart = get_object_or_404(Cart, user=request.user)

        # Convert total price from USD to INR
        response = requests.get('https://api.exchangerate-api.com/v4/latest/USD')
        data = response.json()
        usd_to_inr = Decimal(data['rates']['INR'])  # Convert to Decimal

        # Calculate total price in USD
        total_price_usd = cart.discounted_price if cart.coupon_code else cart.get_total_price()

        # Calculate total price in INR
        total_price_inr = total_price_usd * usd_to_inr  # This will now work since both are Decimals

        if total_price_inr > 0:  # Ensure cart is not empty
            address = get_object_or_404(Address, id=address_id)

            try:
                with transaction.atomic():
                    # Check stock quantities
                    for cart_item in cart.items.all():
                        if cart_item.quantity > cart_item.variant.stock:
                            messages.error(request, f"Not enough stock for {cart_item.variant.product.name}")
                            return redirect('checkout')

                    # Convert total price back to USD before saving to the order
                    total_price_usd = total_price_inr / usd_to_inr

                    # Fetch the coupon if applied
                    coupon_code = cart.coupon_code
                    discount_percentage = 0
                    if coupon_code:
                        try:
                            coupon = Coupon.objects.get(code=coupon_code)
                            discount_percentage = coupon.offer_percentage
                        except ObjectDoesNotExist:
                            pass

                    # Handle wallet payment
                    if payment_method == 'wallet':
                        wallet = Wallet.objects.get(user=request.user)
                        if wallet.balance >= total_price_usd:
                            wallet.balance -= total_price_usd
                            wallet.save()

                            
                            order = Order.objects.create(
                            user=request.user,
                            total_price=total_price_usd,  # Store total price in USD
                            payment_method=payment_method,
                            status='Pending',
                            coupon_code=cart.coupon_code if cart.coupon_code else '',
                            discount_percentage=discount_percentage,
                            address_line_1=address.address_line_1,
                            address_line_2=address.address_line_2,
                            city=address.city,
                            country=address.country,
                            postal_code=address.postal_code,
                            razorpay_order_id=razorpay_order_id,  # Save the Razorpay order ID
                            payment_status='Pending',
                           )
                            # Create order items from cart items
                            for cart_item in cart.items.all():
                                OrderItem.objects.create(
                                    order=order,
                                    variant=cart_item.variant,
                                    quantity=cart_item.quantity
                                )
                                # Update stock after saving the order item
                                cart_item.variant.stock = F('stock') - cart_item.quantity
                                cart_item.variant.save(update_fields=['stock'])

                            # Clear the cart
                            cart.items.all().delete()
                            cart.coupon_code = None
                            cart.discount_amount = Decimal(0)
                            cart.discounted_price = Decimal(0)
                            cart.save()
                            order.payment_status = 'Completed'
                            order.status = 'Confirmed'
                            order.save()
                            WalletTransaction.objects.create(
                                wallet=wallet,
                                transaction_type='Debit',
                                amount=total_price_usd,
                                description=f"Payment for order {order.uuid}"
                            )
                            messages.success(request, "Order placed successfully!")
                            return redirect('order_summary', order_id=order.id)
                        else:
                            messages.error(request, "Insufficient balance in wallet.")
                            return redirect('checkout')

                    # Create the order
                    order = Order.objects.create(
                        user=request.user,
                        total_price=total_price_usd,  # Store total price in USD
                        payment_method=payment_method,
                        status='Pending',
                        coupon_code=cart.coupon_code if cart.coupon_code else '',
                        discount_percentage=discount_percentage,
                        address_line_1=address.address_line_1,
                        address_line_2=address.address_line_2,
                        city=address.city,
                        country=address.country,
                        postal_code=address.postal_code,
                        razorpay_order_id=razorpay_order_id,  # Save the Razorpay order ID
                        payment_status='Pending',
                    )
                    
                    # Create order items from cart items
                    for cart_item in cart.items.all():
                        OrderItem.objects.create(
                            order=order,
                            variant=cart_item.variant,
                            quantity=cart_item.quantity
                        )
                        # Update stock after saving the order item
                        cart_item.variant.stock = F('stock') - cart_item.quantity
                        cart_item.variant.save(update_fields=['stock'])

                    # Clear the cart
                    cart.items.all().delete()
                    cart.coupon_code = None
                    cart.discount_amount = Decimal(0)
                    cart.discounted_price = Decimal(0)
                    cart.save()

                    

                    # Handle online payment
                    if payment_method == 'online_payment':
                        if payment_status == 'Failed':
                            order.payment_status = 'Failed'
                            order.save()
                            messages.error(request, "Payment failed. Please try again.")
                            return redirect('order_summary', order_id=order.id)
                        else:
                            payment_success, message = handle_online_payment(order, razorpay_order_id, razorpay_payment_id, razorpay_signature)
                            print(f"Payment success status: {payment_success}, Message: {message}")  # Debug print
                            if payment_success:
                                order.payment_status = 'Completed'
                                order.save()
                                return redirect('order_summary', order_id=order.id)
                            else:
                                order.payment_status = 'Failed'
                                order.save()
                                messages.error(request, message)
                                return redirect('order_summary', order_id=order.id)
                    else:
                        # For cash on delivery
                        return redirect('order_summary', order_id=order.id)
                    
            except ValidationError as e:
                messages.error(request, str(e))
                return redirect('checkout')

        else:
            messages.error(request, "Your cart is empty.")
            return redirect('checkout')

    return redirect('checkout')


@login_required
def order_summary(request, order_id):
    print("Order ID:", order_id)
    order = get_object_or_404(Order, id=order_id)
    items = order.items.all()
   
    if order.total_price != sum(item.get_subtotal() for item in items):
        total_price = order.total_price  # If a discount was applied, use the stored total price in the order
    else:
        total_price = sum(item.get_subtotal() for item in items)  # If no discount was applied, recalculate total price

    context = {
        'order': order, 
        'items': items, 
        'total_price': total_price,
        'razorpay_key': settings.RAZORPAY_KEY_ID,
        }
    return render(request, 'order/order_summary.html',context)


@login_required
def confirm_order(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        order = get_object_or_404(Order, id=order_id, user=request.user)
        order.status = 'Confirmed'
        order.save()
        return render(request, 'order/order_success.html')
    return redirect('home')

@csrf_exempt
@login_required
def retry_payment(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("Received data:", data)  # Debug print
            order_id = data.get('order_id')
            total_price = data.get('total_price')

            if not (order_id and total_price):
                return JsonResponse({'error': 'Missing order_id or total_price'}, status=400)

            order = get_object_or_404(Order, id=order_id, user=request.user)

            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            total_price = float(total_price)  # Ensure total_price is a float
            amount_in_paisa = int(total_price * 100)  # Convert to paisa

            razorpay_order = client.order.create({
                'amount': amount_in_paisa,
                'currency': 'INR',
                'payment_capture': '1'
            })

            order.razorpay_order_id = razorpay_order['id']
            order.payment_status = 'completed'
            order.save()

            return JsonResponse({
                'order_id': razorpay_order['id'],
                'amount': razorpay_order['amount']
            })
        except json.JSONDecodeError as e:
            print("JSON decoding error:", e)  # Debug print
            return JsonResponse({'error': 'Invalid JSON data in request body'}, status=400)
        except Exception as e:
            print("Exception:", e)  # Debug print
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)
    
#user profile order details view
@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, uuid=order_id, user=request.user)
    items = order.items.all()
    # Check if the invoice download button should be displayed
    show_invoice_button = order.status in ['Delivered', 'Returned']
    return render(request, 'order/order_detail.html', {'order': order,'items': items,'show_invoice_button': show_invoice_button})

#================================== Razorpay ====================================

@csrf_exempt
@login_required
def create_razorpay_order(request):
    if request.method == "POST":
        data = json.loads(request.body)
        total_price_usd = data.get('total_price')
        address_id = data.get('address_id')

        # Fetch real-time USD to INR conversion rate
        response = requests.get('https://api.exchangerate-api.com/v4/latest/USD')
        exchange_data = response.json()
        usd_to_inr_rate = exchange_data['rates']['INR']
        total_price_inr = total_price_usd * usd_to_inr_rate

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        try:
            razorpay_order = client.order.create({
                "amount": int(total_price_inr * 100),  # Amount in paise
                "currency": "INR",
                "payment_capture": 1
            })
            print(f"Razorpay order created: {razorpay_order}")  # Debug print
            return JsonResponse({
                "order_id": razorpay_order['id'],
                "amount": razorpay_order['amount']
            })
        except Exception as e:
            print(f"Error creating Razorpay order: {e}")  # Debug print
            return JsonResponse({"error": "Failed to create Razorpay order"}, status=500)
    return JsonResponse({"error": "Invalid request"}, status=400)
#============================ Cancel Order=====================

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, uuid=order_id, user=request.user)
    if order.status in ['Pending', 'Confirmed']:
        try:
            with transaction.atomic():
                # Get the user's wallet
                try:
                    user_wallet = Wallet.objects.get(user=request.user)
                except ObjectDoesNotExist:
                    # If the wallet does not exist, create a new one
                    user_wallet = Wallet.objects.create(user=request.user)

                # Iterate over order items and add quantity back to variant stock
                for item in order.items.all():
                    item.variant.stock += item.quantity
                    item.variant.save()
                
                # If the payment method was online or wallet, refund the paid amount to the wallet
                if order.payment_method in ['online_payment', 'wallet']:
                    refund_amount = order.total_price
                    user_wallet.balance = F('balance') + refund_amount
                    user_wallet.save()

                    # Create a wallet transaction for the refund
                    refund_description = f"Refund for cancelled order {order.uuid}"
                    WalletTransaction.objects.create(
                        wallet=user_wallet,
                        transaction_type='Credit',
                        amount=refund_amount,
                        description=refund_description
                    )

                # Set order status to Cancelled
                order.status = 'Cancelled'
                order.save()
                
                # Redirect back to the profile page with a success message
                messages.success(request, 'Order cancelled successfully.')
                return redirect('accounts:account_dashboard')
        except Exception as e:
            # Handle any potential errors during the transaction
            return render(request, 'order/error.html', {'message': str(e)})
    else:
        # If the order is not pending or confirmed, display an error message
        return render(request, 'order/error.html', {'message': 'Cannot cancel this order.'})
    
#========================= Return Order =================================

@login_required
def return_order(request, order_id):
    order = get_object_or_404(Order, uuid=order_id, user=request.user)

    if order.status == 'Delivered':
        try:
            with transaction.atomic():

                # Set order status to 'Requested' and request for return
                order.return_status = 'Requested'
                order.save()

                # Redirect back to the profile page with a success message
                messages.success(request, 'Order returned successfully requested.')
                return redirect('accounts:account_dashboard')
        except Exception as e:
            return render(request, 'order/error.html', {'message': str(e)})
    else:
        # If the order is not delivered, display an error message
        return render(request, 'order/error.html', {'message': 'Cannot return this order as it is not yet delivered.'})
    

#=================================SALES REPORT========================================#


# generating sales report with custom date filter.

def generate_sales_report(request):
    form = SalesReportFilterForm(request.GET or None)
    orders = Order.objects.all()

    if form.is_valid():
        date_filter = form.cleaned_data['date_filter']
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']

        now = timezone.now()

        if date_filter == 'daily':
            # Convert start and end dates to the correct timezone
            start_date = timezone.localdate()  # Today's date
            start_date = timezone.make_aware(datetime.combine(start_date, datetime.min.time()))
            end_date = start_date + timedelta(days=1)
        elif date_filter == 'weekly':
            start_date = now - timedelta(days=now.weekday())
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=7)
        elif date_filter == 'monthly':
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            next_month = now.replace(day=28) + timedelta(days=4)  # ensures to get the next month
            end_date = next_month - timedelta(days=next_month.day - 1)
        elif date_filter == 'yearly':
            start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date.replace(year=start_date.year + 1)
        elif date_filter == 'custom' and start_date and end_date:
            start_date = timezone.make_aware(datetime.combine(start_date, datetime.min.time()))
            end_date = timezone.make_aware(datetime.combine(end_date, datetime.max.time()))

        orders = orders.filter(created_at__range=[start_date, end_date])
    orders = orders.order_by('-created_at')
    total_sales = orders.aggregate(total_sales=Sum('total_price'))['total_sales'] or 0

    total_discount = 0
    for order in orders:
        original_price_total = sum(item.variant.price * item.quantity for item in order.items.all())
        total_discount += original_price_total - order.total_price

    total_sales = round(total_sales, 2)
    total_discount = round(total_discount, 2)
    order_count = orders.count()

    context = {
        'form': form,
        'orders': orders,
        'total_sales': total_sales,
        'total_discount': total_discount,
        'order_count': order_count,
    }
    return render(request, 'admin_panel/orders/sales_report.html', context)

# downloading pdf of sales report
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Sales Report', 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(10)

    def chapter_body(self, headers, data):
        # Adjust column widths and height
        column_widths = [25, 30, 25, 20, 25, 25, 35]
        line_height = 10

        if len(headers) != len(column_widths):
            raise ValueError("Number of headers does not match the number of column widths")

        # Add table headers
        self.set_font('Arial', 'B', 10)
        for idx, header in enumerate(headers):
            self.cell(column_widths[idx], line_height, header, 1)
        self.ln()

        # Add table data
        self.set_font('Arial', '', 10)
        for row in data:
            if len(row) != len(headers):
                print(f"Row length: {len(row)}, Headers length: {len(headers)}")  # Debug statement
                raise ValueError("Number of data columns does not match number of headers")

            for idx, datum in enumerate(row):
                self.cell(column_widths[idx], line_height, str(datum), 1)
            self.ln()

def download_pdf_report(request):
    form = SalesReportFilterForm(request.GET or None)
    orders = Order.objects.all()

    if form.is_valid():
        date_filter = form.cleaned_data['date_filter']
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']

        now = timezone.now()

        if date_filter == 'daily':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
        elif date_filter == 'weekly':
            start_date = now - timedelta(days=now.weekday())
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=7)
        elif date_filter == 'monthly':
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            next_month = now.replace(day=28) + timedelta(days=4)  # ensures to get the next month
            end_date = next_month - timedelta(days=next_month.day - 1)
        elif date_filter == 'yearly':
            start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date.replace(year=start_date.year + 1)
        elif date_filter == 'custom' and start_date and end_date:
            start_date = timezone.make_aware(datetime.combine(start_date, datetime.min.time()))
            end_date = timezone.make_aware(datetime.combine(end_date, datetime.max.time()))

        orders = orders.filter(created_at__range=[start_date, end_date])
    orders = orders.order_by('-created_at')
    total_sales = orders.aggregate(total_sales=Sum('total_price'))['total_sales'] or 0
    total_discount = 0
    for order in orders:
        original_price_total = sum(item.variant.price * item.quantity for item in order.items.all())
        total_discount += original_price_total - order.total_price

    total_sales = round(total_sales, 2)
    total_discount = round(total_discount, 2)
    order_count = orders.count()

    headers = [
        'Order ID', 'User', 'Total Price', 'Status', 'Return Status',
        'Coupon Code', 'Discount Percentage'
    ]
    data = [
        [
            order.id,
            order.user.username,
            f"${order.total_price}",
            order.status,
            order.return_status,
            order.coupon_code,
            f"{order.discount_percentage}%",
           
        ] for order in orders 
    ]

    pdf = PDF()
    pdf.add_page()
    pdf.chapter_title('Sales Report')
    pdf.chapter_body(headers, data)

    # Store PDF content in a BytesIO stream
    pdf_output = BytesIO()
    pdf.output(pdf_output)

    # Set response headers
    response = HttpResponse(pdf_output.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'

    return response


# downloading excel sheet of sales report
def download_excel_report(request):
    form = SalesReportFilterForm(request.GET or None)
    orders = Order.objects.all()

    if form.is_valid():
        date_filter = form.cleaned_data['date_filter']
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']

        now = timezone.now()

        if date_filter == 'daily':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
        elif date_filter == 'weekly':
            start_date = now - timedelta(days=now.weekday())
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=7)
        elif date_filter == 'monthly':
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            next_month = now.replace(day=28) + timedelta(days=4)  # ensures to get the next month
            end_date = next_month - timedelta(days=next_month.day - 1)
        elif date_filter == 'yearly':
            start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date.replace(year=start_date.year + 1)
        elif date_filter == 'custom' and start_date and end_date:
            start_date = timezone.make_aware(datetime.combine(start_date, datetime.min.time()))
            end_date = timezone.make_aware(datetime.combine(end_date, datetime.max.time()))

        orders = orders.filter(created_at__range=[start_date, end_date])
    orders = orders.order_by('-created_at')
    excel_data = []

    for order in orders:
        for item in order.items.all():
            excel_data.append({
                'Order ID': order.id,
                'User': order.user.username,
                'Total Price': order.total_price,
                'Status': order.status,
                'Return Status': order.return_status,
                'Coupon Code': order.coupon_code,
                'Discount Percentage': order.discount_percentage,
                'Product': item.variant.product.product_name,
                'Variant': item.variant.name,
                'Quantity': item.quantity,
                'Price': item.variant.price,
                'Discounted Price': item.variant.discounted_price,
            })

    df = pd.DataFrame(excel_data)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=sales_report.xlsx'
    df.to_excel(response, index=False)

    return response

# ==================================== Download Invoice ================================ #

class InvoicePDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Invoice', 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(10)

    def chapter_body(self, body):
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, body)
        self.ln()

    def add_order_items(self, items):
        self.set_font('Arial', 'B', 10)
        self.cell(40, 10, 'Product', 1)
        self.cell(30, 10, 'Price', 1)
        self.cell(20, 10, 'Quantity', 1)
        self.cell(30, 10, 'Subtotal', 1)
        self.ln()
        
        self.set_font('Arial', '', 10)
        for item in items:
            self.cell(40, 10, item.variant.name, 1)
            self.cell(30, 10, f"${item.variant.price}", 1)
            self.cell(20, 10, str(item.quantity), 1)
            self.cell(30, 10, f"${item.get_subtotal()}", 1)
            self.ln()

@login_required
def download_invoice(request, order_id):
    order = get_object_or_404(Order, uuid=order_id, user=request.user)
    items = order.items.all()
    
    pdf = InvoicePDF()
    pdf.add_page()
    pdf.chapter_title(f'Invoice for Order {order.uuid}')
    pdf.chapter_body(f'Order Date: {order.created_at}\n'
                     f'Address: {order.address_line_1}, {order.address_line_2}, {order.city}, {order.country}, {order.postal_code}\n'
                     f'Order Status: {order.status}\n'
                     f'Return Status: {order.return_status}\n'
                     f'Discount Price: ${order.total_price}\n'
                     f'Payment Method: {order.payment_method}')
    
    pdf.add_order_items(items)

    # Store PDF content in a BytesIO stream
    pdf_output = BytesIO()
    pdf.output(pdf_output)

    # Set response headers
    response = HttpResponse(pdf_output.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order.uuid}.pdf"'
    return response