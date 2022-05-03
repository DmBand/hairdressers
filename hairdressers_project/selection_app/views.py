from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect
from django.views import View

from users_app.models import City, Skill, SimpleUser, Hairdresser
from .forms import IncreaseRatingForm
from .services import *


# selection
class SelectionView(View):
    """
    Возвращает страницу подбора парикмахераов:
    включает в себя фильтрацию по городу и навыкам
    """

    context = {
        'title': 'Подбор',
        'city': City.objects.order_by('name'),
        'skills': Skill.objects.order_by('name'),
        'hairdresser': Hairdresser.objects.order_by('-rating'),
        'current_city': 'Город не выбран',
        'chosen_skills': [],
    }

    def get(self, request):
        if request.GET.get('reset'):
            return render(request, 'selection_app/selection.html', self.context)

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

            return render(request, 'selection_app/selection.html', new_context)

        else:
            return render(request, 'selection_app/selection.html', self.context)


# rating and review
@login_required(login_url='users_app:login')
def increase_rating_view(request, slug_name):
    """ Возвращает страницу повышения рейтинга и добавления отзыва """

    # Кого оцениваем
    who_do_we_evaluate = SimpleUser.objects.get(slug=slug_name)
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
            create_new_comment(autor=who_evaluates, belong_to=who_do_we_evaluate, data=form.cleaned_data)

            return redirect('selection_app:see_reviews', slug_name=who_do_we_evaluate.slug)

    context = {
        'title': 'Оценить',
        'form': form,
        'who_do_we_evaluate': who_do_we_evaluate,
        'review': who_do_we_evaluate.hairdresser.comment_set.count(),
        'values': [0, 1, 2, 3, 4, 5],
    }
    return render(request, 'selection_app/increase_rating.html', context)


def see_reviews_view(request, slug_name):
    """ Возвращает страницу просмотра отзывов """

    # hairdresser = Hairdresser.objects.get(slug=slug_name)
    the_hairdresser = SimpleUser.objects.get(slug=slug_name)
    reviews = the_hairdresser.hairdresser.comment_set.order_by('-date_added')
    context = {
        'title': 'Просмотр отзывов',
        'the_hairdresser': the_hairdresser,
        'reviews': reviews,
    }

    return render(request, 'selection_app/see_reviews.html', context)
