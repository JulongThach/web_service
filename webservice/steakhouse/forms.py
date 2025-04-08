from django import forms
from .models import Order, OrderItem, Product

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer_name', 'phone_number', 'address']

# Formset for multiple products in the same order
OrderItemFormSet = forms.inlineformset_factory(
    Order,
    OrderItem,
    fields=('product', 'quantity'),
    extra=1,
    can_delete=True
)
