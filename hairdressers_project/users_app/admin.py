from django.contrib import admin
from .models import *


class HairdresserAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'owner', 'city', 'rating',
        'phone', 'another_info'
    )
    list_display_links = ('id', 'owner')
    list_filter = ('id',)
    list_editable = ('rating',)


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
