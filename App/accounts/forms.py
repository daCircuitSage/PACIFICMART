from django import forms
from .models import Account, UserProfile, Vendor
from factors_Ecom.validators import validate_bangladeshi_phone_number


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Enter Password',
        'class': 'form-control',
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirm Password',
        'class': 'form-control',
    }))
    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'email', 'phone_number']
    
    def clean_phone_number(self):
        # this is validating the user's mobile number so 
        # that a user cannot pass direct string as mobile number
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            validate_bangladeshi_phone_number(phone_number)
        return phone_number
    

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password != confirm_password:
            raise forms.ValidationError(
                'Password does not match'
            )

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter First Name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter Last Name'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Enter Phone Number'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter Email Address'
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


class VendorRegistrationForm(forms.ModelForm):
    """Form for vendor registration with NID card uploads"""
    
    class Meta:
        model = Vendor
        fields = [
            'business_name', 
            'business_category', 
            'business_description',
            'business_phone', 
            'business_email',
            'store_location',
            'store_city',
            'store_state',
            'nid_card_front',
            'nid_card_back'
        ]
        widgets = {
            'business_description': forms.Textarea(attrs={'rows': 4}),
            'store_location': forms.Textarea(attrs={'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        super(VendorRegistrationForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            if field not in ['nid_card_front', 'nid_card_back']:
                self.fields[field].widget.attrs['class'] = 'form-control'
        
        # Add placeholders
        self.fields['business_name'].widget.attrs['placeholder'] = 'Enter your business name'
        self.fields['business_phone'].widget.attrs['placeholder'] = 'Business contact number'
        self.fields['business_email'].widget.attrs['placeholder'] = 'Business email address'
        self.fields['store_location'].widget.attrs['placeholder'] = 'Physical store location (optional)'
        self.fields['store_city'].widget.attrs['placeholder'] = 'City'
        self.fields['store_state'].widget.attrs['placeholder'] = 'State/Division'
    
    def clean_business_phone(self):
        """Validate business phone number"""
        phone_number = self.cleaned_data.get('business_phone')
        if phone_number:
            validate_bangladeshi_phone_number(phone_number)
        return phone_number
    
    def clean(self):
        """Form-level validation"""
        cleaned_data = super().clean()
        
        # Ensure business email is different from personal email if user is logged in
        business_email = cleaned_data.get('business_email')
        
        return cleaned_data


class VendorApprovalForm(forms.ModelForm):
    """Form for admin to approve/reject vendors"""
    
    class Meta:
        model = Vendor
        fields = ['admin_notes']
        widgets = {
            'admin_notes': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter reason for approval or rejection...'})
        }