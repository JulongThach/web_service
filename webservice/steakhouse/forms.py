from django import forms
from .models import Order, OrderItem, Product

class OrderForm(forms.Form):
    customer_name = forms.CharField(max_length=100)
    phone_number = forms.CharField(max_length=20)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}))

# Formset for multiple products in the same order
OrderItemFormSet = forms.inlineformset_factory(
    Order,
    OrderItem,
    fields=('product', 'quantity'),
    extra=1,
    can_delete=True
)

class MessageForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput, label="Name")
    phone = forms.CharField(widget=forms.TextInput, label="Phone Number")
    subject = forms.CharField(widget=forms.TextInput, label="Subject")
    message = forms.CharField(widget=forms.Textarea, label="Your Message")