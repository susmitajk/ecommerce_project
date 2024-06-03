from django import forms
from category.models import Category
from store.models import Product, ProductVariant, ProductImage, Brand , Type
from coupon_management.models import Coupon
from django.core.validators import RegexValidator
from django.forms import DateInput, ValidationError
import re
from datetime import time

# Category form
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        exclude = ['is_deleted']
        widgets = {
            'slug': forms.TextInput(attrs={'readonly': 'readonly'}),
        }
    cat_image = forms.ImageField(required=True)

    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        self.fields['category_name'].widget.attrs['placeholder'] = 'Type  Here'
        self.fields['description'].widget.attrs['placeholder'] = 'Type  Here'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

            
        # Add validators to category_name field to disallow spaces and underscores
        category_name_validator = RegexValidator(
            regex=r'^[\w\s]+$',  # Allow alphanumeric characters and spaces
            message='Category name must contain only alphanumeric characters and spaces.',
        )
        self.fields['category_name'].validators.append(category_name_validator)
    
    def clean_category_name(self):
        category_name = self.cleaned_data.get('category_name')
        if not any(char.isalnum() for char in category_name):
            raise ValidationError('Category name must contain at least one alphanumeric character.')
        return category_name

# Product Form
class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        exclude = ['is_deleted','created_date', 'modified_date']
        widgets = {
            'slug': forms.TextInput(attrs={'readonly': 'readonly'}),
        }

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.fields['product_name'].widget.attrs['placeholder'] = 'Type  Here'
        self.fields['description'].widget.attrs['placeholder'] = 'Type  Here'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

# product Variant form
class ProductVariantForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        fields = ['product', 'name', 'age', 'proof', 'volume', 'price', 'stock']
        exclude = ['is_active']
    
    def __init__(self, *args, **kwargs):
        super(ProductVariantForm, self).__init__(*args, **kwargs)
        
        # Populate the product dropdown with available products
        self.fields['product'].queryset = Product.objects.filter(is_deleted=False)
        
        # Add placeholders and classes to form fields
        placeholders = {
            'name': 'Type Here',
            'age': 'Type Here',
            'proof': 'Type Here',
            'volume': 'Type Here',
            'price': 'Type Here',
            'stock': 'Type Here',
        }
        
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
            self.fields[field].widget.attrs['placeholder'] = placeholders.get(field, '')

        # Add validators to name field to disallow spaces and underscores
        name_validator = RegexValidator(
            regex=r'^[\w\s]+$',  # Allow alphanumeric characters and spaces
            message='Name must contain only alphanumeric characters and spaces.',
        )
        self.fields['name'].validators.append(name_validator)
        
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not any(char.isalnum() for char in name):
            raise ValidationError('Name must contain at least one alphanumeric character.')
        return name


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        exclude = ['is_deleted']
        fields = ['variant', 'image']
        
    def __init__(self, *args, **kwargs):
        super(ProductImageForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
    

class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        exclude = ['is_deleted']
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super(BrandForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

class TypeForm(forms.ModelForm):
    class Meta:
        model = Type
        exclude = ['is_deleted']
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super(TypeForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


#Coupon Form
class CouponForm(forms.ModelForm):

    class Meta:
        model = Coupon
        exclude = ['usage_count','is_active']
        fields = ['code', 'start_date','expiry_date', 'offer_percentage', 'overall_usage_limit', 'limit_per_user','minimum_order_amount','maximum_order_amount']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'text', 'class': 'form-control', 'id': 'id_start_date'}),
            'expiry_date': forms.DateInput(attrs={'type': 'text', 'class': 'form-control', 'id': 'id_end_date'}),
        }
    

    def __init__(self, *args, **kwargs):
        super(CouponForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
    
    def clean_code(self):
        code = self.cleaned_data['code']

        # Length Restriction
        min_length = 6
        max_length = 10
        if len(code) < min_length or len(code) > max_length:
            raise forms.ValidationError(f"Coupon code must be between {min_length} and {max_length} characters long.")


        # # Uniqueness
        # if Coupon.objects.filter(code=code).exists():
        #     raise forms.ValidationError("Coupon code must be unique.")

        # Pattern Matching
        if not re.match(r'^[a-zA-Z0-9]*$', code):
            raise forms.ValidationError("Coupon code must contain both letters and numbers.")

        # Exclusion of Certain Characters
        excluded_characters = ['_', ' ']
        if any(char in code for char in excluded_characters):
            raise forms.ValidationError("Coupon code cannot contain underscores or spaces.")


        # Reserved Keywords
        reserved_keywords = ['invalid', 'expired', 'test']
        if code.lower() in reserved_keywords:
            raise forms.ValidationError("Coupon code cannot be a reserved keyword.")

        return code
    
    def clean_start_date(self):
        start_date = self.cleaned_data['start_date']
        return start_date.replace(hour=0, minute=0, second=0, microsecond=0)

    def clean_expiry_date(self):
        expiry_date = self.cleaned_data['expiry_date']
        return expiry_date.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    def clean_minimum_order_amount(self):
        minimum_order_amount = self.cleaned_data['minimum_order_amount']
        # Check if the value starts with 0
        if str(minimum_order_amount).startswith('0'):
            raise forms.ValidationError("Minimum order amount should not start with 0.")
        # Check if the value is negative
        if  minimum_order_amount < 0:
            raise forms.ValidationError("Minimum order amount cannot be negative.")
        return minimum_order_amount

    def maximum_order_amount(self):
        maximum_order_amount = self.cleaned_data['maximum_order_amount']
        # Check if the value starts with 0
        if str(maximum_order_amount).startswith('0'):
            raise forms.ValidationError("Maximum offer price should not start with 0.")
        # Check if the value is negative
        if  maximum_order_amount < 0:
            raise forms.ValidationError("Maximum offer price cannot be negative.")
        return maximum_order_amount

