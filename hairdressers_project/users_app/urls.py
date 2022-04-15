from django.urls import path
from .views import *

app_name = 'users_app'

urlpatterns = [
    path('', homepage_view, name='homepage'),
    # main_profile
    path('registration/', RegistrationUserView.as_view(), name='register'),
    path('login/', LoginUserView.as_view(), name='login'),
    path('logout/', logout_user_view, name='logout'),
    path('add_avatar/', add_avatar_view, name='avatar'),
    path('edit_profile/<slug:slug_name>', edit_main_profile_view, name='edit_main_profile'),
    path('delete_profile/<slug:slug_name>', delete_main_profile_view, name='delete_main_profile'),
    path('profile/<slug:slug_name>/', get_main_profile_view, name='get_main_profile'),
    # portfolio
    path('create_portfolio/', create_portfolio_view, name='create_portfolio'),
    path('edit_portfolio/<slug:slug_name>/', edit_portfolio_view, name='edit_portfolio'),
    path('reset_portfolio/<slug:slug_name>/', reset_portfolio_photos_view, name='reset_portfolio'),
    path('delete_portfolio/<slug:slug_name>/', delete_portfolio_view, name='delete_portfolio'),
    path('hairdressers/<slug:slug_name>/', get_one_hairdresser_view, name='get_hairdresser'),
    # rating and reviews
    path('increase_rating/<slug:slug_name>/', increase_rating_view, name='increase_rating'),
    path('see_reviews/<slug:slug_name>/', see_reviews_view, name='see_reviews'),
]
