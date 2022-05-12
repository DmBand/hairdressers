from django.urls import path
from .views import *

app_name = 'selection_app'

urlpatterns = [
    path('selection/', selection_view, name='selection'),
    # rating and reviews
    path('increase_rating/<slug:slug_name>/', increase_rating_view, name='increase_rating'),
    path('see_reviews/<slug:slug_name>/', see_reviews_view, name='see_reviews'),
]
