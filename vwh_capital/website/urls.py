"""
@Author Yuzhe Yin
@Date 06/15/2018
VWH property listing website
"""
from django.urls import path, re_path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    path('accounts/login/', auth_views.LoginView.as_view(template_name='website/login.html', redirect_field_name='index/'), name='login'),
    path('logout/', auth_views.logout_then_login, name='logout'),
    path('', views.home, name='index'),
    path('properties/', views.properties, name='properties'),
    path('reset/', views.reset, name='reset'),
    path('signup/', views.register, name='register'),
    path('forget/', views.forget, name='forget'),
    re_path(r'^main_picture/(?P<id>[a-zA-Z0-9]+)$', views.get_main_picture, name='main_picture'),
    re_path(r'^picture/(?P<id>[a-zA-Z0-9]+)$', views.get_picture, name='picture'),
    re_path(r'^details/(?P<id>[a-zA-Z0-9]+)$', views.details, name='details'),
    re_path(r'^favorite/(?P<id>[a-zA-Z0-9]+)$', views.favorite, name='favorite'),
    re_path(r'^add_favorite/(?P<id>[a-zA-Z0-9]+)$', views.add_favorite, name='add_favorite'),
    re_path(r'^remove_favorite/(?P<id>[a-zA-Z0-9]+)$', views.remove_favorite, name='remove_favorite'),
    re_path(r'^confirm/(?P<username>[a-zA-Z0-9]+)/(?P<token>[a-z0-9\-]+)/$', views.confirm_registration, name='confirm'),
    re_path(r'^reset_credential/(?P<username>[a-zA-Z0-9]+)/(?P<token>[a-z0-9\-]+)/$', views.reset_credential, name='reset_credential'),
    re_path(r'^user_message/(?P<id>[a-zA-Z0-9]+)$', views.user_message, name='user_message'),
    re_path(r'^commit_reset_credential/(?P<username>[a-zA-Z0-9]+)/(?P<token>[a-z0-9\-]+)/$', views.commit_reset_credential, name='commit_reset_credential')
]

