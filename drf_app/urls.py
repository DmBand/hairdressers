from django.urls import path

from .views import *

app_name = 'drf_app'
urlpatterns = [
    path('create/', CreateUserAPIView.as_view()),
    # path('cities/', CitiesAPIView.as_view()),
    # path('users/', SimpleUserAPIView.as_view()),
]
