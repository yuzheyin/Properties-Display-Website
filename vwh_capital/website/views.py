from django.shortcuts import render, get_object_or_404,redirect

# Create your views here.
from django.apps import apps
from django.http import Http404, HttpRequest, HttpResponse
# from vwh_capital.website.models import *


def properties(request):
    return render(request, 'website/properties.html')


def details(request):
    return render(request, 'website/details.html')


def favourite(request):
    return render(request, 'website/favourite.html')


def home(request):
    return render(request, 'website/index.html')


def login(request):
    return render(request, 'website/login.html')


def signup(request):
    return render(request, 'website/signup.html')