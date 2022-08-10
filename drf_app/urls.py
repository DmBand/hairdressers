from django.urls import path

from .views import *

app_name = 'drf_app'
urlpatterns = [
    path('create_user/', CreateUpdateUserAPIView.as_view()),
    path('create_user/<slug:username>/', CreateUpdateUserAPIView.as_view()),
]
