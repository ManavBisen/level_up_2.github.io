from django import forms
from .models import ShopItem

class ShopItemForm(forms.ModelForm):
    class Meta:
        model = ShopItem
        fields = ['name', 'description', 'price', 'stock', 'file', 'file_type']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
    
    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price <= 0:
            raise forms.ValidationError("Price must be greater than 0.")
        return price
    
    def clean_stock(self):
        stock = self.cleaned_data.get('stock')
        if stock < 0:
            raise forms.ValidationError("Stock cannot be negative.")
        return stock
