from django.urls import path, re_path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    path('accounts/login/', auth_views.LoginView.as_view(template_name='website/login.html', redirect_field_name='index/'), name='login'),
    # path('accounts/login/', views.login, name='login'),
    path('logout/', auth_views.logout_then_login, name='logout'),
    path('', views.home, name='index'),
    path('details/', views.details, name='details'),
    path('favorite/', views.favorite, name='favorite'),
    path('properties/', views.properties, name='properties'),
    path('signup/', views.register, name='register'),
    # # for loading image from admin
    # re_path(r'^images/.+$', views.images, name='images'),
    re_path(r'^picture/(?P<id>[a-zA-Z0-9]+)$', views.get_picture, name='picture'),
    re_path(r'^confirm/(?P<username>[a-zA-Z0-9]+)/(?P<token>[a-z0-9\-]+)/$', views.confirm_registration, name='confirm')
]

