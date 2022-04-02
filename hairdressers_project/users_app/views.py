from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, ListView, DetailView

from .forms import *


def homepage_view(request):
    """Возвращает главную страницу сайта"""

    context = {
        'title': 'Парикмахеры Беларуси'
    }

    return render(request, 'users_app/index.html', context=context)


class RegistrationUserView(CreateView):
    """
    Возвращает форму решистрации пользователя и, в случае успешной регистрации,
    перенаправляет пользователя на главную страницу сайта
    """

    form_class = RegistrationUserForm
    template_name = 'users_app/register.html'
    success_url = reverse_lazy('users_app:homepage')

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
        # return redirect('users_app:homepage')
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
    return redirect(request.META.get('HTTP_REFERER'))


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

# class GetmMainProfile(DetailView):
#
#     model = SimpleUser
#     template_name = 'users_app/main_profile.html'
#     slug_url_kwarg = 'slug_name'
#     context_object_name = 'profile'
#
#     def get_context_data(self, *, object_list=None, **kwargs):
#         context = super().get_context_data(*kwargs)
#         context['title'] = 'Профиль'
#         context['username'] = profile.username
#         return context


def get_main_profile(request, slug_name):
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
