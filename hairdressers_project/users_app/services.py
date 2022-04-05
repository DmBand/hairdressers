from hairdressers_project.settings import MEDIA_ROOT
import os

MAX_COUNT = 20


def check_number_of_files_in_portfolio(person_slug: str, new_files: list):
    """
    Проверяет уже имеющееся количество файлов в портфолио пользователя.
    Один пользователь может загружать не более 20 фотографий в портфолио (MAX_COUNT).
    По мере добавлений новых фотографий, старые будут удаляться.
    """

    # Опеределяем путь к файлам и название файлов в портфолио
    directory = f'{MEDIA_ROOT}/portfolio/{person_slug}'
    files = os.listdir(directory)

    # Формируем список файлов по дате создания (самые старые идут в конце):
    # 1) формируем словарь, в котором ключ - название файла, значение - дата создания файла;
    # 2) Сотрируем словарь по убыванию (у старых файлов время создания меньше, чем у новых);
    # 3) Получаем список названий файлов, отсортированный по дате создания
    the_oldest = sorted({str(f): os.path.getctime(f'{directory}\\{f}') for f in files}, reverse=True)

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
