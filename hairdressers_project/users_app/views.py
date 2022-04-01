from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect
from django.db.models import Q
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import CreateView

from .models import *
from .forms import *
from .services import get_selection_by_filters


def homepage_view(request):
    """Возвращает главную страницу сайта"""

    context = {
        'title': 'Парикмахеры Беларуси'
    }

    return render(request, 'users_app/index.html', context=context)


class SelectionView(View):
    """
    Возвращает страницу подбора парикмахераов:
    включает в себя фильтрацию по городу и навыкам
    """

    context = {
        'title': 'Подбор',
        'city': City.objects.all().order_by('name'),
        'skills': Skill.objects.order_by('name'),
        'hairdresser': Hairdresser.objects.order_by('-rating'),
        'current_city': 'Город не выбран',
        'chosen_skills': [],
    }

    def get(self, request):

        if request.GET.get('reset'):
            return render(request, 'users_app/selection.html', self.context)

        elif request.GET.get('city') or request.GET.get('skill'):
            new_context = self.context.copy()
            chosen_city = request.GET.get('city')
            if chosen_city:
                new_context['current_city'] = City.objects.get(id=chosen_city)
                # Убираем из списка городов выбранный город, чтобы он не отображался 2 раза
                new_context['city'] = City.objects.filter(~Q(id=chosen_city)).order_by('name')

            chosen_skill = [skill for skill in request.GET.getlist(key='skill')]
            if chosen_skill:
                # Определим переданные навыки, чтобы они отмечались как выбранные
                # после применения фильтра:
                new_context['chosen_skills'] = [int(id_) for id_ in chosen_skill]

            # Фильтруем результат в зависимости от переданных данных
            new_context = get_selection_by_filters(
                model=Hairdresser,
                context=new_context,
                city=chosen_city,
                skills=chosen_skill
            )

            return render(request, 'users_app/selection.html', new_context)

        else:
            return render(request, 'users_app/selection.html', self.context)


# def selection(request):
#     city_id = False
#     skill_id = False
#     context = {
#         'title': 'Подбор',
#         'city': City.objects.all().order_by('name'),
#         'skills': Skill.objects.order_by('name'),
#         'hairdresser': Hairdresser.objects.order_by('-rating'),
#         'current_city': 'Город не выбран',
#         'chosen_skills': [],
#     }
#
#     if request.method == 'POST':
#         # Если в запросе есть reset, то просто обновляем страницу, ничего не меняя в context
#         if 'reset' in request.POST:
#             context = context
#         else:
#             # Проверяем, передавался ли город
#             chosen_city = request.POST['city']
#             if chosen_city:
#                 city_id = True
#                 context['current_city'] = City.objects.get(id=chosen_city)
#                 # Убираем из списка городов выбранный город, чтобы он не отображался 2 раза
#                 context['city'] = City.objects.filter(~Q(id=chosen_city)).order_by('name')
#
#             # Проверяем, передавался ли навык
#             chosen_skill = [skill for skill in request.POST.getlist(key='skill')]
#             if chosen_skill:
#                 skill_id = True
#                 # Для определения, какой навык передали, чтобы он отмечался как выбранный после применения фильтра
#                 context['chosen_skills'] = [int(id_) for id_ in chosen_skill]
#
#             # Фильтруем результат в зависимости от переданных данных
#             if city_id and skill_id:
#                 context['hairdresser'] = Hairdresser.objects.filter(
#                     city=chosen_city,
#                     skills__in=chosen_skill
#                 ).distinct().order_by('-rating')
#             elif city_id and not skill_id:
#                 context['hairdresser'] = Hairdresser.objects.filter(city=chosen_city).order_by('-rating')
#             elif not city_id and skill_id:
#                 context['hairdresser'] = Hairdresser.objects.filter(
#                     skills__in=chosen_skill
#                 ).distinct().order_by('-rating')
#
#     return render(request, 'users_app/selection.html', context)


def one_hairdresser_view(requset, slug_name):
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

    return render(requset, 'users_app/one_hairdresser.html', context)


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
        Hairdresser.objects.create(
            owner=user,
            name=user.first_name.capitalize(),
            surname=user.last_name.capitalize(),
            email=user.email,
            slug=user.username
        )
        login(self.request, user)
        return redirect('users_app:homepage')


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
