from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Order, OrderItem
from .forms import OrderForm, OrderItemFormSet
from .utils import send_telegram_message  # We'll create this later
from django.forms import modelformset_factory
import random

from .cart import Cart


# Show Product List
def product_list(request):
    products = Product.objects.all()
    return render(request, 'steakhouse/product_list.html', {'products': products})

def add_to_cart(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.add(product)
    return redirect('product_list')


def remove_from_cart(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('view_cart')


def view_cart(request):
    cart = Cart(request)
    return render(request, 'steakhouse/cart.html', {'cart': cart})

# Handle Order Form
def order_form(request):
    cart = Cart(request)
    if not cart.cart:
        return redirect('product_list')  # cart empty
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            # Generate Receipt Number
            order.receipt_number = f"REC-{random.randint(100000, 999999)}"
            order.save()

            # Save Order Items
            for product_id, item in cart.cart.items():
                product = Product.objects.get(id=product_id)
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item['quantity']
                )

            message = f"🧾 *New Order Received*\n\nReceipt No: {order.receipt_number}\n"
            message += f"Name: {order.customer_name}\nPhone: {order.phone_number}\nAddress: {order.address}\n\n*Order Items:*\n"

            for item in cart:
                message += f"- {item['name']} x{item['quantity']} = ${item['total_price']}\n"

            message += f"\n*Total Price:* ${cart.get_total_price()}"
            send_telegram_message(message)
            cart.clear()
            return redirect('product_list')

    else:
        form = OrderForm()

    return render(request, 'steakhouse/order_form.html', {'form': form})


# Success Page
def order_success(request):
    return render(request, 'steakhouse/order_success.html')
