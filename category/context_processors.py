from .models import Category
from django.shortcuts import render

def menu_links(request):
    links = Category.objects.all()
    return dict(links=links)
