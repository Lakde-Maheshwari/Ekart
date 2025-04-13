from django.shortcuts import render
from store.models import Product
from category.models import Category
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator    


# Create your views here.
def store(request,category_slug=None):
    category = None
    products = None

    if category_slug != None:
        categories = get_object_or_404(Category,slug=category_slug) 
        products = Product.objects.all().filter(category=categories,is_available=True) 
        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True)
        product_count = products.count()

    context  = {
        'products': products,
        'product_count': product_count,
    }

    return render(request,'store/store.html',context)


def product_detail(request,category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
    except Exception as e:
        raise e
    
    context = {
        'single_product': single_product,
    }
    return render(request,'store/product_detail.html',context=context)

