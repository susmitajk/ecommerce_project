from django.contrib import admin
from .models import Brand, Type, Product, ProductVariant, ProductImage
import admin_thumbnails

# @admin_thumbnails.thumbnail('image')
# class ProductImageInline(admin.TabularInline):
#     model = ProductImage
#     extra = 1


# Register your models here.
admin.site.register(Brand)
admin.site.register(Type)

class ProductAdmin(admin.ModelAdmin):
    list_display = ('id','product_name', 'category', 'brand', 'liquor_type')
    list_display_links = ('id','product_name')
    prepopulated_fields = {'slug':('product_name',)}
    # inlines = [ProductImageInline]

admin.site.register(Product, ProductAdmin)

admin.site.register(ProductVariant)
admin.site.register(ProductImage)
