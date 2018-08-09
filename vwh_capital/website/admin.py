"""
@Author Yuzhe Yin
@Date 06/15/2018
VWH property listing website
"""
from django.contrib import admin

# Register your models here.
from .models import *
from django.forms import Textarea, TextInput


class PropertyAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '40'})},
        models.TextField: {'widget': Textarea(attrs={'rows': 6, 'cols': 40})},
    }


admin.site.register(Property, PropertyAdmin)
admin.site.register(Picture)
admin.site.register(Profile)
admin.site.register(Locality)
admin.site.register(Address)

































































