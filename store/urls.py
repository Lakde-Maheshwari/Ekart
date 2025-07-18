from django.urls import path 
from . import views
from .views import store,product_detail

urlpatterns = [
    path('',views.store,name='store'),
    path('category/<slug:category_slug>',views.store,name='products_by_category'),
    path('category/<slug:category_slug>/<product_slug>/',views.product_detail,name='product_detail'),
    path('search/' , views.search, name='search'
    ),
]