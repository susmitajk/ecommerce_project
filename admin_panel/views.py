import json
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from accounts.models import Account,Wallet,WalletTransaction
from category.models import Category
from .category_views import category_list
from .product_views import brand_list,type_list,product_list,product_variant_list,product_image_list
from orders.models import Order,OrderItem 
from django.contrib import messages
import logging
from django.db import transaction
from django.db.models import F, Sum, OuterRef, Subquery, Value,CharField,Count
from django.db.models.functions import Coalesce
from django.core.exceptions import ObjectDoesNotExist
from store.models import Product, ProductImage,ProductVariant
from django.utils import timezone
from datetime import timedelta,datetime
import logging




# Configure logging
logger = logging.getLogger(__name__)


# Create your views here.

def filter_sales_data(period):
    today = timezone.localdate()
    print(f"Today's date (localdate): {today}")

    if period == 'yearly':
        start_date = today - timedelta(days=365)
    elif period == 'monthly':
        start_date = today - timedelta(days=30)
    elif period == 'weekly':
        start_date = today - timedelta(days=7)
    else:
        start_date = today
    
    # Make the start date timezone-aware at the start of the day
    start_date = timezone.make_aware(datetime.combine(start_date, datetime.min.time()))
    print(f"Start date for period '{period}': {start_date}")

    if period == 'daily':
        # Ensure `today` is a datetime and timezone-aware
        start_datetime = timezone.make_aware(datetime.combine(today, datetime.min.time()))
        end_datetime = timezone.make_aware(datetime.combine(today, datetime.max.time()))
        print(f"Filtering orders from {start_datetime} to {end_datetime}")

        # Filter sales for today within the whole day range
        sales_data = Order.objects.filter(created_at__range=(start_datetime, end_datetime)).annotate(total_sales=Sum('total_price')).order_by('created_at__date')
        print(f"Orders for today: {list(Order.objects.filter(created_at__range=(start_datetime, end_datetime)))}")
    else:
        # Filter sales for the period (yearly, monthly, weekly)
        sales_data = Order.objects.filter(created_at__date__gte=start_date).values('created_at__date').annotate(total_sales=Sum('total_price')).order_by('created_at__date')

    # Extract sales dates and totals
    if period == 'daily':
        sales_dates = [today.strftime('%Y-%m-%d')]
        sales_totals = [float(sum([order.total_price for order in Order.objects.filter(created_at__range=(start_datetime, end_datetime))]))]
    else:
        sales_dates = [data['created_at__date'].strftime('%Y-%m-%d') for data in sales_data]
        sales_totals = [float(data['total_sales']) for data in sales_data]

    print(f"Period: {period}")
    print(f"Sales Dates: {sales_dates}")
    print(f"Sales Totals: {sales_totals}")

    return sales_dates, sales_totals

