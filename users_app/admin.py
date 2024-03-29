from django.contrib import admin
from .models import (Skill,
                     Region,
                     City,
                     Hairdresser,
                     SimpleUser)


class SkillAdmin(admin.ModelAdmin):
    """ Навыки парикмахеров """
    list_display = (
        'id',
        'name'
    )


class HairdresserAdmin(admin.ModelAdmin):
    """ Парикмахеры """
    list_display = (
        'id',
        'owner',
        'city',
        'rating',
        'phone',
        'another_info'
    )
    list_display_links = (
        'id',
        'owner'
    )
    list_filter = ('id',)
    list_editable = ('rating',)


class SimpleUserAdmin(admin.ModelAdmin):
    """ Простые пользователи """
    list_display = (
        'id', 
        'username', 
        'name', 
        'surname', 
        'email',
        'is_hairdresser', 
        'avatar', 
        'date_of_registration',
    )
    list_display_links = (
        'username',
    )
    list_editable = (
        'is_hairdresser',
    )
    prepopulated_fields = {
        'slug': ('username',),
    }


class CityAdmin(admin.ModelAdmin):
    """ Город """
    list_display = (
        'id', 
        'name', 
        'region',
    )
    search_fields = (
        'name',
    )
    list_filter = (
        'region',
    )


admin.site.register(Skill, SkillAdmin)
admin.site.register(Region)
admin.site.register(City, CityAdmin)
admin.site.register(Hairdresser, HairdresserAdmin)
admin.site.register(SimpleUser, SimpleUserAdmin)
