from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView

from hairdressers_project.settings import MEDIA_ROOT, MEDIA_URL
from .forms import *
from .services import check_number_of_files_in_portfolio, check_number_of_files_in_avatar_directory

import os


def homepage_view(request):
    """Возвращает главную страницу сайта"""

    top10 = Hairdresser.objects.order_by('-rating')[:10]
    context = {
        'title': 'Парикмахеры Беларуси',
        'top10': top10
    }

    return render(request, 'users_app/index.html', context=context)


class RegistrationUserView(CreateView):
    """
    Возвращает форму регистрации пользователя и, в случае успешной регистрации,
    перенаправляет пользователя на главную страницу сайта
    """

    form_class = RegistrationUserForm
    template_name = 'users_app/register.html'
    success_url = reverse_lazy('users_app:homepage')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Регистрация'
        return context

    def form_valid(self, form):
        user = form.save()
        SimpleUser.objects.create(
            owner=user,
            username=user.username,
            name=user.first_name.capitalize(),
            surname=user.last_name.capitalize(),
            email=user.email,
            slug=user.username,
        )
        login(self.request, user)
        # редирект на страницу добавления аватарки
        return redirect('users_app:avatar')


def add_avatar_view(request):
    """
    Добавление аватарки польователя.
    Если пользователь не загрузит аватарку, то будет установлено
    стандартное изображение
    """

    if request.POST.get('avatar') == 'yes':
        form = AddAvatarForm(
            request.POST,
            request.FILES,
            instance=request.user.simpleuser
        )

        if form.is_valid():
            # Удаляем старую аватарку из хранилища
            check_number_of_files_in_avatar_directory(person_slug=request.user.simpleuser.slug)
            form.save()
            return redirect('users_app:get_main_profile', slug_name=request.user.simpleuser.slug)

    elif request.POST.get('avatar') == 'no':
        return redirect('users_app:get_main_profile', slug_name=request.user.simpleuser.slug)

    else:
        form = AddAvatarForm()

    context = {'form': form, 'title': 'Добавить фото профиля'}

    return render(request, 'users_app/add_avatar.html', context)


class LoginUserView(LoginView):
    """
    Возвращает страницу авторизации пользователя.
    В случае успешной авторизации перенаправляет пользователя
    на главную страницу сайта
    """

    form_class = LoginUserForm
    template_name = 'users_app/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Вход'
        return context

    def get_success_url(self):
        return reverse_lazy('users_app:homepage')


def logout_user(request):
    """
    Разлогинивает пользователя. После разлогина пользователь остаётся
    на текущей странице
    """

    logout(request)
    # return redirect(request.META.get('HTTP_REFERER'))
    return redirect('users_app:login')


def get_one_hairdresser(requset, slug_name):
    """ Возвращает страницу парикмахера (портфолио) """

    person = Hairdresser.objects.get(slug=slug_name)
    skills = person.skills.all().order_by('name')
    context = {
        'title': f'{person.name.capitalize()} {person.surname.capitalize()}',
        'avatar': person.avatar,
        'rating': person.rating,
        'city': person.city,
        'skills': [skill.name for skill in skills],
        'phone': person.phone,
        'email': person.email,
        'instagram': person.instagram,
        'another_info': person.another_info,
        'slug': person.slug,
    }

    # Получаем путь к директории хранения файлов пользователя
    directory = f'{MEDIA_ROOT}/portfolio/{person.slug}'

    # Если пользователь первый раз добавляет фотографии, то файлов
    # в директории и самой директории ещё не будет. В этом случае
    # передаём в шаблон пустой список фотографий
    try:
        # Получаем список имен файлов из найденной директории
        files = os.listdir(directory)
    except FileNotFoundError:
        context['files'] = []
    else:
        # URL, по которому будут находиться фото пользователя
        url_for_photo = f'{MEDIA_URL}portfolio/{person.slug}'
        # Сохраняем в context имена файлов и путь к файлам,
        # после чего в шаблоне проходим циклом по всем файлам
        # и загружаем их на страницу
        context['files'] = files
        context['url_for_photo'] = url_for_photo

    return render(requset, 'users_app/portfolio.html', context)


def get_main_profile(request, slug_name):
    """ Возвращает страницу главного профиля пользователя """

    person = SimpleUser.objects.get(slug=slug_name)
    context = {
        'title': 'Главный профиль',
        'username': person.username,
        'name': person.name,
        'surname': person.surname,
        'email': person.email,
        'avatar': person.avatar
    }

    return render(request, 'users_app/main_profile.html', context)


def create_portfolio_view(request):
    """ Возвращает страницу с формой регистрации нового парикмахера """

    if request.method != 'POST':
        form = CreatePortfolioForm()
    else:
        form = CreatePortfolioForm(request.POST)
        if form.is_valid():
            # Получаем текущего пользователя из БД и создаем мадель парикмахера
            user = SimpleUser.objects.get(slug=request.user.username)
            the_hairdresser = Hairdresser.objects.create(
                name=user.name,
                surname=user.surname,
                slug=user.slug,
                city=form.cleaned_data.get('city'),
                phone=form.cleaned_data.get('phone'),
                email=user.email,
                avatar=user.avatar,
                instagram=form.cleaned_data.get('instagram'),
                another_info=form.cleaned_data.get('another_info'),
                owner=user,
            )
            # Получаем весь набор навыков из заполненной формы
            all_skills = form.cleaned_data.get('skills')
            # Добавляем наши навыки объекту "парикмахер"
            the_hairdresser.skills.add(*all_skills)

            # Если передавались файлы в портфолио, то обрабатываем их и сохраняем
            files = request.FILES.getlist('portfolio')
            if files:
                check_number_of_files_in_portfolio(person_slug=user.slug, new_files=files)
                for f in files:
                    the_hairdresser.portfolio = f
                    the_hairdresser.save()

            # Меняем флаг пользователя - он теперь парикмахер. И обязательно сохраняем
            user.is_hairdresser = True
            user.save()

            # Редирект на страницу портфолио
            return redirect('users_app:get_hairdresser', slug_name=request.user.username)

        else:
            print(form.errors)

    context = {'title': 'Регистрация формы', 'form': form}

    return render(request, 'users_app/add_portfolio.html', context)


def edit_portfolio_view(request, slug_name):
    """ Возвращает страницу изменения портфолио """

    the_hairdresser = Hairdresser.objects.get(slug=slug_name)
    # Получаем отдельно список навыков, чтобы отметить в форме уже имеющиеся навыки
    skills = the_hairdresser.skills.all()

    if request.method != 'POST':
        form = CreatePortfolioForm(instance=the_hairdresser)
    else:
        form = CreatePortfolioForm(instance=the_hairdresser, data=request.POST)
        if form.is_valid():
            form.save()
            files = request.FILES.getlist('portfolio')
            if files:
                check_number_of_files_in_portfolio(person_slug=the_hairdresser.slug, new_files=files)
                for f in files:
                    the_hairdresser.portfolio = f
                    the_hairdresser.save()

            return redirect('users_app:get_hairdresser', slug_name=the_hairdresser.slug)

    context = {'form': form, 'skills': skills}
    return render(request, 'users_app/edit_portfolio.html', context)
