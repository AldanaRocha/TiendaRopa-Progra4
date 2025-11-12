# chat_ai/forms.py
from django import forms

class ChatForm(forms.Form):
    message = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 2}), 
        label="Tu mensaje"
    ) 