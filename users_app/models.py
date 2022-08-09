import os

from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import User

default_avatar_path = f"{os.path.join('../', 'static', 'users_app', 'assets', 'img', 'default_photo.jpg')}"


def path_to_user_portfolio_directory(instance, filename):
    return 'portfolio/{0}/{1}'.format(instance.owner.slug, filename)


def path_to_user_avatar_directory(instance, filename):
    return 'avatars/{0}/{1}'.format(instance.slug, filename)


class Skill(models.Model):
    """ Модель навыков парикмахеров """
    name = models.CharField(
        max_length=150,
        verbose_name='навык',
        db_index=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'навыки'
        verbose_name = 'навык'
        ordering = ['name']


class Region(models.Model):
    """ Модель областей """
    name = models.CharField(
        max_length=30,
        verbose_name='область',
        unique=True
    )

    class Meta:
        verbose_name = 'область'
        verbose_name_plural = 'области'

    def __str__(self):
        return self.name


class City(models.Model):
    """Модель городов"""
    region = models.ForeignKey(
        Region,
        on_delete=models.PROTECT,
        verbose_name='область',
        related_name='city'
    )
    name = models.CharField(
        max_length=60,
        verbose_name='город',
        db_index=True,
        unique=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'город'
        verbose_name_plural = 'города'
        ordering = ['name']


class SimpleUser(models.Model):
    """ Модель пользователя """
    username = models.CharField(
        max_length=30,
        verbose_name='логин'
    )
    name = models.CharField(
        max_length=50,
        verbose_name='имя'
    )
    surname = models.CharField(
        max_length=50,
        verbose_name='фамилия'
    )
    email = models.EmailField(
        verbose_name='адрес эл. почты',
        unique=True
    )
    avatar = models.ImageField(
        upload_to=path_to_user_avatar_directory,
        blank=True,
        default=default_avatar_path,
        verbose_name='фото профиля',
    )
    default_avatar = models.BooleanField(
        default=True,
    )
    slug = models.SlugField(
        max_length=50, 
        unique=True, 
        db_index=True, 
        verbose_name='URL',
    )
    is_hairdresser = models.BooleanField(
        default=False, 
        verbose_name='парикмахер',
    )
    date_of_registration = models.DateField(
        auto_now_add=True, 
        verbose_name='дата регистрации',
    )
    owner = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='simpleuser'
    )

    def __str__(self):
        return self.username

    class Meta:
        verbose_name_plural = 'простые пользователи'
        verbose_name = 'простого пользователя'


class Hairdresser(models.Model):
    """ Модель парикмахера """
    city = models.ForeignKey(
        City,
        on_delete=models.PROTECT,
        null=True,
        related_name='hairdresser'
    )
    phone = PhoneNumberField(verbose_name='номер телефона')
    skills = models.ManyToManyField(
        Skill,
        verbose_name='навыки',
        related_name='hairdressers'
    )
    rating = models.IntegerField(
        default=1,
        verbose_name='рейтинг'
    )
    instagram = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='инстаграм'
    )
    another_info = models.TextField(
        max_length=1000,
        blank=True,
        verbose_name='дополнительная информация'
    )
    portfolio = models.ImageField(
        upload_to=path_to_user_portfolio_directory,
        blank=True,
        verbose_name='портфолио'
    )
    owner = models.OneToOneField(
        SimpleUser,
        on_delete=models.CASCADE,
        related_name='hairdresser'
    )

    class Meta:
        verbose_name_plural = 'парикмахеры'
        verbose_name = 'парикмахер'

    def __str__(self):
        return self.owner.username
