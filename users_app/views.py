from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (LoginView,
                                       PasswordResetConfirmView,
                                       PasswordResetView,
                                       PasswordChangeView)
from django.core.cache import cache
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView

from .decorators import user_is_authenticated
from hairdressers_project.settings import MEDIA_URL
from .forms import *
from .models import default_avatar_path
from .services import *


def homepage_view(request):
    """Возвращает главную страницу сайта"""
    top10 = cache.get_or_set('top10', Hairdresser.objects.order_by('-rating')[:10].select_related('city'), 60)
    context = {
        'title': 'Парикмахеры Беларуси',
        'top10': top10
    }

    return render(request, 'users_app/index.html', context=context)


# main profile
@method_decorator(user_is_authenticated, name='dispatch')
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
        create_new_user(user=user)
        login(self.request, user)
        # редирект на страницу добавления аватарки
        return redirect('users_app:avatar')


@login_required(login_url='users_app:login')
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
            person = SimpleUser.objects.get(slug=request.user.simpleuser.slug)
            person.default_avatar = False
            person.save()
            compress_avatar(person_slug=request.user.simpleuser.slug)
            return redirect('users_app:get_main_profile', slug_name=request.user.simpleuser.slug)

    elif request.POST.get('avatar') == 'no':
        return redirect('users_app:get_main_profile', slug_name=request.user.simpleuser.slug)

    else:
        form = AddAvatarForm()

    context = {'form': form, 'title': 'Добавить фото профиля'}

    return render(request, 'users_app/add_avatar.html', context)


@login_required(login_url='users_app:login')
def delete_avatar_view(request, slug_name):
    """ Удаление аватарки пользователя """
    if request.user.simpleuser.slug != slug_name:
        return redirect('users_app:get_main_profile', slug_name=request.user.simpleuser.slug)
    # Удаляем директорию с аватаром и ставим пользователю дефолтный аватар
    delete_avatar_directory(person_slug=slug_name)
    person = SimpleUser.objects.get(slug=slug_name)
    person.avatar = default_avatar_path
    person.default_avatar = True
    person.save()
    return redirect('users_app:get_main_profile', slug_name=slug_name)


@login_required(login_url='users_app:login')
def get_main_profile_view(request, slug_name):
    """ Возвращает страницу главного профиля пользователя """
    person = SimpleUser.objects.get(slug=slug_name)
    if request.user.username != person.slug:
        return redirect('users_app:get_main_profile', slug_name=request.user.username)

    context = {
        'title': f'Главный профиль: {person.username}',
        'username': person.username,
        'name': person.name,
        'surname': person.surname,
        'email': person.email,
        'avatar': person.avatar,
        'default_avatar': person.default_avatar,
        'slug': person.slug
    }
    return render(request, 'users_app/main_profile.html', context)


@login_required(login_url='users_app:login')
def edit_main_profile_view(request, slug_name):
    """ Возвращает страницу редактирования главного профиля """
    simple_user = SimpleUser.objects.get(slug=slug_name)
    if request.user.username != simple_user.owner.username:
        return redirect('users_app:get_main_profile', slug_name=request.user.username)

    user = User.objects.get(username=slug_name)
    if request.method != 'POST':
        form = EditProfileForm(instance=user)
    else:
        form = EditProfileForm(instance=user, data=request.POST)
        if form.is_valid():
            form.save()
            # Меняем данные модели SimpleUser
            simple_user.name = form.cleaned_data.get('first_name')
            simple_user.surname = form.cleaned_data.get('last_name')
            simple_user.save()
            return redirect('users_app:get_main_profile', slug_name=user.username)

    context = {'title': 'Редактирование главного профиля', 'form': form}
    return render(request, 'users_app/edit_main_profile.html', context)


