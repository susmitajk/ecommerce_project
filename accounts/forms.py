from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.core.validators import validate_email
from accounts.models import Account,Address
from phonenumber_field.formfields import PhoneNumberField
import re


User = get_user_model()

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={"placeholder": "First Name"}),
                                 required=True, help_text='Required. 30 characters or fewer.')
    last_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={"placeholder": "Last Name"}),
                                required=True, help_text='Required. 30 characters or fewer.')
    email = forms.EmailField(max_length=254, widget=forms.EmailInput(attrs={"placeholder": "Email"}), required=True,
                             help_text='Required. Enter a valid email address.')
    phone_number = PhoneNumberField(widget=forms.TextInput(attrs={"placeholder": "Phone(+91)"}), required=True,
                                    help_text='Required. Enter a valid phone number.')
    password1 = forms.CharField(max_length=30, widget=forms.PasswordInput(attrs={"placeholder": "Password"}),
                                required=True, help_text='Required. 30 characters or fewer.')
    password2 = forms.CharField(max_length=30, widget=forms.PasswordInput(attrs={"placeholder": "Confirm Password"}),
                                required=True, help_text='Required. 30 characters or fewer.')
    username = forms.CharField(max_length=30, widget=forms.TextInput(attrs={"placeholder": "Username"}), required=True,
                               help_text='Required. 30 characters or fewer.')

    class Meta:
        model = Account
        fields = ['username', 'first_name', 'last_name', 'email','phone_number','password1','password2']
        labels = {'email': 'Email'}

  


    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')

        # Check if the first name contains any leading space
        if first_name.strip() != first_name:
            raise ValidationError(_('First name should not contain leading spaces.'))

        # Check if the first name contains only letters
        if not first_name.isalpha():
            raise ValidationError(_('First name should only contain letters.'))
        
        return first_name
    


    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')

        # Check if the last name contains any leading space
        if last_name.strip() != last_name:
            raise ValidationError(_('Last name should not contain leading spaces.'))
        
        if not last_name.isalpha():
            raise ValidationError(_('Last name should only contain letters '))
        
        return last_name
    

    
    def clean_username(self):
        username = self.cleaned_data.get("username")
        if not username.isalnum():
            raise ValidationError('Username should only contain letters and/or numbers.')
        
        return username
    

    # def clean_email(self):
    #     email = self.cleaned_data.get('email')
    #     try:
    #         validate_email(email)
    #     except ValidationError:
    #         raise forms.ValidationError("Invalid email address")
        
    #     return email
    
    # def clean_phone_number(self):
    #     phone_number = self.cleaned_data.get('phone_number')

    #     if not phone_number.isdigit():
    #         raise forms.ValidationError('Phone number must contain only numeric characters.')
        
    #     # Check if the phone number is exactly 10 digits long
    #     if len(phone_number) != 10:
    #         raise forms.ValidationError('Phone number must be exactly 10 digits long.')


    #     # Check if the phone number contains no spaces or special characters
    #     if not re.match(r'^\d+$', phone_number):
    #         raise forms.ValidationError('Phone number must not contain spaces or special characters.')
        
    #     return phone_number


# Form for Editing User Profile
class ProfileEditForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, label='First Name', required=True)
    last_name = forms.CharField(max_length=30, label='Last Name', required=True)
    username = forms.CharField(max_length=30, label='User Name', required=True)
    email = forms.EmailField(max_length=254, label='Email', required=True)
    phone_number = PhoneNumberField(label='Phone Number', required=True)
    

    class Meta:
        model = Account
        fields = ['username', 'first_name', 'last_name','username','email', 'phone_number']
    
    def __init__(self, *args, **kwargs):
        super(ProfileEditForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['readonly'] = True  # Setting  email field to read-only because its an verified email

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')

        # Strip leading and trailing spaces
        first_name = first_name.strip()

        # Check if the first name contains only letters
        if not first_name.isalpha():
            raise ValidationError(_('First name should only contain letters.'))

        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')

        # Strip leading and trailing spaces
        last_name = last_name.strip()

        # Check if the last name contains only letters
        if not last_name.isalpha():
            raise ValidationError(_('Last name should only contain letters.'))

        return last_name
    
    def clean_username(self):
        username = self.cleaned_data.get("username")
        if not username.isalnum():
            raise ValidationError('Username should only contain letters and/or numbers.')
        
        return username
    

# Form for Creating and Adding New Address
address_regex = re.compile(r'^[a-zA-Z0-9\s\.,#/-]+$')

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['address_line_1', 'address_line_2', 'city', 'state', 'postal_code', 'country', 'is_default']
        widgets = {
            'address_line_1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address Line 1'}),
            'address_line_2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address Line 2'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Postal Code'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_address_line_1(self):
        address_line_1 = self.cleaned_data.get('address_line_1')

        if not address_regex.match(address_line_1):
            raise forms.ValidationError("Invalid characters in address line 1.")
        
        return address_line_1

    def clean_address_line_2(self):
        address_line_2 = self.cleaned_data.get('address_line_2')

        if address_line_2 and not address_regex.match(address_line_2):
            raise forms.ValidationError("Invalid characters in address line 2.")
        
        return address_line_2

    def clean_city(self):
        city = self.cleaned_data.get('city')
        if not city.isalpha():
            raise ValidationError(_('City name should only contain alphabetic characters.'))
        return city

    def clean_state(self):
        state = self.cleaned_data.get('state')
        if not state.isalpha():
            raise ValidationError(_('State name should only contain alphabetic characters.'))
        return state

    def clean_postal_code(self):
        postal_code = self.cleaned_data.get('postal_code')

        if not postal_code.isdigit():
            raise forms.ValidationError("Postal code must contain only digits.")
        
        return postal_code

    def clean_country(self):
        country = self.cleaned_data.get('country')
        if not country.isalpha():
            raise ValidationError(_('Country name should only contain alphabetic characters.'))
        return country