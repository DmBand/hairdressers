from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from rest_framework import serializers

from users_app.services import create_new_user
# from users_app.models import (Region,
#                               City,
#                               Skill,
#                               SimpleUser,
#                               Hairdresser)


class CreateUserSerialazer(serializers.ModelSerializer):
    """ Регистрация пользователя """
    username_validator = RegexValidator(
        regex=r'^[0-9a-zA-Z_-]*$',
        message='Допускаются буквы a-zA-Z, цифры и символы _- (не более 30).',
    )
    first_and_last_name_validator = RegexValidator(
        regex=r'^[a-zA-Zа-яёА-ЯЁ-]*$',
        message='Допускаются буквы а-яА-Я, a-zA-Z.'
    )
    password_validator = RegexValidator(
        regex=r'^[^а-яёА-ЯЁ]+$',
        message='Символы кириллицы (а-яА-Я) не допускаются.'
    )

    username = serializers.CharField(
        label='Логин',
        max_length=30,
        validators=[username_validator],
    )
    first_name = serializers.CharField(
        label='Имя',
        validators=[first_and_last_name_validator],
    )
    last_name = serializers.CharField(
        label='Фамилия',
        validators=[first_and_last_name_validator],
    )
    email = serializers.EmailField(
        label='Эл. адрес',
    )
    password1 = serializers.CharField(
        label='Пароль',
        validators=[password_validator],
    )
    password2 = serializers.CharField(
        label='Повторите пароль',
    )

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2'
        )

    def save(self, **kwargs):
        user = User(
            username=self.validated_data.get('username'),
            first_name=self.validated_data.get('first_name'),
            last_name=self.validated_data.get('last_name'),
        )

        email = self.validated_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError({email: 'Пользователь с таким эл. адресом уже существует'})
        user.email = email

        password1 = self.validated_data.get('password1')
        password2 = self.validated_data.get('password2')
        if password1 != password2:
            raise serializers.ValidationError({password1: "Пароли не совпадают"})
        user.set_password(password1)
        user.save()
        simpleuser = create_new_user(user=user)
        return simpleuser
