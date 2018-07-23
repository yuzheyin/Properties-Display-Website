from django.shortcuts import render, get_object_or_404,redirect

# Create your views here.
from django.apps import apps
from django.http import Http404, HttpRequest, HttpResponse
# from vwh_capital.website.models import *
from django.contrib.auth.tokens import default_token_generator
# Used to send mail from within Django
from django.core.mail import send_mail
from .forms import *
from .models import *
from django.db import transaction
from django.db.models import Q
from django.urls import reverse
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from django.core import serializers


@transaction.atomic
def register(request):
    context = {}
    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['form'] = RegistrationForm()
        return render(request, 'website/signup.html', context)

    # Creates a bound form from the request POST parameters and makes the
    # form available in the request context dictionary.
    form = RegistrationForm(request.POST)
    context['form'] = form

    # Validates the form.
    if not form.is_valid():
        return render(request, 'website/signup.html', context)

    # At this point, the form data is valid.  Register and login the user.
    new_user = User.objects.create_user(username=form.cleaned_data['username'],
                                        password=form.cleaned_data['password1'],
                                        email=form.cleaned_data['email'],
                                        first_name=form.cleaned_data['first_name'],
                                        last_name=form.cleaned_data['last_name'])
    # new_user.is_active = False
    new_user.save()

    new_profile = Profile(user=new_user,
                          longitude=form.cleaned_data['longitude'],
                          latitude=form.cleaned_data['latitude']
                          )

    new_profile.save()

    # Generate a one-time use token and an email message body
    token = default_token_generator.make_token(new_user)

    email_body = """
        Please click the link below to verify your email address and
        complete the registration of your account:
        http://{host}{path}
        """.format(host=request.get_host(),
                   path=reverse('confirm', args=(new_user.username, token)))

    send_mail(subject="Verify your email address",
              message=email_body,
              from_email="yuzhe.yin@vwhcapital.com",
              recipient_list=[new_user.email])

    context['email'] = form.cleaned_data['email']

    return render(request, 'website/confirmation.html', context)


@transaction.atomic
def confirm_registration(request, username, token):
    user = get_object_or_404(User, username=username)

    # Send 404 error if token is invalid
    if not default_token_generator.check_token(user, token):
        raise Http404

    # Otherwise token was valid, activate the user.
    user.is_active = True
    user.save()
    login(request, user)
    most_viewed = Property.objects.order_by('-viewed_times')[1:4]
    new_added = Property.objects.order_by('-creation_time')[:3]
    context = {'most_viewed': most_viewed, 'new_added': new_added}
    properties = Property.objects.order_by('-viewed_times')
    if len(properties) != 0:
        cover = {'cover': Property.objects.order_by('-viewed_times')[0]}
        context.update(cover)
    return render(request, 'website/index.html', context)



@transaction.atomic
def properties(request):
    properties_all = Property.objects.order_by('-creation_time')
    most_viewed = Property.objects.order_by('-viewed_times')[:4]

    paginator = Paginator(properties_all, 1)
    page = request.GET.get('page', 1)

    try:
        properties = paginator.page(page)
    except PageNotAnInteger:
        properties = paginator.page(1)
    except EmptyPage:
        properties = paginator.page(paginator.num_pages)

    form = FilterForm()
    context = {'properties': properties, 'form': form, 'most_viewed': most_viewed}

    return render(request, 'website/properties.html', context)


@login_required
@transaction.atomic
def details(request, id):
    property = Property.objects.get(id=id)
    property.viewed_times += 1
    property.save()
    similar = Property.objects.filter(address__locality__state=property.address.locality.state).exclude(id=id)[:3]
    pictures = property.pictures.all()
    profile = Profile.objects.get(user=request.user)
    c_list = profile.favorite_list.all()
    most_viewed = Property.objects.order_by('-viewed_times')[:4]
    if property in c_list:
        is_added = True
    else:
        is_added = False

    context = {'property': property, 'pictures': pictures, 'similar': similar, 'is_added': is_added, 'most_viewed': most_viewed}
    return render(request, 'website/details.html', context)


def home(request):
    most_viewed = Property.objects.order_by('-viewed_times')[1:4]
    new_added = Property.objects.order_by('-creation_time')[:3]
    context = {'most_viewed': most_viewed, 'new_added': new_added}
    properties = Property.objects.order_by('-viewed_times')
    if len(properties) != 0:
        cover = {'cover': Property.objects.order_by('-viewed_times')[0]}
        context.update(cover)
    return render(request, 'website/index.html', context)


@login_required
@transaction.atomic
def favorite(request, id):
    profile = Profile.objects.get(user__id=id)
    properties = profile.favorite_list.all()
    message = ""
    if len(properties) == 0:
        message = "Nothing in Your Collection"
    context = {'properties': properties, 'message': message}
    return render(request, 'website/favorite.html', context)


@login_required
@transaction.atomic
def add_favorite(request, id):
    errors = []
    if request.method == 'POST':
        request.user.profile.favorite_list.add(Property.objects.get(id=id))
    else:
        errors.append('Wrong method')
    return redirect('details', id=id)


@login_required
@transaction.atomic
def remove_favorite(request, id):
    errors = []
    if request.method == 'POST':
        request.user.profile.favorite_list.remove(Property.objects.get(id=id))
    else:
        errors.append('Wrong method')
    return redirect('details', id=id)

@transaction.atomic
def get_main_picture(request, id):
    property = get_object_or_404(Property, id=id)
    pictures = property.pictures.all()
    picture = 0
    for pic in pictures:
        if pic.title == 'main':
            picture = pic.image
            break
    # picture = Picture.objects.filter(id=id).image
    return HttpResponse(picture, content_type='image/png')


@transaction.atomic
def get_picture(request, id):
    picture = get_object_or_404(Picture, id=id)
    image = picture.image

    return HttpResponse(image, content_type='image/png')
