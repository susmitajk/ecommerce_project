from django import forms
from offers.models import ProductOffer, CategoryOffer, ReferralOffer
from django.forms import DateInput, ValidationError

class ProductOfferForm(forms.ModelForm):
    class Meta:
        model = ProductOffer
        fields = ['name', 'discount_percentage', 'start_date', 'end_date', 'product']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'text', 'class': 'form-control', 'id': 'id_start_date'}),
            'end_date': forms.DateInput(attrs={'type': 'text', 'class': 'form-control', 'id': 'id_end_date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super(ProductOfferForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
    
    def clean_discount_percentage(self):
        discount_percentage = self.cleaned_data.get('discount_percentage')
        if discount_percentage > 100:
            raise forms.ValidationError("Discount percentage cannot exceed 100")
        return discount_percentage
    

class CategoryOfferForm(forms.ModelForm):
    class Meta:
        model = CategoryOffer
        fields = ['name', 'discount_percentage', 'start_date', 'end_date', 'category']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'text', 'class': 'form-control', 'id': 'id_start_date'}),
            'end_date': forms.DateInput(attrs={'type': 'text', 'class': 'form-control', 'id': 'id_end_date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super(CategoryOfferForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
    
    def clean_discount_percentage(self):
        discount_percentage = self.cleaned_data.get('discount_percentage')
        if discount_percentage > 100:
            raise forms.ValidationError("Discount percentage cannot exceed 100")
        return discount_percentage
    

class ReferralOfferForm(forms.ModelForm):
    class Meta:
        model = ReferralOffer
        fields = ['name', 'referrer_reward', 'referee_reward', 'eligibility_conditions', 'expiration_date', 'referrer']
    
    def __init__(self, *args, **kwargs):
        super(ReferralOfferForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
    
    