@login_required(login_url='users_app:login')
def delete_main_profile_view(request, slug_name):
    """ Возвращает страницу удаления главного профиля """
    if request.user.username != slug_name:
        return redirect('users_app:get_main_profile', slug_name=request.user.username)

    user = User.objects.get(username=slug_name)
    # Проверочный код, который состоит из никнейма + /id +/profile
    code = f'{user.username}/{user.id}/profile'
    if request.method != 'POST':
        if user.simpleuser.is_hairdresser:
            messages.info(request, 'Внимание! У вас есть действующее портфолио парикмахера. '
                                   'Оно будет безвозвратно удалено.')
        form = DeleteProfileForm()
    else:
        form = DeleteProfileForm(data=request.POST)
        if request.POST.get('code') == code:
            # Если пользовтель парикмахер и у него есть фото в портфолио, то удаляем все файлы
            if user.simpleuser.is_hairdresser:
                delete_portfolio_directory(person_slug=slug_name)
            # Удаляем папку с аватаром
            delete_avatar_directory(person_slug=slug_name)
            user.delete()
            return redirect('users_app:homepage')
        else:
            if user.simpleuser.is_hairdresser:
                messages.info(request, 'Внимание! У вас есть действующее портфолио парикмахера. '
                                       'Оно будет безвозвратно удалено.')
            messages.error(request, 'Введен неверный код!')

    context = {
        'title': 'Удалить профиль',
        'form': form,
        'code': code,
        'user': user,
    }
    return render(request, 'users_app/delete_main_profile.html', context)


@method_decorator(user_is_authenticated, name='dispatch')
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


def logout_user_view(request):
    """
    Разлогинивает пользователя. После разлогина пользователь остаётся
    на текущей странице
    """

    logout(request)
    # return redirect(request.META.get('HTTP_REFERER'))
    return redirect('users_app:login')


# reset password
class ResetPasswordView(PasswordResetView):
    """ Письмо, которое получает пользователь при запросе сброса пароля """

    # Переопределяем путь к шаблону сообщения и основному шаблону
    email_template_name = 'users_app/reset_password/password_reset_email.html'
    template_name = 'users_app/reset_password/password_reset_form.html'
    # Переопределяем путь для перенаправления
    success_url = reverse_lazy("users_app:password_reset_done")


class ResetPasswordConfirmView(PasswordResetConfirmView):
    """ Страница ввода нового пароля после сброса """
    # Переопределили форму в forms.py
    form_class = ResetPasswordForm
    template_name = 'users_app/reset_password/password_reset_confirm.html'
    success_url = reverse_lazy("users_app:password_reset_complete")


# change password
class ChangePasswordView(PasswordChangeView):
    """ Страница ввода нового пароля при изменении пароля (с вводом старого) """
    # Переопределили форму в Forms.py
    form_class = ChangePasswordForm
    template_name = 'users_app/change_password/password_change_form.html'
    success_url = reverse_lazy('users_app:password_change_done')


# portfolio
@login_required(login_url='users_app:login')
def create_portfolio_view(request):
    """ Возвращает страницу с формой регистрации нового парикмахера """
    if request.user.simpleuser.is_hairdresser:
        return redirect('users_app:get_hairdresser', slug_name=request.user.simpleuser.slug)

    if request.method != 'POST':
        form = CreatePortfolioForm()
    else:
        form = CreatePortfolioForm(request.POST)
        if form.is_valid():
            # Получаем текущего пользователя из БД
            user = SimpleUser.objects.get(slug=request.user.username)
            # Получаем список файлов для портфолио и создаём нового парикмахера
            files = request.FILES.getlist('portfolio')
            create_new_hairdresser(user=user, data=form.cleaned_data, files=files)
            # Меняем флаг пользователя - он теперь парикмахер
            user.is_hairdresser = True
            user.save()
            compress_images_in_portfolio(person_slug=user.slug)
            # Редирект на страницу портфолио
            return redirect('users_app:get_hairdresser', slug_name=request.user.username)

    context = {'title': 'Создание портфолио', 'form': form, 'files': MAX_COUNT}
    return render(request, 'users_app/add_portfolio.html', context)


