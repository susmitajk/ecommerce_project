from django.db import models
from category.models import Category
from django.core.exceptions import ValidationError

# Create your models here.

# Brand
class Brand(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# #coupon
# class Coupon(models.Model):
#     code = models.CharField(max_length=20)
#     discount = models.DecimalField(max_digits=5, decimal_places=2)
#     brand = models.ForeignKey(Brand, related_name='brand_coupons', on_delete=models.CASCADE)

#Liquor Type
class Type(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# Main Product
class Product(models.Model):
    product_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(max_length=500, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, related_name='brand_products', on_delete=models.CASCADE)
    liquor_type = models.ForeignKey(Type, on_delete=models.CASCADE)

    def __str__(self):
        return self.product_name
    

# Product Variant Field Validation Logic 
def validate_age_within_range(value):
    if not (0 <= value <= ProductVariant.MAX_AGE):
        raise ValidationError(f'Age must be between 0 and {ProductVariant.MAX_AGE}.')

def validate_proof_within_range(value):
    if not (0 <= value <= ProductVariant.MAX_PROOF):
        raise ValidationError(f'Proof must be between 0 and {ProductVariant.MAX_PROOF}.')

def validate_volume_within_range(value):
    if not (0 <= value <= ProductVariant.MAX_VOLUME):
        raise ValidationError(f'Volume must be between 0 and {ProductVariant.MAX_VOLUME}.')

def validate_price_within_range(value):
    if not (0 <= value <= ProductVariant.MAX_PRICE):
        raise ValidationError(f'Price must be between 0 and {ProductVariant.MAX_PRICE}.')

def validate_stock_within_range(value):
    if not (0 <= value <= ProductVariant.MAX_STOCK):
        raise ValidationError(f'Stock must be between 0 and {ProductVariant.MAX_STOCK}.')

class ProductVariant(models.Model):
    # Upper limits for variant fields
    MAX_AGE = 200
    MAX_PRICE = 1000
    MAX_STOCK = 1000
    MAX_PROOF = 200
    MAX_VOLUME = 5000  # Assuming a maximum volume of 5000 milliliters

    product = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE)
    age = models.PositiveIntegerField(validators=[validate_age_within_range])
    proof = models.DecimalField(max_digits=5, decimal_places=2, validators=[validate_proof_within_range])
    volume = models.DecimalField(max_digits=5, decimal_places=2, validators=[validate_volume_within_range])
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[validate_price_within_range])
    stock = models.PositiveIntegerField(validators=[validate_stock_within_range])

    def __str__(self):
        return self.product.product_name

# Multiple Product Image
class Image(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, related_name='images', on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(upload_to='photos/product_images')
