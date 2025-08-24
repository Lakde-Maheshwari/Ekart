from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from store.models import Product
from category.models import Category
from carts.models import CartItem
from carts.views import ___cart_id
from django.db.models import Q
from .forms import ReviewForm
from .models import ReviewRating
from django.shortcuts import render,redirect
from django.contrib import messages
from orders.models import OrderProduct
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
        raise 
    
    # querying the product reviews from the particular user for the above single product 
    if request.user.is_authenticated : 
        try:
            orderproduct = OrderProduct.objects.filter(user=request.user,product_id=single_product.id).exists()
        except OrderProduct.DoesNotExist:
            orderproduct = None
    else:
        orderproduct = None

    reviews  = ReviewRating.objects.filter(product_id = single_product.id,status = True)
    # product_gallery = 
    context = {
        'single_product': single_product,
        'in_cart': in_cart, 
        'orderproduct': orderproduct,
        'reviews': reviews,
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

def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thank you! Your review has been updated.')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Thank you! Your review has been submitted.')
                return redirect(url)

