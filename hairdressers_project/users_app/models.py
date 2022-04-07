from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import User


def user_portfolio_directory_path(instance, filename):
    return 'portfolio/{0}/{1}'.format(instance.slug, filename)


def user_avatar_directory_path(instance, filename):
    return 'avatars/{0}/{1}'.format(instance.slug, filename)


class Skill(models.Model):
    """ Модель навыков парикмахеров """
    name = models.CharField(max_length=50, verbose_name='навык', db_index=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Навыки'
        verbose_name = 'Навык'


class City(models.Model):
    """Модель городов, где живут парикмахеры"""
    name = models.CharField(max_length=255, verbose_name='город', db_index=True, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'


class SimpleUser(models.Model):
    """ Модель пользователя """

    username = models.CharField(max_length=30, verbose_name='логин')
    name = models.CharField(max_length=50, verbose_name='имя')
    surname = models.CharField(max_length=50, verbose_name='фамилия')
    email = models.EmailField(verbose_name='адрес эл. почты')
    avatar = models.ImageField(upload_to=user_avatar_directory_path, blank=True, verbose_name='фото профиля')
    slug = models.SlugField(max_length=50, unique=True, db_index=True, verbose_name='URL')
    is_hairdresser = models.BooleanField(default=False, verbose_name='парикмахер')
    date_of_registration = models.DateField(auto_now_add=True, verbose_name='дата регистрации')
    owner = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name_plural = 'простые пользователи'
        verbose_name = 'простого пользователя'


class Hairdresser(models.Model):
    """ Модель парикмахера """
    name = models.CharField(max_length=50, verbose_name='имя')
    surname = models.CharField(max_length=50, verbose_name='фамилия')
    slug = models.SlugField(max_length=50, verbose_name='URL', unique=True, db_index=True)
    city = models.ForeignKey(City, on_delete=models.PROTECT, null=True)
    phone = PhoneNumberField(verbose_name='номер телефона', blank=True)
    email = models.EmailField(verbose_name='фдрес эл. почты')
    avatar = models.ImageField(upload_to='avatars/%Y/%m/%d/', blank=True, verbose_name='фото профиля')
    skills = models.ManyToManyField(Skill, verbose_name='навыки')
    rating = models.IntegerField(default=1, verbose_name='рейтинг')
    instagram = models.URLField(max_length=255, blank=True, verbose_name='инстаграм')
    another_info = models.TextField(max_length=1000, blank=True, verbose_name='дополнительная информация')
    portfolio = models.ImageField(upload_to=user_portfolio_directory_path, blank=True, verbose_name='портфолио')
    owner = models.OneToOneField(SimpleUser, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'парикмахеры'
        verbose_name = 'парикмахер'

    def __str__(self):
        return self.name
