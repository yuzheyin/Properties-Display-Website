from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='index'),
    path('details/', views.details, name='details'),
    path('favourite/', views.favourite, name='favourite'),
    path('properties/', views.properties, name='properties'),
]