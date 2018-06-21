from django.shortcuts import render, get_object_or_404,redirect

# Create your views here.
from django.apps import apps
from django.http import Http404, HttpRequest, HttpResponse
# from vwh_capital.website.models import *


def index(request):
    return render(request, 'website/properties.html')