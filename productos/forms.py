from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["title", "description", "marca", "price","stock","image","nuevo"]

        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }
