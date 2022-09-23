import base64
import datetime
import os
import random
import shutil

from hairdressers_project.settings import (MEDIA_ROOT,
                                           MEDIA_URL,
                                           HOST_FOR_API,
                                           DEBUG)
from users_app.models import (SimpleUser,
                              default_avatar_path)
from users_app.services import (check_number_of_files_in_portfolio,
                                MAX_COUNT,
                                compress_images_in_portfolio,
                                check_number_of_files_in_avatar_directory,
                                compress_avatar)

NUMBER_OF_CHANGES_PER_DAY = 1


def convert_and_save_photo_to_portfolio(images: list, username: str) -> None or dict:
    """
    Получает список файлов, декодирует их и сохраняет
    в портфолио пользователя или возвращает словарь с ошибками
    """

    errors = {
        'count': 0,
        'message': 'Поврежденный поток данных при чтении файла изображения.'
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

    compression_errors = compress_images_in_portfolio(person_slug=username)
    # если есть ошибки при сжатии, то суммируем их
    # с количеством ошибок при чтении данных файла
    if compression_errors:
        compression_errors['count'] += errors['count']
        return compression_errors
    else:
        if errors['count'] > 0:
            return errors


def set_default_avatar(user: SimpleUser) -> None:
    """ Устанавливает пользователю стандартный аватар """

    user.avatar = default_avatar_path
    user.default_avatar = True
    user.save()


def convert_and_save_avatar(image: str, user: SimpleUser) -> None or dict:
    """
    Получает список файлов, декодирует их и сохраняет
    в качестве аватара пользователя или возвращает словарь с ошибками
    """

    errors = {
        'count': 0,
        'message': 'Поврежденный поток данных при чтении файла изображения.'
    }
    b_image = str.encode(image)
    check_number_of_files_in_avatar_directory(person_slug=user.username)
    directory = f'{MEDIA_ROOT}/avatars/{user.username}'
    if not os.path.isdir(directory):
        os.mkdir(directory)
    try:
        img_dec = base64.decodebytes(b_image)
    except:
        errors['count'] += 1
        os.rmdir(directory)
    else:
        with open(f'{directory}/avatar.jpg', 'wb') as img:
            img.write(img_dec)
            user.avatar = f'/avatars/{user.username}/avatar.jpg'
            user.default_avatar = False
            user.save()

    compression_errors = compress_avatar(person_slug=user.username)
    if compression_errors:
        compression_errors['count'] += errors['count']
        set_default_avatar(user)
        return compression_errors
    else:
        if errors['count'] > 0:
            set_default_avatar(user)
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


def check_comments_count(who_evaluates: SimpleUser, who_do_we_evaluate: SimpleUser) -> bool:
    """
    Проверяет, комментировал ли сегодня
    пользователь выбранного парикмахера
    """

    now = datetime.datetime.today()
    return (who_do_we_evaluate
            .hairdresser
            .comments
            .filter(autor=who_evaluates, date_added__date=now)
            .exists())
