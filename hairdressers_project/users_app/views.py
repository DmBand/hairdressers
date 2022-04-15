import os

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.db.models import F
from django.http import Http404
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView

from .decorators import user_is_authenticated
from hairdressers_project.settings import MEDIA_ROOT, MEDIA_URL
from .forms import *
from .services import \
    check_number_of_files_in_portfolio, \
    check_number_of_files_in_avatar_directory, \
    delete_portfolio_directory, \
    delete_avatar_directory


def homepage_view(request):
    """Возвращает главную страницу сайта"""

    top10 = Hairdresser.objects.order_by('-rating')[:10]
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
            return redirect('users_app:get_main_profile', slug_name=request.user.simpleuser.slug)

    elif request.POST.get('avatar') == 'no':
        return redirect('users_app:get_main_profile', slug_name=request.user.simpleuser.slug)

    else:
        form = AddAvatarForm()

    context = {'form': form, 'title': 'Добавить фото профиля'}

    return render(request, 'users_app/add_avatar.html', context)


@login_required(login_url='users_app:login')
def get_main_profile_view(request, slug_name):
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


@login_required(login_url='users_app:login')
def edit_main_profile_view(request, slug_name):
    """ Возвращает страницу редактирования главного профиля """

    # Флаг, показывающий, является ли пользователь парикмахером
    the_hairdresser = True

    try:
        hairdresser = Hairdresser.objects.get(slug=slug_name)
        # Ловим исключение self.model.DoesNotExist, если пользователь
        # не является парикмахером, и устанавливаем флаг False
    except:
        the_hairdresser = False

    simple_user = SimpleUser.objects.get(slug=slug_name)
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

            # Если пользователь парикмахер, то меняем данные в портфолио
            if the_hairdresser:
                hairdresser.name = form.cleaned_data.get('first_name')
                hairdresser.surname = form.cleaned_data.get('last_name')
                hairdresser.save()

            return redirect('users_app:get_main_profile', slug_name=user.username)

    context = {'title': 'Редактирование главного профиля', 'form': form}
    return render(request, 'users_app/edit_main_profile.html', context)


