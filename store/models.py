from django.db import models
from category.models import Category
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.text import slugify
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
    is_deleted = models.BooleanField(default=False)
    image = models.ImageField(upload_to='photos/products')
    

    def get_url(self):
        return reverse('product_detail', args=[self.category.slug, self.slug])
    
    def soft_delete(self, *args, **kwargs):
        # Soft delete by setting is_deleted to True
        self.is_deleted = True
        self.save()
    
    def restore(self):
        # Restore by setting is_deleted to False
        self.is_deleted = False
        self.save()
    
    def permanent_delete(self):
        # Perform a permanent delete
        super(Product, self).delete()
    
    objects = models.Manager()
    available_objects = models.Manager()  # For retrieving non-deleted items
    
   # slugify the product_name field
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.product_name)
        super(Product, self).save(*args, **kwargs)

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
    name = models.CharField(max_length=200, unique=True)
    age = models.PositiveIntegerField(validators=[validate_age_within_range])
    proof = models.DecimalField(max_digits=5, decimal_places=2, validators=[validate_proof_within_range])
    volume = models.DecimalField(max_digits=5, decimal_places=2, validators=[validate_volume_within_range])
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[validate_price_within_range])
    stock = models.PositiveIntegerField(validators=[validate_stock_within_range])
    is_active = models.BooleanField(default=True)

    
    def __str__(self):
        return self.name

# Multiple Product Image
class ProductImage(models.Model):
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='photos/productvariant')

    def __str__(self):
        return f"Image for {self.variant.name}"

