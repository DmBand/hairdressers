def get_selection_by_filters(model, context, city=None, skills=None, sort_option='-rating'):
    """Возвращает результат фильтрации парикмахеров по городу и навыкам"""

    if city and skills:
        context['hairdresser'] = model.objects.filter(
            city=city,
            skills__in=skills
        ).distinct().order_by(sort_option)
    elif city and not skills:
        context['hairdresser'] = model.objects.filter(
            city=city
        ).order_by(sort_option)
    elif not city and skills:
        context['hairdresser'] = model.objects.filter(
            skills__in=skills
        ).distinct().order_by(sort_option)

    return context