@login_required(login_url='users_app:login')
def delete_main_profile_view(request, slug_name):
    """ Возвращает страницу удаления главного профиля """

    # Если пользователь захочет удалить чужой профиль через URL,
    # то его перекинет на страницу удаления своего портфолио
    if request.user.simpleuser.slug != slug_name:
        return redirect('users_app:delete_main_profile', slug_name=request.user.simpleuser.slug)

    user = User.objects.get(username=slug_name)
    user_is_hairdresser = user.simpleuser.is_hairdresser

    # Проверочный код, который состоит из никнейма + /id +/profile
    code = f'{user.username}/{user.id}/profile'

    if request.method != 'POST':
        if user_is_hairdresser:
            messages.info(request, f'Внимание! {user.simpleuser.name}, у вас есть заполненное портфолио. '
                                   f'Оно будет безвозвратно удалено.')
        form = DeleteProfileForm()
    else:
        form = DeleteProfileForm(data=request.POST)
        if request.POST.get('code') == code:
            # Если пользовтель парикмахер и у него есть фото в портфолио, то удаляем все файлы
            if user_is_hairdresser:
                delete_portfolio_directory(person_slug=slug_name)

            # Удаляем папку с аватаром
            delete_avatar_directory(person_slug=slug_name)
            user.delete()

            return redirect('users_app:homepage')

        else:
            if user_is_hairdresser:
                messages.info(request, f'Внимание! {user.simpleuser.name}, у вас есть заполненное портфолио. '
                                       f'Оно будет безвозвратно удалено.')
            messages.error(request, 'Введен неверный код!')

    context = {
        'title': 'Удалить профиль',
        'form': form,
        'code': code,
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


# portfolio
@login_required(login_url='users_app:login')
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


def get_one_hairdresser_view(requset, slug_name):
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
        'review': person.comment_set.count(),
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
        context['count'] = len(files)
        context['url_for_photo'] = url_for_photo

    return render(requset, 'users_app/portfolio.html', context)


@login_required(login_url='users_app:login')
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

    context = {'title': 'Редактирование портфолио', 'form': form, 'skills': skills}
    return render(request, 'users_app/edit_portfolio.html', context)


@login_required(login_url='users_app:login')
def reset_portfolio_photos_view(request, slug_name):
    """ Удаление всех фотографий в портфолио """

    # Если пользователь попытается удалить чужие фото через URL,
    # то его перекинет на главную страницу сайта
    if request.user.simpleuser.slug != slug_name:
        return redirect('users_app:homepage')

    delete_portfolio_directory(person_slug=slug_name)
    return redirect('users_app:get_hairdresser', slug_name=slug_name)


@login_required(login_url='users_app:login')
def delete_portfolio_view(request, slug_name):
    """ Возвращает страницу удаления портфолио """

    # Если пользователь захочет удалить чужое портфолио через URL,
    # то его перекинет на страницу удаления своего портфолио
    if request.user.simpleuser.slug != slug_name:
        return redirect('users_app:delete_portfolio', slug_name=request.user.simpleuser.slug)

    hairdresser = Hairdresser.objects.get(slug=slug_name)
    user = SimpleUser.objects.get(slug=slug_name)

    # Проверочный код, который состоит из никнейма + /id + /portfolio
    code = f'{user.username}/{hairdresser.id}/portfolio'

    if request.method != 'POST':
        form = DeleteProfileForm()
    else:
        form = DeleteProfileForm(data=request.POST)
        if request.POST.get('code') == code:
            # Очищаем папку портфолио со всеми фотографиями
            delete_portfolio_directory(person_slug=slug_name)
            # Удаляем модель парикмахера
            hairdresser.delete()
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
        'slug': hairdresser.slug,
    }

    return render(request, 'users_app/delete_portfolio.html', context)


# rating and review
@login_required(login_url='users_app:login')
def increase_rating_view(request, slug_name):
    """ Возвращает страницу повышения рейтинга и добавления отзыва """

    # Кого оцениваем
    who_do_we_evaluate = Hairdresser.objects.get(slug=slug_name)
    # Кто оценивает
    who_evaluates = SimpleUser.objects.get(slug=request.user.simpleuser.slug)

    # Если парикмахер захочет проголосовать сам за себя, то его перекинет на его портфолио
    if who_evaluates.slug == who_do_we_evaluate.slug:
        return redirect('users_app:get_hairdresser', slug_name=who_evaluates.slug)

    if request.method != 'POST':
        form = IncreaseRatingForm()
    else:
        form = IncreaseRatingForm(data=request.POST)
        if form.is_valid():
            Comment.objects.create(
                autor=who_evaluates.username,
                belong_to=who_do_we_evaluate,
                text=form.cleaned_data.get('text'),
                rating_value=form.cleaned_data.get('rating_value')
            )
            # Увеличиваем значение рейтинга на величину переданного значения
            who_do_we_evaluate.rating = F('rating') + form.cleaned_data.get('rating_value')
            who_do_we_evaluate.save()

            return redirect('users_app:see_reviews', slug_name=who_do_we_evaluate.slug)

    context = {
        'title': 'Оценить',
        'form': form,
        'who_do_we_evaluate': who_do_we_evaluate,
        'review': who_do_we_evaluate.comment_set.count(),
        'values': [0, 1, 2, 3, 4, 5],
    }
    return render(request, 'users_app/increase_rating.html', context)


def see_reviews_view(request, slug_name):
    """ Возвращает страницу просмотра отзывов """

    hairdresser = Hairdresser.objects.get(slug=slug_name)
    reviews = hairdresser.comment_set.order_by('-date_added')
    context = {
        'title': 'Просмотр отзывов',
        'hairdresser': hairdresser,
        'reviews': reviews,
    }

    return render(request, 'users_app/see_reviews.html', context)
