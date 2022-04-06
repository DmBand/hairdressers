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
        message='Не более 30 символов. Только латинские буквы, цифры и символы ./-/_',
    )
    # Валидатор для имени и фамилии
    first_and_last_name_validator = RegexValidator(
        regex=r'^[a-zA-Zа-яА-Я]*$',
        message='Допускаются буквы /а-яА-Я/, /a-zA-Z/'
    )

    # Валидатор пароля
    password_validator = RegexValidator(
        regex=r'^[^а-яА-Я]*$',
        message='Символы кириллицы /а-яА-Я/ не допускаются'
    )

    username = forms.CharField(
        label='Логин',
        max_length=30,
        validators=[username_validator],
        widget=forms.TextInput(attrs={'class': 'reg-form-input'}))
    first_name = forms.CharField(
        label='Имя',
        validators=[first_and_last_name_validator],
        widget=forms.TextInput(attrs={'class': 'reg-form-input'})
    )
    last_name = forms.CharField(
        label='Фамилия',
        validators=[first_and_last_name_validator],
        widget=forms.TextInput(attrs={'class': 'reg-form-input'})
    )
    email = forms.EmailField(label='Эл. адрес', widget=forms.EmailInput(attrs={'class': 'reg-form-input'}))
    password1 = forms.CharField(
        label='Пароль',
        validators=[password_validator],
        widget=forms.PasswordInput(attrs={'class': 'reg-form-input'}))
    password2 = forms.CharField(label='Повторите пароль', widget=forms.PasswordInput(attrs={'class': 'reg-form-input'}))

    class Meta:
        model = User
        fields = (
            'username', 'first_name', 'last_name', 'email',
            'password1', 'password2'
        )


class LoginUserForm(AuthenticationForm):
    """ Форма авторизации пользователей """

    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'reg-form-input'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'reg-form-input'}))


class AddAvatarForm(forms.ModelForm):
    """ Форма добавления аватарки пользователя """

    class Meta:
        model = SimpleUser
        fields = ['avatar']


# class CreatePortfolioForm(forms.ModelForm):
#     """ Форма создания портфолио """
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#     class Meta:
#         model = Hairdresser
#         fields = [
#             'phone', 'city', 'skills',
#             'another_info', 'instagram', 'portfolio'
#         ]
#         widgets = {
#             'portfolio': forms.ClearableFileInput(attrs={'multiple': True})
#         }

class CreatePortfolioForm(forms.ModelForm):
    """ Форма создания портфолио """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Hairdresser
        fields = [
            'phone', 'city', 'skills',
            'another_info', 'instagram', 'portfolio'
        ]
        widgets = {
            'phone': forms.NumberInput(attrs={'class': 'portf-form-input',
                                              'placeholder': 'Пример: +375291112233',
                                              'required': True}),
            'city': forms.Select(attrs={'class': 'portfolio-city-select'}, ),
            'skills': forms.CheckboxSelectMultiple(attrs={'class': 'portf-form-input-cb'}),
            'another_info': forms.Textarea(attrs={'class': 'portfolio-textarea',
                                                  'placeholder': 'Укажите доплнительную информацию о себе: '
                                                                 'стоимость услуг, возмжен ли выезд к клиенту, '
                                                                 'стаж, ссылки на электронные сертификаты и т.д.'}),
            'instagram': forms.URLInput(attrs={'class': 'portf-form-input',
                                               'placeholder': 'url-адрес'}),
            'portfolio': forms.ClearableFileInput(attrs={'multiple': True,
                                                         'class': 'input input__file',
                                                         'id': 'input__file'}),
        }
