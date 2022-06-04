from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, SetPasswordForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from .models import Hairdresser, SimpleUser


# main profile
class RegistrationUserForm(UserCreationForm):
    """ Форма регистрации нового пользователя """

    # Валидатор для username
    username_validator = RegexValidator(
        regex=r'^[0-9a-zA-Z_-]*$',
        message='Допускаются буквы a-zA-Z, цифры и символы _- (не более 30).',
    )
    # Валидатор для имени и фамилии
    first_and_last_name_validator = RegexValidator(
        regex=r'^[a-zA-Zа-яёА-ЯЁ-]*$',
        message='Допускаются буквы а-яА-Я, a-zA-Z.'
    )

    # Валидатор пароля
    password_validator = RegexValidator(
        regex=r'^[^а-яёА-ЯЁ]+$',
        message='Символы кириллицы (а-яА-Я) не допускаются.'
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

    def clean_email(self):
        email = self.cleaned_data['email'].strip()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError('Пользователь с таким эл. адресом уже существует')
        return email


class AddAvatarForm(forms.ModelForm):
    """ Форма добавления аватарки пользователя """

    class Meta:
        model = SimpleUser
        fields = ['avatar']

        widgets = {
            'avatar': forms.FileInput(attrs={'class': 'input input__file2',
                                             'id': 'input__file2'})
        }


class LoginUserForm(AuthenticationForm):
    """ Форма авторизации пользователей """

    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'reg-form-input'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'reg-form-input'}))


class EditProfileForm(forms.ModelForm):
    """ Форма редактирования главного профиля """

    # Валидатор для имени и фамилии
    first_and_last_name_validator = RegexValidator(
        regex=r'^[a-zA-Zа-яёА-ЯЁ-]*$',
        message='Допускаются буквы а-яА-Я, a-zA-Z.'
    )

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

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name'
        ]

        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'reg-form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'reg-form-input'})
        }


# passwords
class ResetPasswordForm(SetPasswordForm):
    """
    Форма создания нового пароля после сброса старого
    (без ввода старого пароля)
    """

    # Валидатор пароля
    password_validator = RegexValidator(
        regex=r'^[^а-яёА-ЯЁ]+$',
        message='Символы кириллицы (а-яА-Я) не допускаются.'
    )

    new_password1 = forms.CharField(
        label="Новый пароль",
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
        validators=[password_validator]
    )

    new_password2 = forms.CharField(
        label="Подтвердите пароль",
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )


class ChangePasswordForm(PasswordChangeForm):
    """ Форма изменения пароля (с вводом старого пароля) """

    # Валидатор пароля
    password_validator = RegexValidator(
        regex=r'^[^а-яёА-ЯЁ]+$',
        message='Символы кириллицы (а-яА-Я) не допускаются.'
    )

    new_password1 = forms.CharField(
        label="Новый пароль",
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
        validators=[password_validator]
    )

    new_password2 = forms.CharField(
        label="Подтвердите пароль",
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )


# Portfolio
class CreatePortfolioForm(forms.ModelForm):
    """ Форма создания портфолио """

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
            'city': forms.Select(attrs={'class': 'portfolio-city-select'}),
            'skills': forms.CheckboxSelectMultiple(attrs={'class': 'portf-form-input-cb'}),
            'another_info': forms.Textarea(attrs={'class': 'portfolio-textarea',
                                                  'placeholder': 'Укажите доплнительную информацию о себе: '
                                                                 'стоимость услуг, возмжен ли выезд к клиенту, '
                                                                 'стаж, ссылки на электронные сертификаты и т.д.'}),
            'instagram': forms.TextInput(attrs={'class': 'portf-form-input',
                                                'placeholder': 'Никнейм (например: ivan123.1vanov)'}),
            'portfolio': forms.FileInput(attrs={'multiple': True,
                                                'class': 'input input__file',
                                                'id': 'input__file'}),
        }


class DeleteProfileForm(forms.Form):
    """ Форма удаления портфолио и профиля пользователя """

    code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'del-profile-input',
        'autocomplete': 'off',
        'placeholder': 'Ваш код'}
    ))
