from django.db.models import F

from users_app.models import SimpleUser
from .models import Comment


def get_selection_by_filters(model,
                             context,
                             city=None,
                             skills=None,
                             sort_option='-rating') -> dict:
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


def create_new_comment(author: SimpleUser,
                       belong_to: SimpleUser,
                       data: dict) -> Comment:
    """ Создаёт новый отзыв о парикмахере """
    new_coment = Comment.objects.create(
        autor=author.username,
        belong_to=belong_to.hairdresser,
        text=data.get('text'),
        rating_value=data.get('rating_value')
    )
    # Увеличиваем рейтинг
    belong_to.hairdresser.rating = F('rating') + data.get('rating_value')
    belong_to.hairdresser.save()
    return new_coment
