from django.urls import path
from .views import *


app_name = 'selection_app'

urlpatterns = [
    path('', SelectionView.as_view(), name='selection'),
]