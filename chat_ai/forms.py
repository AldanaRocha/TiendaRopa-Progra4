# chat_ai/forms.py
from django import forms
# IMPORTANTE: Se necesita importar tu modelo Product para PriceSuggestForm si lo requiriera, 
# pero la guía lo define como un formulario base sin ModelForm.

# 1. Formulario para la Sugerencia de Precios
class PriceSuggestForm(forms.Form):
    title = forms.CharField(max_length=200)
    description = forms.CharField(widget=forms.Textarea, required=False)
    marca = forms.CharField(max_length=100, required=False)
    current_price = forms.DecimalField(max_digits=12, decimal_places=2, required=False)

# 2. Formulario para el Chat Asistente
class ChatForm(forms.Form):
    message = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 2}), 
        label="Tu mensaje"
    )