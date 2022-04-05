from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import *
from .models import City, Skill


def homepage_view(request):
    """Возвращает главную страницу сайта"""

    context = {
        'title': 'Парикмахеры Беларуси'
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
            form.save()
            return redirect('users_app:homepage')

    elif request.POST.get('avatar') == 'no':
        return redirect('users_app:homepage')

    else:
        form = AddAvatarForm()

    context = {'form': form, 'title': 'Добавить фото'}

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
    """Возвращает страницу парикмахера"""

    pers = Hairdresser.objects.get(slug=slug_name)
    skills = pers.skills.all().order_by('name')
    context = {
        'title': f'{pers.name.capitalize()} {pers.surname.capitalize()}',
        'avatar': pers.avatar,
        'rating': pers.rating,
        'city': pers.city,
        'skills': [skill.name for skill in skills],
        'phone': pers.phone,
        'email': pers.email,
        'instagram': pers.instagram,
        'another_info': pers.another_info,
    }

    return render(requset, 'users_app/portfolio.html', context)


def get_main_profile(request, slug_name):
    """ Возвращает страницу главного профиля пользователя """

    pers = SimpleUser.objects.get(slug=slug_name)
    context = {
        'title': 'Главный профиль',
        'username': pers.username,
        'name': pers.name,
        'surname': pers.surname,
        'email': pers.email,
        'avatar': pers.avatar
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
                for f in files:
                    the_hairdresser.portfolio = f
                    the_hairdresser.save()

            # Меняем флаг пользователя - он теперь парикмахер. И обязательно сохраняем
            user.is_hairdresser = True
            user.save()

            # Редирект на страницу портфолио
            return redirect('users_app:get_hairdresser', slug_name=request.user.username)

    context = {'title': 'Регистрация формы', 'form': form}

    return render(request, 'users_app/add_portfolio3.html', context)
