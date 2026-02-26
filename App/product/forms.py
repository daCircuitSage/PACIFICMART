from django import forms 
from .models import ReviewRating, Product
from category.models import Category

class Reviewform(forms.ModelForm):
    # Define rating field to accept float values (0.5, 1, 1.5, ... 5)
    rating = forms.FloatField(
        required=True,
        min_value=0.5,
        max_value=5.0
    )
    
    class Meta:
        model = ReviewRating
        fields = ['subject', 'review', 'rating']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'review': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'rating': forms.HiddenInput(),
        }
    
    def clean_rating(self):
        """Ensure rating is properly converted to float"""
        rating = self.cleaned_data.get('rating')
        if rating is not None:
            try:
                rating = float(rating)
                if rating < 0.5 or rating > 5.0:
                    raise forms.ValidationError('Rating must be between 0.5 and 5.0')
            except (ValueError, TypeError):
                raise forms.ValidationError('Invalid rating value')
        return rating


class VendorProductForm(forms.ModelForm):
    """Form for vendors to create products"""
    
    class Meta:
        model = Product
        fields = [
            'product_name',
            'product_slug', 
            'product_description',
            'product_price',
            'product_img',
            'stock',
            'product_category'
        ]
        widgets = {
            'product_name': forms.TextInput(attrs={'class': 'form-control'}),
            'product_slug': forms.TextInput(attrs={'class': 'form-control'}),
            'product_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'product_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'product_category': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        vendor = kwargs.pop('vendor', None)
        super(VendorProductForm, self).__init__(*args, **kwargs)
        
        # Filter categories if needed
        self.fields['product_category'].queryset = Category.objects.all()
        
        # Add placeholders
        self.fields['product_name'].widget.attrs['placeholder'] = 'Enter product name'
        self.fields['product_slug'].widget.attrs['placeholder'] = 'Enter product slug (URL-friendly)'
        self.fields['product_description'].widget.attrs['placeholder'] = 'Describe your product'
        self.fields['product_price'].widget.attrs['placeholder'] = '0.00'
        self.fields['stock'].widget.attrs['placeholder'] = 'Quantity in stock'
    
    def clean_product_slug(self):
        """Ensure slug is unique"""
        slug = self.cleaned_data.get('product_slug')
        if slug:
            # Check if slug already exists (excluding current product if editing)
            queryset = Product.objects.filter(product_slug=slug)
            if self.instance and self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise forms.ValidationError('A product with this slug already exists.')
        return slug
    
    def save(self, commit=True):
        """Save product with vendor and pending status"""
        product = super().save(commit=False)
        
        # Set vendor and status for new products
        if not product.pk:  # New product
            product.status = 'PENDING'  # Requires admin approval
        
        if commit:
            product.save()
        return product


class ProductApprovalForm(forms.Form):
    """Form for admin to approve/reject products"""
    
    rejection_reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Reason for rejection (if rejecting)...'})
    )