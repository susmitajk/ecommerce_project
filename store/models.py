from django.utils import timezone
from django.db import models
from category.models import Category
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.text import slugify
from django.conf import settings
# Create your models here.

# Brand
class Brand(models.Model):
    name = models.CharField(max_length=100)
    is_deleted = models.BooleanField(default=False)

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

    def __str__(self):
        return self.name

#Liquor Type
class Type(models.Model):
    name = models.CharField(max_length=100)
    is_deleted = models.BooleanField(default=False)

   


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
    featured = models.BooleanField(default=False)


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

    # to campare and get the best discount percentage from category offer and discount offer.
    def get_best_discount_percentage(self):
        from offers.models import CategoryOffer, ProductOffer  # lazy import inside the method to break from circular import.

        product_offers = ProductOffer.objects.filter(product=self, start_date__lte=timezone.now().date(), end_date__gte=timezone.now().date())
        category_offers = CategoryOffer.objects.filter(category=self.category, start_date__lte=timezone.now().date(), end_date__gte=timezone.now().date())
        
        max_product_discount = product_offers.aggregate(models.Max('discount_percentage'))['discount_percentage__max'] or 0
        max_category_discount = category_offers.aggregate(models.Max('discount_percentage'))['discount_percentage__max'] or 0

        return max(max_product_discount, max_category_discount)
    
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
    is_deleted = models.BooleanField(default=False)
    

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
    
    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews:
            total_rating = sum(review.rating for review in reviews)
            return total_rating / len(reviews)
        return 0
    
    # calculating discount price for each variant.
    @property
    def discounted_price(self):
        best_discount_percentage = self.product.get_best_discount_percentage()
        discount_amount = self.price * best_discount_percentage / 100
        return round(self.price - discount_amount, 2)
    
    @property
    def get_variant_image(self):
        return self.images.first().image.url if self.images.exists() else 'default_image_path'
        
    def __str__(self):
        return self.name

# Multiple Product Image
class ProductImage(models.Model):
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='photos/productvariant')
    is_deleted = models.BooleanField(default=False)

  

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

    def __str__(self):
        return f"Image for {self.variant.name}"


# Review Model
class Review(models.Model):
    RATING_CHOICES = [
        (1, '⭐'),
        (2, '⭐⭐'),
        (3, '⭐⭐⭐'),
        (4, '⭐⭐⭐⭐'),
        (5, '⭐⭐⭐⭐⭐'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, related_name='reviews', on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'variant')

    def __str__(self):
        return f"Review of {self.user}"