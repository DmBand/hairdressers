from django.urls import path

from .views import *

app_name = 'drf_app'
urlpatterns = [
    path('create_user/', CreateUserAPIView.as_view()),
    path('update_delete_user/<slug:username>/', UpdateDeleteUserAPIView.as_view()),
    path('create_hairdresser/', CreateHairdresserAPIView.as_view()),
]
