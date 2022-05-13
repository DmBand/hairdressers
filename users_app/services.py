import os
import shutil

from .models import SimpleUser, Hairdresser

from hairdressers_project.settings import MEDIA_ROOT

MAX_COUNT = 20


def check_number_of_files_in_portfolio(person_slug: str, new_files: list):
    """
    Проверяет уже имеющееся количество файлов в портфолио пользователя.
    Один пользователь может загружать не более 20 фотографий в портфолио (MAX_COUNT).
    По мере добавления новых фотографий, старые будут удаляться.
    """

    # Опеределяем путь к файлам и название файлов в портфолио.
    # Если директория не найдена, значит пользователь добавляет файлы первый раз -
    # прекращаем работу функции
    directory = f'{MEDIA_ROOT}/portfolio/{person_slug}'
    try:
        files = os.listdir(directory)
    except FileNotFoundError:
        return

    # Формируем список файлов по дате создания (самые старые идут в конце списка):
    # 1) формируем словарь, в котором ключ - название файла, значение - дата создания файла;
    # 2) Сотрируем словарь по убыванию (у старых файлов время создания меньше, чем у новых);
    # 3) Получаем список названий файлов, отсортированный по дате создания.
    all_files = {str(f): os.path.getmtime(f'{directory}/{f}') for f in files}
    the_oldest = sorted(all_files, key=all_files.get, reverse=True)

    # Определяем количество файлов в портфолио и количество новых файлов
    number_of_files_in_portfolio = len(files)
    number_of_recived_files = len(new_files)

    # Если портфолио пустое, то прекращаем работу функции
    if number_of_files_in_portfolio == 0:
        return

    # Если портфолио полное, то удаляем нужное количество старых файлов,
    # равное количеству новых файлов
    elif number_of_files_in_portfolio == MAX_COUNT:
        files_to_be_deleted = the_oldest[-number_of_recived_files:]
        for f in files_to_be_deleted:
            os.remove(f'{directory}/{f}')

    # Если после добавления новых файлов общее количество станет > 20,
    # то удаляем лишние старые файлы
    elif number_of_files_in_portfolio + number_of_recived_files > MAX_COUNT:
        number_of_files_to_delete = (number_of_files_in_portfolio + number_of_recived_files) - MAX_COUNT
        files_to_be_deleted = the_oldest[-number_of_files_to_delete:]
        for f in files_to_be_deleted:
            os.remove(f'{directory}/{f}')


def check_number_of_files_in_avatar_directory(person_slug: str):
    """
    Проверяет наличие аватара в папке пользователя и,
    в случае загрузки нового аватара, удаляет старый из папки хранения
    """

    # Определяем директорию хранения файлов
    directory = f'{MEDIA_ROOT}/avatars/{person_slug}'
    try:
        files = os.listdir(directory)
    # Если директории нет, то пользователь добавляет фото первый раз - останавливаем работу функции
    except FileNotFoundError:
        return
    else:
        os.remove(f'{directory}/{files[0]}')


def delete_portfolio_directory(person_slug: str):
    """ Удаляет папку портфолио со всеми фотографиями  """

    directory = f'{MEDIA_ROOT}/portfolio/{person_slug}'
    try:
        shutil.rmtree(directory)
    # Если папки нет, то пользователь не добавлял фото в портфолио
    except FileNotFoundError:
        return


def delete_avatar_directory(person_slug: str):
    """ Удаляет папку аватара с самим аватаром  """

    directory = f'{MEDIA_ROOT}/avatars/{person_slug}'
    try:
        shutil.rmtree(directory)
    # Если папки нет, то пользователь не добавлял фото в портфолио
    except FileNotFoundError:
        return


def create_new_user(user: object):
    """ Создаёт нового пользователя в БД (после регистрации) """

    return SimpleUser.objects.create(
        owner=user,
        username=user.username,
        name=user.first_name.title(),
        surname=user.last_name.title(),
        email=user.email,
        slug=user.username,
    )


def create_new_hairdresser(user: object, data: dict, files: list):
    """ Создаёт нового парикмахера """

    the_hairdresser = Hairdresser.objects.create(
        city=data.get('city'),
        phone=data.get('phone'),
        instagram=data.get('instagram'),
        another_info=data.get('another_info'),
        owner=user,
    )
    all_skills = data.get('skills')
    the_hairdresser.skills.add(*all_skills)

    if files:
        check_number_of_files_in_portfolio(person_slug=user.slug, new_files=files)
        for f in files:
            the_hairdresser.portfolio = f
            the_hairdresser.save()

    return the_hairdresser