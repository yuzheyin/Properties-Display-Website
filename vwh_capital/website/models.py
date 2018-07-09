from django.db import models
from django.contrib.auth.models import User
from .choices import *


# class State(models.Model):
#     name = models.CharField(max_length=165, blank=True, choices=STATE_CHOICES)
#     code = models.CharField(max_length=3, blank=True)
#
#     def to_str(self):
#         return '%s' % (self.name or self.code)


class Locality(models.Model):
    city = models.CharField(max_length=165, blank=True)
    postal_code = models.CharField(max_length=10, blank=True)
    # state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='localities')
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default='NA')

    class Meta:
        verbose_name_plural = 'Localities'
        unique_together = ('city', 'postal_code', 'state')
        ordering = ('state', 'city')

    def __str__(self):
        txt = '%s' % self.city
        state = self.state if self.state else ''
        if txt and state:
            txt += ', '
        txt += state
        if self.postal_code:
            txt += ' %s' % self.postal_code
        return txt


class Address(models.Model):
    street_number = models.CharField(max_length=20, blank=True)
    route = models.CharField(max_length=100, blank=True)
    locality = models.ForeignKey(Locality, on_delete=models.CASCADE, related_name='addresses', blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Addresses'
        ordering = ('locality', 'route', 'street_number')

    def __str__(self):
        txt = ''
        if self.street_number:
            txt = '%s' % self.street_number
        if self.route:
            if txt:
                txt += ' %s' % self.route
        locality = '%s' % self.locality
        if txt and locality:
            txt += ', '
        txt += locality

        return txt

    def as_dict(self):
        ad = dict(
            street_number=self.street_number,
            route=self.route,
            latitude=self.latitude if self.latitude else '',
            longitude=self.longitude if self.longitude else '',
        )
        if self.locality:
            ad['locality'] = self.locality.city
            ad['postal_code'] = self.locality.postal_code
            if self.locality.state:
                ad['state'] = self.locality.state
                # ad['state_code'] = self.locality.state.code
                if self.locality.state.country:
                    ad['country'] = self.locality.state.country.name
                    ad['country_code'] = self.locality.state.country.code
        return ad


class Picture(models.Model):
    image = models.FileField(blank=True)
    title = models.CharField(max_length=100, blank=True)
    intro = models.TextField(max_length=300, blank=True)
    # property = models.ForeignKey(Property, on_delete=models.CASCADE)

    def __unicode__(self):
        return 'Picture(id=' + str(self.id) + ')'


# Property Model
class Property(models.Model):
    creation_time = models.DateTimeField()
    last_changed = models.DateTimeField()
    pictures = models.ManyToManyField(Picture, related_name="pics_belongs_to", blank=True)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    loan_id = models.CharField(max_length=50, default='NA')
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPE_CHOICES, blank=True)
    age = models.IntegerField(default=0)
    description = models.TextField(max_length=1000, blank=True)
    favorite_by = models.ManyToManyField(User, related_name="prop_favorite_by", blank=True)
    likes = models.IntegerField(default=0)
    size = models.FloatField(default=0)
    lot_size = models.FloatField(default=0)
    style = models.CharField(max_length=30, blank=True)
    condition = models.CharField(max_length=30, blank=True)
    bedroom = models.IntegerField(default=0)
    bath = models.IntegerField(default=0)
    half_bath = models.IntegerField(default=0)
    total_room = models.IntegerField(default=0)
    garage_style = models.CharField(max_length=30, blank=True)
    garage_stall = models.IntegerField(default=0)
    basement = models.BooleanField(default=False)
    pool = models.BooleanField(default=False)
    list_price = models.FloatField(default=0)

    def __unicode__(self):
        return 'Property(id=' + str(self.id) + ')'


# Profile Model
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    favorite_list = models.ManyToManyField(Property, related_name="liked_prop")
    longitude = models.FloatField(blank=True, default=0)
    latitude = models.FloatField(blank=True, default=0)

    def __unicode__(self):
        return 'Profile(id=' + str(self.id) + ')'
