from django.urls import path
from .views import *

app_name = 'users_app'

urlpatterns = [
    path('', homepage_view, name='homepage'),
    path('registration/', registration_view, name='register'),
    path('edit_profile/<slug:slug_name>', edit_main_profile_view, name='edit_main_profile'),
    path('login/', LoginUserView.as_view(), name='login'),
    path('logout/', logout_user_view, name='logout'),
    path('add_avatar/', add_avatar_view, name='avatar'),
    path('create_portfolio/', create_portfolio_view, name='create_portfolio'),
    path('edit_portfolio/<slug:slug_name>/', edit_portfolio_view, name='edit_portfolio'),
    path('increase_rating/<slug:slug_name>/', increase_rating_view, name='increase_rating'),
    path('hairdressers/<slug:slug_name>/', get_one_hairdresser_view, name='get_hairdresser'),
    path('profile/<slug:slug_name>/', get_main_profile_view, name='get_main_profile'),
    path('see_reviews/<slug:slug_name>/', see_reviews_view, name='see_reviews'),
]
