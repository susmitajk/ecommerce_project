import uuid
from django.db import models
from django.conf import settings
from accounts.models import Address
from store.models import ProductVariant
from cart.models import CartItem
from django.core.exceptions import ValidationError
from django.db.models import F

class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    )

    PAYMENT_CHOICES = (
        ('cash_on_delivery', 'Cash on Delivery'),
        ('online_payment', 'Online Payment'),
        ('wallet', 'Wallet'),
    )

    RETURN_CHOICES = (
        ('Not Requested', 'Not Requested'),
        ('Requested', 'Requested'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )

    PAYMENT_STATUS_CHOICES = (
    ('Pending', 'Pending'),
    ('Failed', 'Failed'),
    ('Completed', 'Completed'),
)

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_CHOICES, default='cash_on_delivery')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    return_status = models.CharField(max_length=50, choices=RETURN_CHOICES, default='Not Requested')
    coupon_code = models.CharField(max_length=50, blank=True, null=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    razorpay_order_id = models.CharField(max_length=255, blank=True, null=True)  # New field for Razorpay order ID
    payment_status = models.CharField(max_length=50, choices=PAYMENT_STATUS_CHOICES, default='Pending')

    # Fields to store address details at the time of order placement
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)

    def __str__(self):
        return f"Order {self.uuid} - {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, related_name='order_items', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def get_subtotal(self):
        return self.quantity * self.variant.price
    
    def get_variant_image(self):
        return self.variant.images.first().image if self.variant.images.exists() else None

    def save(self, *args, **kwargs):
        # Check stock availability
        if self.quantity > self.variant.stock:
            raise ValidationError(f"Only {self.variant.stock} items left in stock for {self.variant.product.product_name}.")


        super(OrderItem, self).save(*args, **kwargs)

        # # Update stock after saving the order item
        # self.variant.stock = F('stock') - self.quantity
        # self.variant.save(update_fields=['stock'])

    def __str__(self):
        return f"{self.quantity} x {self.variant} in Order {self.order.uuid} for {self.order.user}"

