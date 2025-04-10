from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Order, OrderItem
from .forms import OrderForm, OrderItemFormSet
from .utils import send_telegram_message  # We'll create this later
from django.forms import modelformset_factory
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
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0

    for product_id, item in cart.items():
        product = Product.objects.get(id=product_id)
        quantity = item['quantity']
        price = product.price * quantity
        total_price += price
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'price': price,
        })
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'steakhouse/cart.html', context)

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
            
            print("🛒 Cart data:")
            for item in cart:
                message += f"- {item['name']} x{item['quantity']} = ${item['total_price']:.2f}\n"

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
