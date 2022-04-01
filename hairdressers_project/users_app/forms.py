from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

from .models import Hairdresser, SimpleUser


class RegistrationUserForm(UserCreationForm):
    """ Форма регистрации нового пользователя """

    # Валидатор для username
    username_validator = RegexValidator(
        regex=r'^[0-9a-zA-Z._-]*$',
        message='Используйте символы латинского алфавита, цифры 0-9, символ "_"',
    )
    username = forms.CharField(
        label='Логин',
        max_length=30,
        validators=[username_validator])

    # avatar = forms.ImageField(label='Аватар')

    class Meta:
        model = User
        fields = (
            'username', 'first_name', 'last_name', 'email',
            'password1', 'password2'
        )


class LoginUserForm(AuthenticationForm):
    """ Форма авторизации пользователей """

    username = forms.CharField(label='Логин', widget=forms.TextInput())
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput())


class AddPortfolioForm(forms.ModelForm):
    """ Форма создания портфолио """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Hairdresser
        exclude = ['slug', 'date_of_registration', 'owner']


class AddAvatarForm(forms.ModelForm):

    class Meta:
        model = SimpleUser
        fields = ['avatar']
