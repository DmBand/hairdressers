from django.contrib import admin
from .models import *


class HairdresserAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'surname', 'slug', 'city', 'rating', 'phone', 'email', 'date_of_registration', 'portfolio',
        'another_info'
    )
    list_display_links = ('name', 'surname')
    list_filter = ('name',)
    list_editable = ('rating',)
    prepopulated_fields = {'slug': ('name', 'surname')}


class SimpleUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'surname', 'slug', 'phone', 'email')
    list_display_links = ('name', 'surname')
    list_filter = ('name',)
    prepopulated_fields = {'slug': ('name', 'surname')}


admin.site.register(Skill)
admin.site.register(City)
admin.site.register(Hairdresser, HairdresserAdmin)
# admin.site.register(SimpleUser, SimpleUserAdmin)
