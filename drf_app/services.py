import base64
import os
import random

from hairdressers_project.settings import (MEDIA_ROOT,
                                           MEDIA_URL,
                                           HOST_FOR_API,
                                           DEBUG)
from users_app.services import (check_number_of_files_in_portfolio,
                                MAX_COUNT,
                                compress_images_in_portfolio)


def get_images(images: list, username: str) -> None or dict:
    """
    Получает список файлов, декодирует их и сохраняет
    в портфолио пользователя или возвращает словарь с ошибками
    """

    errors = {
        'count': 0,
        'message': 'Поврежденный поток данных при чтении файла изображения'
    }
    b_images = [str.encode(img) for img in images if img]
    check_number_of_files_in_portfolio(
        person_slug=username,
        new_files=b_images
    )
    directory = f'{MEDIA_ROOT}/portfolio/{username}'
    if not os.path.isdir(directory):
        os.mkdir(directory)
    for index, value in enumerate(b_images):
        files = os.listdir(directory)
        while True:
            name = f'img_{random.randrange(MAX_COUNT + 1)}.jpg'
            if name not in files:
                break
        try:
            img_dec = base64.decodebytes(value)
        except:
            errors['count'] += 1
        else:
            with open(f'{directory}/{name}', 'wb') as img:
                img.write(img_dec)

    compresion_errors = compress_images_in_portfolio(person_slug=username)
    # если есть ошибки при сжатии, то суммируем их
    # с количеством ошибок при чтении данных файла
    if compresion_errors:
        compresion_errors['count'] += errors['count']
        return compresion_errors
    else:
        if errors['count'] > 0:
            return errors


def get_photo_urls(username: str) -> dict or None:
    """ Получение ссылок на все фото в портфолио """

    if not DEBUG:
        host = HOST_FOR_API
    else:
        host = 'http://127.0.0.1:8000'

    directory = f'{MEDIA_ROOT}/portfolio/{username}'
    try:
        files = [f for f in os.listdir(directory)]
    except FileNotFoundError:
        return
    else:
        urls_list = [f'{host}{MEDIA_URL}portfolio/{username}/{f}' for f in files]
        urls = {'urls': urls_list}
        return urls