def get_one_hairdresser_view(request, slug_name):
    """ Возвращает страницу парикмахера (портфолио) """
    person = SimpleUser.objects.get(slug=slug_name)
    try:
        skills = person.hairdresser.skills.all().order_by('name')
    except:
        return redirect('users_app:get_main_profile', slug_name=request.user.username)
    context = {
        'title': f'Портфолио: {person.name.title()} {person.surname.title()}',
        'name': person.name,
        'surname': person.surname,
        'avatar': person.avatar,
        'rating': person.hairdresser.rating,
        'city': person.hairdresser.city,
        'skills': [skill.name for skill in skills],
        'phone': person.hairdresser.phone,
        'email': person.email,
        'instagram': person.hairdresser.instagram,
        'another_info': person.hairdresser.another_info,
        'slug': person.username,
        'review': person.hairdresser.comment_set.count(),
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
        # Файлы отображаются по дате добавления в портфолио
        all_files = {str(f): os.path.getmtime(f'{directory}/{f}') for f in files}
        sorted_files = sorted(all_files, key=all_files.get, reverse=True)
        # Сохраняем в context имена файлов, количество и путь к файлам,
        # после чего в шаблоне проходим циклом по всем файлам
        # и загружаем их на страницу
        context['files'] = sorted_files
        context['count'] = len(files)
        context['url_for_photo'] = url_for_photo

    return render(request, 'users_app/portfolio.html', context)


@login_required(login_url='users_app:login')
def edit_portfolio_view(request, slug_name):
    """ Возвращает страницу изменения портфолио """
    the_hairdresser = SimpleUser.objects.get(slug=slug_name)
    if request.user.username != the_hairdresser.owner.username:
        if request.user.simpleuser.is_hairdresser:
            return redirect('users_app:get_hairdresser', slug_name=request.user.username)
        else:
            return redirect('users_app:get_main_profile', slug_name=request.user.username)

    # Получаем отдельно список навыков, чтобы отметить в форме уже имеющиеся навыки
    skills = the_hairdresser.hairdresser.skills.all()
    if request.method != 'POST':
        form = CreatePortfolioForm(instance=the_hairdresser.hairdresser)
    else:
        form = CreatePortfolioForm(instance=the_hairdresser.hairdresser, data=request.POST)
        if form.is_valid():
            form.save()
            files = request.FILES.getlist('portfolio')
            if files:
                check_number_of_files_in_portfolio(person_slug=the_hairdresser.slug, new_files=files)
                for f in files:
                    the_hairdresser.hairdresser.portfolio = f
                    the_hairdresser.hairdresser.save()
                compress_images_in_portfolio(person_slug=the_hairdresser.slug)
            return redirect('users_app:get_hairdresser', slug_name=the_hairdresser.slug)

    context = {
        'title': 'Редактирование портфолио',
        'form': form,
        'skills': skills,
        'files': MAX_COUNT
    }
    return render(request, 'users_app/edit_portfolio.html', context)


@login_required(login_url='users_app:login')
def reset_portfolio_photos_view(request, slug_name):
    """ Удаление всех фотографий в портфолио """
    if request.user.simpleuser.slug != slug_name:
        return redirect('users_app:homepage')

    delete_portfolio_directory(person_slug=slug_name)
    return redirect('users_app:get_hairdresser', slug_name=slug_name)


@login_required(login_url='users_app:login')
def delete_portfolio_view(request, slug_name):
    """ Возвращает страницу удаления портфолио """

    if request.user.simpleuser.slug != slug_name:
        return redirect('users_app:get_main_profile', slug_name=request.user.simpleuser.slug)

    user = SimpleUser.objects.get(slug=slug_name)
    # Проверочный код, который состоит из никнейма + /id + /portfolio
    code = f'{user.username}/{user.hairdresser.id}/portfolio'
    if request.method != 'POST':
        form = DeleteProfileForm()
    else:
        form = DeleteProfileForm(data=request.POST)
        if request.POST.get('code') == code:
            # Очищаем папку портфолио со всеми фотографиями
            delete_portfolio_directory(person_slug=slug_name)
            # Удаляем модель парикмахера
            user.hairdresser.delete()
            # Меняем флаг пользователя - он теперь не парикмахер
            user.is_hairdresser = False
            user.save()
            return redirect('users_app:get_main_profile', slug_name=slug_name)
        else:
            # Отображается, если введён неверный код
            messages.error(request, 'Введен неверный код!')

    context = {
        'title': 'Удалить портфолио',
        'form': form,
        'code': code,
        'hairdresser': user,
    }
    return render(request, 'users_app/delete_portfolio.html', context)


# errors
def page_400_view(request, exception):
    """ Возвращает страницу 400 """
    context = {'title': 'Некорректный запрос...'}
    return render(request, 'users_app/400.html', context, status=400)


def page_403_view(request, exception):
    """ Возвращает страницу 403 """
    context = {'title': 'Доступ запрещен...'}
    return render(request, 'users_app/403.html', context, status=403)


def page_404_view(request, exception):
    """ Возвращает страницу 404 """
    context = {'title': 'Страница не найдена...'}
    return render(request, 'users_app/404.html', context, status=404)


def page_500_view(request):
    """ Возвращает страницу 500 """
    context = {'title': 'Ошибка сервера...'}
    return render(request, 'users_app/500.html', context, status=500)
