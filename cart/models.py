from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings
from store.models import ProductVariant

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    coupon_code = models.CharField(max_length=50, blank=True, null=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    

    def get_total_price(self):
        total = sum(item.get_subtotal() for item in self.items.all())
        return total if total else 0
    
    def get_total_discount_amount(self):
        total_discount = sum(item.variant.price - item.variant.discounted_price for item in self.items.all() if item.variant.discounted_price)
        return total_discount
    
    def get_discount_percentage(self):
        if self.get_total_price() > 0:
            return (self.get_total_discount_amount() / self.get_total_price()) * 100
        return 0

    def remove_item(self, variant_id):
        try:
            item = self.items.get(variant_id=variant_id)
            item.delete()
        except CartItem.DoesNotExist:
            raise ValidationError("Item not found in the cart.")

    def __str__(self):
        return f" Cart for {self.user}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def get_subtotal(self):
        price = self.variant.discounted_price if self.variant.discounted_price else self.variant.price
        return self.quantity * price
    
    def get_variant_image(self):
        return self.variant.images.first().image if self.variant.images.exists() else None

    def save(self, *args, **kwargs):
        # Check stock availability
        if self.quantity > self.variant.stock:
            raise ValidationError(f"Only {self.variant.stock} items left in stock for {self.variant.product.product_name}.")

        # Check maximum quantity per user for the cart
        max_qty_per_user = 5  # You can change this value based on your requirements
        total_qty_for_user = CartItem.objects.filter(
            cart__user=self.cart.user,
            variant=self.variant,
            cart__isnull=False  
        ).exclude(id=self.id).aggregate(total=models.Sum('quantity'))['total'] or 0

        if total_qty_for_user + self.quantity > max_qty_per_user:
            raise ValidationError(f"Maximum {max_qty_per_user} items allowed per user for {self.variant.product.product_name}.")

        super(CartItem, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.variant} in Cart for {self.cart.user}"
