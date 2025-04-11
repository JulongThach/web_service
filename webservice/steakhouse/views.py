from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Order, OrderItem
from .forms import OrderForm, OrderItemFormSet
from .utils import send_telegram_message  # We'll create this later
from django.forms import modelformset_factory
from django.views.decorators.http import require_POST
from django.http import JsonResponse

import random

from .cart import Cart

# Show Product List
def product_list(request):
    popular = Product.objects.filter(category='Popular')
    mixed = Product.objects.filter(category='Mixed Food')
    steak = Product.objects.filter(category='Steak')
    suit = Product.objects.filter(category='Suit')
    spaghetti = Product.objects.filter(category='Spaghetti')
    add = Product.objects.filter(category='Add')
    drink = Product.objects.filter(category='Drink')
    context = {
        'popular' : popular,
        'mixed' : mixed,
        'drink' : drink,
        'suit' : suit,
        'spaghetti' : spaghetti,
        'add' : add,
        'steak' : steak,
    }
    return render(request, 'steakhouse/product_list.html', context)

#Add to cart
def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    cart = Cart(request)
    cart.add(product, quantity=1)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'cart_item_count': len(cart)})
    
    return redirect('product_list')

#Update to cart
def update_cart(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
        
    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity'))
            if quantity > 0:
                cart.update(product, quantity)
            else:
                cart.remove(product) 
        except (ValueError, TypeError):
            pass  # Handle invalid input gracefully

    return redirect('view_cart') 

#Remove from cart
def remove_from_cart(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('view_cart')

# View Cart
def view_cart(request):
    cart_data = request.session.get('cart', {})
    cart_items = []
    total_price = 0

    for product_id, item in cart_data.items():
        product = get_object_or_404(Product, id=product_id)
        quantity = item['quantity']
        price = product.price * quantity
        total_price += price
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'price': price,
        })

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = Order.objects.create(
                customer_name=form.cleaned_data['customer_name'],
                phone_number=form.cleaned_data['phone_number'],
                address=form.cleaned_data['address']
            )
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    quantity=item['quantity']
                )
                
            map_url = f"https://www.google.com/maps?q={order.latitude},{order.longitude}"
            # Send Telegram Message (if set up)
            message = f"🧾 *New Order Received*\n\nReceipt No: {order.receipt_number}\n"
            message += f"Name: {order.customer_name}\nPhone: {order.phone_number}\nAddress: {order.address}\n\n*Order Items:*\n"
            for item in cart_items:
                message += f"- {item['product'].name} x{item['quantity']} = ${item['price']:.2f}\n"
            message += f"\n*Total Price:* ${total_price:.2f}"
            send_telegram_message(message)

            # Clear session cart
            request.session['cart'] = {}

            return redirect('order_success', order_id=order.id)
    else:
        form = OrderForm()

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'form': form,
    }
    return render(request, 'steakhouse/cart.html', context)

# Success Page
def order_success(request, order_id):
    order = Order.objects.get(id=order_id)
    order_items = order.items.all()
    
    items_with_totals = []
    total_order = 0

    for item in order_items:
        item_total = item.product.price * item.quantity
        total_order += item_total
        items_with_totals.append({
            'name': item.product.name,
            'quantity': item.quantity,
            'price': item.product.price,
            'total': item_total,
        })
        
    context = {
        'order': order,
        'order_items': order_items,
        'order_items': items_with_totals,
        'total_order': total_order,
    }
    return render(request, 'steakhouse/order_success.html', context)

#Clear Cart
@require_POST
def clear_cart(request):
    request.session['cart'] = {} 
    request.session.modified = True
    return redirect('view_cart')