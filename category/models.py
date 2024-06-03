from django.db import models
from django.urls import reverse
from django.utils.text import slugify

# Create your models here.

class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(max_length=255, blank=True)
    cat_image = models.ImageField(upload_to='photos/categories', blank=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'
        ordering = ['-id']

    def get_url(self):
            return reverse('product_list_by_category', args=[self.slug])
    
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
        super(Category, self).delete()
    
    objects = models.Manager()
    available_objects = models.Manager()  # For retrieving non-deleted items

    # slugify the product_name field
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.category_name)
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return self.category_name