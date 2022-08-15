from django.urls import path

from .views import *

app_name = 'drf_app'
urlpatterns = [
    # users
    path('create_user/', CreateUserAPIView.as_view()),
    path('update_delete_user/<slug:username>/', UpdateDeleteUserAPIView.as_view()),
    path('create_hairdresser/', CreateHairdresserAPIView.as_view()),
    path('get_hairdresser/<slug:username>/', GetHairdresserAPIView.as_view()),
    path('update_delete_hairdresser/<slug:username>/', UpdateDeleteHairdresserAPIView.as_view()),
    # other
    path('get_skills/', SkillsAPIView.as_view()),
    path('get_cities/', CitiesAPIView.as_view()),
    path('get_city/<int:pk>/', GetCityAPIView.as_view()),
    path('get_cities_in_the_region/<int:pk>/', GetAllCitiesInTheRegion.as_view()),
]
