from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render,redirect
from store.models import Product,Variation
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.
def __cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    product_variation = []

    if request.method == 'POST':
        for key in request.POST:
            value = request.POST.get(key)  # ✅ Correct way to get dynamic key's value
            try:
                variation = Variation.objects.get(
                    product=product,
                    variation_category__iexact=key,
                    variation_value__iexact=value
                )
                product_variation.append(variation)
            except Variation.DoesNotExist:
                pass

    try:
        cart = Cart.objects.get(cart_id=__cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=__cart_id(request))
        cart.save()

    cart_item_qs = CartItem.objects.filter(product=product, cart=cart)

    if cart_item_qs.exists():
        # There are existing items with the same product
        found_match = False
        for item in cart_item_qs:
            existing_variation = list(item.variations.all())
            if sorted(existing_variation, key=lambda x: x.id) == sorted(product_variation, key=lambda x: x.id):
                item.quantity += 1
                item.save()
                found_match = True
                break

        if not found_match:
            item = CartItem.objects.create(product=product, quantity=1, cart=cart)
            if product_variation:
                item.variations.add(*product_variation)
            item.save()
    else:
        # No cart item for this product yet
        cart_item = CartItem.objects.create(product=product, cart=cart, quantity=1)
        if product_variation:
            cart_item.variations.add(*product_variation)
        cart_item.save()

    return redirect('cart')

def remove_cart(request,product_id):
    cart = Cart.objects.get(cart_id = __cart_id(request))
    product = get_object_or_404(Product,id = product_id)
    cart_item = CartItem.objects.get(product = product,cart = cart)
    
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    
    return redirect('cart')

def remove_cart_item(request,product_id):
    cart = Cart.objects.get(cart_id = __cart_id(request))
    product = get_object_or_404(Product,id = product_id)
    cart_item = CartItem.objects.filter(product = product,cart = cart)
    cart_item.delete()
    return redirect('cart')
 
def cart(request,Total = 0, quantity=0, cart_items=None):
    try:
        cart = Cart.objects.get(cart_id=__cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            Total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
    except Cart.ObjectDoesNotExist:
        pass
    context = {
        'Total': Total,
        'quantity': quantity,
        'cart_items': cart_items,
    }
    return render(request, 'store/cart.html',context=context)