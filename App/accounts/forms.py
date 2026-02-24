from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from .models import Account, UserProfile
from factors_Ecom.validators import validate_bangladeshi_phone_number
import re


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Enter Password',
        'class': 'form-control',
        'minlength': '8',
        'required': True
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirm Password',
        'class': 'form-control',
        'minlength': '8',
        'required': True
    }))
    
    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'email', 'phone_number']
    
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if first_name:
            # Remove extra whitespace and validate
            first_name = ' '.join(first_name.split())
            if len(first_name) < 2:
                raise forms.ValidationError("First name must be at least 2 characters long.")
            if not re.match(r'^[a-zA-Z\s]+$', first_name):
                raise forms.ValidationError("First name should only contain letters.")
        return first_name
    
    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if last_name:
            # Remove extra whitespace and validate
            last_name = ' '.join(last_name.split())
            if len(last_name) < 2:
                raise forms.ValidationError("Last name must be at least 2 characters long.")
            if not re.match(r'^[a-zA-Z\s]+$', last_name):
                raise forms.ValidationError("Last name should only contain letters.")
        return last_name
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower().strip()
            # Check if email already exists
            if Account.objects.filter(email__iexact=email).exists():
                # Check if the existing user is inactive (not verified)
                existing_user = Account.objects.get(email__iexact=email)
                if not existing_user.is_active:
                    raise forms.ValidationError(
                        "This email is already registered but not verified. "
                        "Please check your email or <a href='/accounts/resend-verification/'>resend verification</a>."
                    )
                else:
                    raise forms.ValidationError("An account with this email already exists.")
        return email
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            # Remove any whitespace
            phone_number = phone_number.strip()
            validate_bangladeshi_phone_number(phone_number)
            
            # Check if phone number already exists
            if Account.objects.filter(phone_number=phone_number).exists():
                raise forms.ValidationError("An account with this phone number already exists.")
        return phone_number
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            # Use Django's built-in password validation
            try:
                validate_password(password)
            except ValidationError as e:
                raise forms.ValidationError(list(e.messages))
            
            # Additional custom validation
            if not re.search(r'[A-Z]', password):
                raise forms.ValidationError("Password must contain at least one uppercase letter.")
            if not re.search(r'[a-z]', password):
                raise forms.ValidationError("Password must contain at least one lowercase letter.")
            if not re.search(r'\d', password):
                raise forms.ValidationError("Password must contain at least one digit.")
            if password.lower() in ['password', '12345678', 'qwerty', 'admin']:
                raise forms.ValidationError("Password is too common. Please choose a stronger password.")
        return password
    
    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password:
            if password != confirm_password:
                raise forms.ValidationError("Passwords do not match.")
        
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter First Name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter Last Name'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Enter Phone Number'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter Email Address'
        
        # Add HTML5 validation attributes
        self.fields['first_name'].widget.attrs['required'] = True
        self.fields['last_name'].widget.attrs['required'] = True
        self.fields['email'].widget.attrs['required'] = True
        self.fields['phone_number'].widget.attrs['required'] = True
        
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ('first_name','last_name','phone_number')

    def clean_phone_number(self):
        # this is validating the user's mobile number so 
        # that a user cannot pass direct string as mobile number
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            validate_bangladeshi_phone_number(phone_number)
        return phone_number

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


class UserProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False, error_messages = {'invalid':("Image files only")}, widget=forms.FileInput)
    class Meta:
        model = UserProfile
        fields = ('address_line_1', 'address_line_2', 'city', 'state', 'country', 'profile_picture')

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'