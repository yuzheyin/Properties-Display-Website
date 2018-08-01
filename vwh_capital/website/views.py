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
    states = {
     'Alabama': 'AL',  'Alaska': 'AK',  'American Samoa':'AS',  'Arizona': 'AZ',  'Arkansas': 'AR',
     'Armed Forces Americas': 'AA',  'Armed Forces Europe': 'AE',  'Armed Forces Pacific': 'AP',
     'California': 'CA',  'Colorado': 'CO',  'Connecticut': 'CT',  'Delaware': 'DE',
     'District of Columbia': 'DC',  'Florida': 'FL',  'Georgia': 'GA',  'Guam': 'GU',  'Hawaii': 'HI',
     'Idaho': 'ID',  'Illinois': 'IL',  'Indiana': 'IN',  'Iowa': 'IA',  'Kansas': 'KS',
     'Kentucky': 'KY',  'Louisiana': 'LA',  'Maine': 'ME',  'Maryland': 'MD',  'Massachusetts': 'MA',
     'Michigan': 'MI',  'Minnesota': 'MN',  'Mississippi': 'MS',  'Missouri': 'MO',  'Montana': 'MT',
     'Nebraska': 'NE',  'Nevada': 'NV',  'New Hampshire': 'NH',  'New Jersey': 'NJ',
     'New Mexico': 'NM',  'New York': 'NY',  'North Carolina': 'NC',  'North Dakota':'ND',
     'Northern Mariana Islands': 'MP',  'Ohio': 'OH',  'Oklahoma': 'OK',  'Oregon': 'OR',
     'Pennsylvania': 'PA',  'Puerto Rico': 'PR',  'Rhode Island': 'RI',  'South Carolina': 'SC',
     'South Dakota': 'SD',  'Tennessee': 'TN',  'Texas': 'TX',  'Utah': 'UT',  'Vermont': 'VT',
     'Virgin Islands': 'VI',  'Virginia': 'VA',  'Washington': 'WA',  'West Virginia': 'WV',
     'Wisconsin': 'WI',  'Wyoming': 'WY'}

    # See if there is a new filter form submitted
    if 'state' in request.GET:
        if 'price_top' in request.GET and request.GET['price_top'] != "":
            price_top = request.GET['price_top']
        else:
            price_top = 1000000

        if 'price_bottom' in request.GET and request.GET['price_bottom'] != "":
            price_bottom = request.GET['price_bottom']
        else:
            price_bottom = 10000

        if 'size_top' in request.GET and request.GET['size_top'] != "":
            size_top = request.GET['size_top']
        else:
            size_top = 5000

        if 'size_bottom' in request.GET and request.GET['size_bottom'] != "":
            size_bottom = request.GET['size_bottom']
        else:
            size_bottom = 100

        if 'state' in request.GET and request.GET['state'] != "":
            state = request.GET['state']
        else:
            state = ""

        if 'bedrooms' in request.GET and request.GET['bedrooms'] != "":
            bedrooms = request.GET['bedrooms']
        else:
            bedrooms = ""

        if 'bathrooms' in request.GET and request.GET['bathrooms'] != "":
            bathrooms = request.GET['bathrooms']
        else:
            bathrooms = ""

        if 'basement' in request.GET and request.GET['basement'] == 'on':
            basement = 'on'
        else:
            basement = ""

        if 'garage' in request.GET and request.GET['garage'] == "on":
            garage = request.GET['garage']
        else:
            garage = ""

        if 'pool' in request.GET and request.GET['pool'] == "on":
            pool = request.GET['pool']
        else:
            pool = ""

        if 'keywords' in request.GET and request.GET['keywords'] != "":
            keywords = request.GET['keywords']
        else:
            keywords = ""

    else:

        if request.COOKIES.get('price_top'):
            price_top = request.COOKIES.get('price_top')
        else:
            price_top = 1000000

        if request.COOKIES.get('price_bottom'):
            price_bottom = request.COOKIES.get('price_bottom')
        else:
            price_bottom = 10000

        if request.COOKIES.get('size_top'):
            size_top = request.COOKIES.get('size_top')
        else:
            size_top = 5000

        if request.COOKIES.get('size_bottom'):
            size_bottom = request.COOKIES.get('size_bottom')
        else:
            size_bottom = 100

        if request.COOKIES.get('state'):
            state = request.COOKIES.get('state')
        else:
            state = ""

        if request.COOKIES.get('bedrooms'):
            bedrooms = request.COOKIES.get('bedrooms')
        else:
            bedrooms = ""

        if request.COOKIES.get('bathrooms'):
            bathrooms = request.COOKIES.get('bathrooms')
        else:
            bathrooms = ""

        if request.COOKIES.get('basement'):
            basement = request.COOKIES.get('basement')
        else:
            basement = ""

        if request.COOKIES.get('garage'):
            garage = request.COOKIES.get('garage')
        else:
            garage = ""

        if request.COOKIES.get('pool'):
            pool = request.COOKIES.get('pool')
        else:
            pool = ""

        if request.COOKIES.get('keywords'):
            keywords = request.COOKIES.get('keywords')
        else:
            keywords = ""

    # Check if user changed sorting criteria
    if 'sort' in request.GET:
        sort = request.GET['sort']
    elif request.COOKIES.get('sort'):
        sort = request.COOKIES.get('sort')
    else:
        sort = 'time'

    # properties_all = Property.objects.filter(list_price__gte=int(price_bottom), list_price__lte=int(price_top),
    #                                          size__lte=int(size_top), size__gte=int(size_bottom))

    properties_all = Property.objects.all()
    if int(price_bottom) != 10000:
        properties_all = properties_all.filter(list_price__gte=int(price_bottom))

    if int(price_top) != 1000000:
        properties_all = properties_all.filter(list_price__lte=int(price_top))

    if int(size_bottom) != 100:
        properties_all = properties_all.filter(size__gte=int(size_bottom))

    if int(size_top) != 5000:
        properties_all = properties_all.filter(size__lte=int(size_top))

    if state != "":
        state_brief = states[state]
        properties_all = properties_all.filter(address__locality__state=state_brief)

    if bedrooms != "":
        properties_all = properties_all.filter(bedroom__gte=int(bedrooms))

    if bathrooms != "":
        properties_all = properties_all.filter(bath__gte=int(bathrooms))

    if basement == "on":
        properties_all = properties_all.filter(basement=True)

    if garage != "":
        properties_all = properties_all.filter(garage_stall__gt=0)
    if pool == "on":
        properties_all = properties_all.filter(pool=True)

    if len(keywords) > 0:
        properties_all = properties_all.filter(Q(description__icontains=keywords) | Q(address__route__icontains=keywords)
                                               | Q(address__locality__city__icontains=keywords)| Q(address__street_number__icontains=keywords)
                                               | Q(address__locality__postal_code__icontains=keywords))

    if sort == 'most_view':
        properties_all = properties_all.order_by('-viewed_times')
    elif sort == 'low_price':
        properties_all = properties_all.order_by('list_price')
    elif sort == 'high_price':
        properties_all = properties_all.order_by('-list_price')
    else:
        properties_all = properties_all.order_by('-creation_time')

    most_viewed = Property.objects.order_by('-viewed_times')[:5]

    paginator = Paginator(properties_all, 4)
    page = request.GET.get('page', 1)

    try:
        properties = paginator.page(page)
    except PageNotAnInteger:
        properties = paginator.page(1)
    except EmptyPage:
        properties = paginator.page(paginator.num_pages)

    form = {'state': state, 'basement': basement, 'bathrooms': bathrooms, 'pool': pool, 'bedrooms': bedrooms, 'garage': garage,
            'price_top': price_top, 'price_bottom': price_bottom, 'size_top': size_top, 'size_bottom': size_bottom, 'sort': sort, 'keywords': keywords}

    length = len(properties_all)
    context = {'properties': properties, 'form': form, 'most_viewed': most_viewed, 'length': length}

    response = render(request, 'website/properties.html', context)
    response.set_cookie(key='price_top', value=price_top)
    response.set_cookie(key='price_bottom', value=price_bottom)
    response.set_cookie(key='size_top', value=size_top)
    response.set_cookie(key='size_bottom', value=size_bottom)
    response.set_cookie(key='state', value=state)
    response.set_cookie(key='bedrooms', value=bedrooms)
    response.set_cookie(key='bathrooms', value=bathrooms)
    response.set_cookie(key='basement', value=basement)
    response.set_cookie(key='garage', value=garage)
    response.set_cookie(key='pool', value=pool)
    response.set_cookie(key='sort', value=sort)
    response.set_cookie(key='keywords', value=keywords)

    return response


@login_required
@transaction.atomic
def details(request, id):
    property = Property.objects.get(id=id)
    property.viewed_times += 1
    property.save()
    similar = Property.objects.filter(address__locality__state=property.address.locality.state).exclude(id=id)[:4]
    pictures = property.pictures.all()
    profile = Profile.objects.get(user=request.user)
    c_list = profile.favorite_list.all()
    most_viewed = Property.objects.order_by('-viewed_times')[:5]
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
    return HttpResponse(picture, content_type='image/png')


@transaction.atomic
def get_picture(request, id):
    picture = get_object_or_404(Picture, id=id)
    image = picture.image

    return HttpResponse(image, content_type='image/png')