def DashboardView(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        period = request.GET.get('period', 'daily')
        sales_dates, sales_totals = filter_sales_data(period)
        status_data = Order.objects.values('status').annotate(count=Count('status'))
        order_statuses = [data['status'] for data in status_data]
        order_counts = [data['count'] for data in status_data]

        return JsonResponse({
            'sales_dates': sales_dates,
            'sales_totals': sales_totals,
            'order_statuses': order_statuses,
            'order_counts': order_counts,
        })

    period = 'daily'
    sales_dates, sales_totals = filter_sales_data(period)
    status_data = Order.objects.values('status').annotate(count=Count('status'))
    order_statuses = [data['status'] for data in status_data]
    order_counts = [data['count'] for data in status_data]

    # Calculate total revenue, total orders, and total products
    total_revenue = float(Order.objects.aggregate(total_revenue=Sum('total_price'))['total_revenue'] or 0)
    total_orders = Order.objects.count()
    total_products = Product.objects.count()
    total_categories = Category.objects.count()

    context = {
        'sales_dates': json.dumps(sales_dates),
        'sales_totals': json.dumps(sales_totals),
        'order_statuses': json.dumps(order_statuses),
        'order_counts': json.dumps(order_counts),
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'total_products': total_products,
        'total_categories': total_categories,
    }

    return render(request, 'admin_panel/admin_dashboard.html', context)
#======================================= Best selling ====================================== #
def best_selling(request):
    image_subquery = ProductImage.objects.filter(
        variant=OuterRef('pk')
    ).values('image')[:1]

    default_image_url = settings.MEDIA_URL + 'photos/productvariant/default_image.jpg'

    top_products = ProductVariant.objects.annotate(
        total_quantity=Sum('order_items__quantity'),
        variant_image=Coalesce(
            Subquery(image_subquery, output_field=CharField()), 
            Value('photos/productvariant/180-ml-milk-bottle.jpg', output_field=CharField())
        )
    ).values(
        'product__product_name', 
        'product__slug',
        'product__category__category_name',
        'product__brand__name',
        'product__id',
        'id',  # Variant ID
        'price',  # Variant price 
        'name',
        'variant_image',
        'total_quantity'  # Include total_quantity for ordering
    ).order_by('-total_quantity')[:10]

    # Prefix the variant_image with MEDIA_URL
    for product in top_products:
        product['variant_image'] = settings.MEDIA_URL + product['variant_image']

    top_categories = Product.objects.values(
        'category__category_name',
        'category__cat_image'
    ).annotate(
        total_quantity=Coalesce(Sum('variants__order_items__quantity'), Value(0))
    ).exclude(total_quantity=0).order_by('-total_quantity')[:10]

    top_brands = Product.objects.values(
        'brand__name'
    ).annotate(
        total_quantity=Coalesce(Sum('variants__order_items__quantity'), Value(0))
    ).exclude(total_quantity=0).order_by('-total_quantity')[:10]

    # Debug statement to print top_categories
    print("Top Categories: ", top_categories)

    context = {
        'top_products': top_products,
        'top_categories': top_categories,
        'top_brands': top_brands,
        'MEDIA_URL': settings.MEDIA_URL,
    }
    return render(request, 'admin_panel/best_selling.html', context)


#======================================= User Management =================================== #
# To list Users
def user_list(request):
    user = Account.objects.all()
    context = {'user': user}
    return render(request, 'admin_panel/user/user_list.html', context)

# Activate the user
def activate_user(request, user_id):
    user = Account.objects.get(id=user_id)
    user.activate_account()  # Activation function defined in the model
    logging.debug(f"User {user.username} reactivated")  # Add this line
    messages.success(request, f"User {user.username} has been reactivated.")
    return redirect('user_list')

# Deactivate the user
def deactivate_user(request, user_id):
    user = Account.objects.get(id=user_id)
    if user.is_admin:
        messages.error(request, "Admin user cannot be deactivated.")
    else:
        user.deactivate_account()  # Deactivation function defined in the model
        logging.debug(f"User {user.username} deactivated")  # Add this line
        messages.success(request, f"User {user.username} has been deactivated successfully.")
    return redirect('user_list')

# =================================== order management================================================= #


# listing Orders
def order_list(request):
    orders = Order.objects.all().order_by('-created_at')   # Retrieve all orders from the database
    context = {'orders': orders}
    return render(request, 'admin_panel/orders/order_list.html', context)

#edit order status
def edit_order(request, order_id):
    order = get_object_or_404(Order, uuid=order_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['Pending', 'Confirmed', 'Shipped', 'Delivered', 'Cancelled']:
            try:
                with transaction.atomic():
                    order.status = new_status
                    order.save()

                    if new_status == 'Confirmed':
                        # Deduct stock for order items
                        for item in order.items.all():
                            item.variant.stock -= item.quantity
                            item.variant.save()
                    elif new_status == 'Cancelled':
                        # Iterate over order items and add quantity back to variant stock
                        for item in order.items.all():
                            item.variant.stock += item.quantity
                            item.variant.save()

                        # Refund the paid amount to the wallet if the payment method was online or wallet
                        if order.payment_method in ['online_payment', 'wallet']:
                            refund_amount = order.total_price
                            logger.info(f"Refund amount: {refund_amount}")

                            try:
                                user_wallet = Wallet.objects.get(user=order.user)
                            except ObjectDoesNotExist:
                                # If the wallet does not exist, create a new one
                                user_wallet = Wallet.objects.create(user=order.user)
                            
                            logger.info(f"User wallet before refund: {user_wallet.balance}")

                            # Add the refund amount to the user's wallet balance
                            user_wallet.balance = F('balance') + refund_amount
                            user_wallet.save()
                            
                            user_wallet.refresh_from_db()  # Refresh to get the updated balance
                            logger.info(f"User wallet after refund: {user_wallet.balance}")

                            # Create a wallet transaction for the refund
                            refund_description = f"Refund for cancelled order {order.uuid}"
                            WalletTransaction.objects.create(
                                wallet=user_wallet,
                                transaction_type='Credit',
                                amount=refund_amount,
                                description=refund_description
                            )

                    # If all operations are successful, redirect with success message
                    messages.success(request, 'Order status updated successfully.')
                    if new_status == 'Cancelled':
                        messages.success(request, 'Order cancelled and refund processed successfully.')
                    return redirect('order_list')

            except Exception as e:
                logger.error(f"Error processing order update: {e}")
                messages.error(request, f'Error processing order update: {e}')
                return redirect('edit_order', order_id=order_id)

    context = {'order': order}
    return render(request, 'admin_panel/orders/edit_order.html', context)


#view order details
def view_order(request, order_id):
    order = get_object_or_404(Order, uuid=order_id)
    return render(request, 'admin_panel/orders/view_order.html', {'order': order})


def review_return(request, order_id):
    order = get_object_or_404(Order, uuid=order_id)

    if request.method == 'POST':
        if 'accept' in request.POST:
            # Check if the order is delivered and the return status is requested
            if order.status == 'Delivered' and order.return_status == 'Requested':
                try:
                    with transaction.atomic():
                        # Retrieve the user's wallet
                        try:
                            user_wallet = Wallet.objects.get(user=request.user)
                        except ObjectDoesNotExist:
                            # If the wallet does not exist, create a new one
                            user_wallet = Wallet.objects.create(user=request.user)

                        # Iterate over order items and add quantity back to variant stock
                        for item in order.items.all():
                            item.variant.stock += item.quantity
                            item.variant.save()

                        # Refund the paid amount to the wallet
                        refund_amount = order.total_price
                        user_wallet.balance = F('balance') + refund_amount
                        user_wallet.save()

                        # Create a wallet transaction for the refund
                        refund_description = f"Refund for returned order {order.uuid}"
                        WalletTransaction.objects.create(
                            wallet=user_wallet,
                            transaction_type='Credit',
                            amount=refund_amount,
                            description=refund_description
                        )

                        # Set order return status to 'Approved'
                        order.return_status = 'Approved'
                        order.save()

                        # Add any additional actions upon accepting return request

                        messages.success(request, 'Return request approved successfully.')
                        return redirect('order_list')
                except Exception as e:
                    messages.error(request, f'Error approving return request: {e}')

        elif 'reject' in request.POST:
            # Update the return status to 'Rejected'
            order.return_status = 'Rejected'
            order.save()
            # Add any additional actions upon rejecting return request
            messages.success(request, 'Return request rejected successfully.')
            return redirect('order_list')

    # If the request method is not POST, render the template normally
    return render(request, 'admin_panel/orders/review_return.html', {'order': order})