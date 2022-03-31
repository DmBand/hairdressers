from django.db import models


from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import User
# from slugify import slugify
# from django.utils.text import slugify


class Skill(models.Model):
    """Модель навыков парикмахеров"""
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


class Hairdresser(models.Model):
    """Модель парикмахера"""
    name = models.CharField(max_length=30, verbose_name='имя')
    surname = models.CharField(max_length=50, verbose_name='фамилия')
    slug = models.SlugField(max_length=255, verbose_name='URL', unique=True, db_index=True)
    city = models.ForeignKey(City, on_delete=models.PROTECT, blank=True, null=True)
    phone = PhoneNumberField(verbose_name='номер телефона', blank=True)
    email = models.EmailField(verbose_name='фдрес эл. почты')
    avatar = models.ImageField(upload_to='avatars/%Y/%m/%d/', blank=True, verbose_name='фото профиля')
    skills = models.ManyToManyField(Skill, verbose_name='навыки', blank=True)
    rating = models.IntegerField(default=1, verbose_name='рейтинг')
    instagram = models.URLField(max_length=255, blank=True, verbose_name='инстаграм')
    another_info = models.TextField(max_length=1000, blank=True, verbose_name='дополнительная информация')
    portfolio = models.ImageField(upload_to='portfolio/%Y/%m/%d/', blank=True, verbose_name='портфолио')
    date_of_registration = models.DateField(auto_now_add=True, verbose_name='дата регистрации')
    owner = models.OneToOneField(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'Парикмахеры'
        verbose_name = 'Парикмахера'


    def __str__(self):
        return self.name

    # def save(self, *args, **kwargs):
    #     self.slug = slugify(f'{self.name} {self.surname}', allow_unicode=True)
    #     return super().save(*args, **kwargs)


# class SimpleUser(models.Model):
#     """Модель простого пользователя (посетителя сайта)"""
#     name = models.CharField(max_length=50, verbose_name='Имя')
#     surname = models.CharField(max_length=50, blank=True, verbose_name='Фамилия')
#     slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name='URL')
#     phone = PhoneNumberField(blank=True, verbose_name='Телефон')
#     email = models.EmailField(blank=True, verbose_name='Адрес эл. почты')
#
#     def __str__(self):
#         return self.name
#
#     class Meta:
#         verbose_name_plural = 'Простые пользователи'
#         verbose_name = 'Пользователя'
