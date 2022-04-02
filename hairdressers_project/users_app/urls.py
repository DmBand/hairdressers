from django.urls import path
from .views import *

app_name = 'users_app'

urlpatterns = [
    path('', homepage_view, name='homepage'),
    path('registration/', RegistrationUserView.as_view(), name='register'),
    path('login/', LoginUserView.as_view(), name='login'),
    path('logout/', logout_user, name='logout'),
    path('avatar/', add_avatar_view, name='avatar'),
    path('create_portfolio/<slug:slug_name>/', CreatePortfolioView.as_view(), name='create_portfolio'),
    path('hairdresser/<slug:slug_name>/', get_one_hairdresser, name='get_hairdresser'),
    path('profile/<slug:slug_name>/', get_main_profile, name='get_main_profile'),
]
