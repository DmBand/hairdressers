from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from rest_framework import serializers

from users_app.models import City, SimpleUser
from users_app.services import create_new_user


class CreateUserSerialazer(serializers.Serializer):
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

    def create(self, validated_data):
        email = validated_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError({email: 'Пользователь с таким эл. адресом уже существует'})

        password1 = validated_data.get('password1')
        password2 = validated_data.get('password2')
        if password1 != password2:
            raise serializers.ValidationError({password1: "Пароли не совпадают"})

        user = User.objects.create_user(
            username=validated_data.get('username'),
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            email=email,
            password=password1,
        )

        simple_user = create_new_user(user=user)
        return simple_user


class UpdateUserSerialazer(serializers.Serializer):
    UNUSED_FIELDS = [
        'email',
        'password1',
        'password2'
    ]
    first_and_last_name_validator = RegexValidator(
        regex=r'^[a-zA-Zа-яёА-ЯЁ-]*$',
        message='Допускаются буквы а-яА-Я, a-zA-Z.'
    )
    first_name = serializers.CharField(
        label='Имя',
        validators=[first_and_last_name_validator],
        required=False
    )
    last_name = serializers.CharField(
        label='Фамилия',
        validators=[first_and_last_name_validator],
        required=False
    )

    def update(self, instance, validated_data):
        simple_user = SimpleUser.objects.get(username=instance.username)
        first_name = validated_data.get('first_name')
        last_name = validated_data.get('last_name')
        if first_name:
            instance.first_name = first_name.title()
            simple_user.name = first_name.title()
            instance.save()
            simple_user.save()
        if last_name:
            instance.last_name = last_name.title()
            simple_user.surname = last_name.title()
            instance.save()
            simple_user.save()

        return instance
