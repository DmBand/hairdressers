from django.contrib import admin
from .models import *


class HairdresserAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'surname', 'slug', 'city',
        'rating', 'phone', 'email', 'portfolio', 'another_info'
    )
    list_display_links = ('id', 'name', 'surname')
    list_filter = ('name',)
    list_editable = ('rating',)
    prepopulated_fields = {'slug': ('name', 'surname')}


class SimpleUserAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'username', 'name', 'surname', 'email',
        'is_hairdresser', 'avatar', 'date_of_registration'
    )
    list_display_links = ('username',)
    list_editable = ('is_hairdresser',)
    prepopulated_fields = {'slug': ('username',)}


admin.site.register(Skill)
admin.site.register(City)
admin.site.register(Hairdresser, HairdresserAdmin)
admin.site.register(SimpleUser, SimpleUserAdmin)
