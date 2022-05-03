from django.contrib.auth import views as av
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
    # password reset
    path('forgot_password', ResetPasswordView.as_view(),
         name='password_reset'),
    path('reset_confirm/<uidb64>/<token>', ResetPasswordConfirmView.as_view(),
         name='password_reset_confirm'),
    path('reset_done', av.PasswordResetDoneView.as_view(
        template_name='users_app/reset_password/password_reset_done.html'),
         name='password_reset_done'),
    path('reset_complete', av.PasswordResetCompleteView.as_view(
        template_name='users_app/reset_password/password_reset_complete.html'),
         name='password_reset_complete'),
    # password change
    path('password_change/', ChangePasswordView.as_view(), name='password_change'),
    path('password_change/done/', av.PasswordChangeDoneView.as_view(
        template_name='users_app/change_password/password_change_done.html'),
         name='password_change_done'),

    # portfolio
    path('create_portfolio/', create_portfolio_view, name='create_portfolio'),
    path('edit_portfolio/<slug:slug_name>/', edit_portfolio_view, name='edit_portfolio'),
    path('reset_portfolio/<slug:slug_name>/', reset_portfolio_photos_view, name='reset_portfolio'),
    path('delete_portfolio/<slug:slug_name>/', delete_portfolio_view, name='delete_portfolio'),
    path('hairdressers/<slug:slug_name>/', get_one_hairdresser_view, name='get_hairdresser'),
]
