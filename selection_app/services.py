from django.db.models import F

from .models import Comment


def get_selection_by_filters(model, context, city=None, skills=None, sort_option='-rating'):
    """Возвращает результат фильтрации парикмахеров по городу и навыкам"""
    if city and skills:
        context['hairdresser'] = (model.objects
                                  .filter(city=city, skills__in=skills)
                                  .distinct()
                                  .order_by(sort_option))
    elif city and not skills:
        context['hairdresser'] = (model.objects
                                  .filter(city=city)
                                  .order_by(sort_option))
    elif not city and skills:
        context['hairdresser'] = (model.objects
                                  .filter(skills__in=skills)
                                  .distinct()
                                  .order_by(sort_option))
    return context


def create_new_comment(autor: object, belong_to: object, data: dict):
    """ Создаёт новый отзыв о парикмахере """
    new_coment = Comment.objects.create(
        autor=autor.username,
        belong_to=belong_to.hairdresser,
        text=data.get('text'),
        rating_value=data.get('rating_value')
    )
    # Увеличиваем рейтинг
    belong_to.hairdresser.rating = F('rating') + data.get('rating_value')
    belong_to.hairdresser.save()

    return new_coment
