from django.db import models
from django.utils import timezone
from category.models import Category
from django.conf import settings
from django.core.validators import MaxValueValidator

class ProductOffer(models.Model):
    name = models.CharField(max_length=100)
    discount_percentage = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(100)])
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField()
    product = models.ForeignKey('store.Product', on_delete=models.CASCADE)  # Use string reference for model relationship to break circular import


    def is_active(self):
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date
    
    


class CategoryOffer(models.Model):
    name = models.CharField(max_length=100)
    discount_percentage = models.PositiveIntegerField(default=0,validators=[MaxValueValidator(100)])
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def is_active(self):
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date
    


class ReferralOffer(models.Model):
    name = models.CharField(max_length=100)
    referrer_reward = models.PositiveIntegerField()
    referee_reward = models.PositiveIntegerField()
    eligibility_conditions = models.TextField()
    expiration_date = models.DateField()
    referrer = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='referrals', on_delete=models.CASCADE)
    
    def has_expired(self):
        """
        Check if the referral offer has expired.
        """
        today = timezone.now().date()
        return self.expiration_date < today
    
    
