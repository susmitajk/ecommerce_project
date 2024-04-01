from django.contrib import admin
from .models import Brand, Type, Product, ProductVariant, Image


# Register your models here.
admin.site.register(Brand)
admin.site.register(Type)

class ProductAdmin(admin.ModelAdmin):
    list_display = ('id','product_name', 'category', 'brand', 'liquor_type')
    list_display_links = ('id','product_name')
    prepopulated_fields = {'slug':('product_name',)}

admin.site.register(Product, ProductAdmin)

admin.site.register(ProductVariant)
admin.site.register(Image)
