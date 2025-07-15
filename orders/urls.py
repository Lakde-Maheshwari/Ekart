from django.urls import path
from . import views
from .views import place_order,payments,paypal_view

urlpatterns = [
    path('place_order/', views.place_order,name='place_order'),
    path('payments/', views.payments,name='payments'),
    path('paypal/', views.paypal_view, name='paypal'),

]