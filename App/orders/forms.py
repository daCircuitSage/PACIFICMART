from django import forms
from .models import Order
from factors_Ecom.validators import is_valid_bangladeshi_phone

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'phone', 'email', 'address_line_1', 'address_line_2', 'country', 'state', 'city', 'order_note']
          
    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if is_valid_bangladeshi_phone(phone):
            return phone
        raise forms.ValidationError('Please enter a valid Bangladeshi phone number (01XXXXXXXXX)')
