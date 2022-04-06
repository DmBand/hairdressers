from django.db.models import Q
from django.shortcuts import render
from django.views import View

from users_app.models import City, Hairdresser, Skill
from .services import get_selection_by_filters


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
