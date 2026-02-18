from django import forms 
from .models import ReviewRating

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