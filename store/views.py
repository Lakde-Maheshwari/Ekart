from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

from store.models import Product
from category.models import Category
from carts.models import CartItem
from carts.views import ___cart_id
from django.db.models import Q

# Store page view
def store(request, category_slug=None):
    category = None
    products = None

    if category_slug is not None:
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=category, is_available=True)
        paginator = Paginator(products, 6)  # Show 6 products per page
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
    else:
        products = Product.objects.filter(is_available=True).order_by('id')
        paginator = Paginator(products, 6)  # Show 6 products per page
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()

    context = {
        'products': paged_products,
        'product_count': product_count,
        
    }

    return render(request, 'store/store.html', context)


# Product detail view
def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=___cart_id(request),product = single_product).exists()
    except Exception as e:
        raise e

    context = {
        'single_product': single_product,
        'in_cart': in_cart, 
    }

    return render(request, 'store/product_detail.html', context=context)


def search(request):
    products = []
    product_count = 0

    if 'q' in request.GET:
        keyword = request.GET['q']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(
                Q(description__icontains=keyword) | Q(product_name__icontains=keyword)
            )
            product_count = products.count()

    context = {
        'products': products,
        'product_count': product_count,
    }

    return render(request, 'store/store.html', context)


