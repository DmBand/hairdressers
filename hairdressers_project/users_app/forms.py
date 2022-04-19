from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, SetPasswordForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from .models import Hairdresser, SimpleUser, Comment


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


class ResetPasswordForm(SetPasswordForm):
    """
    Форма создания нового пароля после сброса старого
    (без ввода старого пароля)
    """

    # Валидатор пароля
    password_validator = RegexValidator(
        regex=r'^[^а-яА-Я]*$',
        message='Символы кириллицы /а-яА-Я/ не допускаются'
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
        regex=r'^[^а-яА-Я]*$',
        message='Символы кириллицы /а-яА-Я/ не допускаются'
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


class LoginUserForm(AuthenticationForm):
    """ Форма авторизации пользователей """

    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'reg-form-input'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'reg-form-input'}))


class AddAvatarForm(forms.ModelForm):
    """ Форма добавления аватарки пользователя """

    class Meta:
        model = SimpleUser
        fields = ['avatar']

        widgets = {
            'avatar': forms.ClearableFileInput(attrs={'class': 'input input__file2',
                                                      'id': 'input__file2'})
        }


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


class DeleteProfileForm(forms.Form):
    """ Форма удаления портфолио и профиля пользователя """

    code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'del-profile-input',
        'autocomplete': 'off',
        'placeholder': 'Ваш код'}
    ))


class EditProfileForm(forms.ModelForm):
    """ Форма редактирования портфолио """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name'
        ]

        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'reg-form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'reg-form-input'})
        }


class IncreaseRatingForm(forms.ModelForm):
    """ Форма повышения рейтинга парикмахера """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Comment
        fields = [
            'rating_value', 'text'
        ]

        widgets = {
            'text': forms.Textarea(attrs={'class': 'portfolio-textarea2',
                                          'placeholder': 'Не менее 10 символов!'})
        }

    def clean_text(self):
        text = self.cleaned_data.get('text')
        if len(text) < 10:
            raise ValidationError('Текст комментария должен содержать не менее 10 символов')
        return text
