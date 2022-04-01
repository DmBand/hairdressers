from django.urls import path
from .views import *

app_name = 'users_app'

urlpatterns = [
    path('', homepage_view, name='homepage'),
    path('selection/', SelectionView.as_view(), name='selection'),
    path('hairdresser/<slug:slug_name>', one_hairdresser_view, name='one_hairdresser'),
    path('login/', LoginUserView.as_view(), name='login'),
    path('logout/', logout_user, name='logout'),
    path('avatar/', add_avatar_view, name='avatar'),
    path('register', RegistrationUserView.as_view(), name='register'),
]
