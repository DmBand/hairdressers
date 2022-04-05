from hairdressers_project.settings import MEDIA_ROOT
import os


def check_number_of_files_in_portfolio(person_slug: str, received_files: list):

    # Опеределяем путь к файлам и название файлов в портфолио, если они есть
    directory = f'{MEDIA_ROOT}/portfolio/{person_slug}'
    files = os.listdir(directory)

    number_of_files_in_portfolio = len(files)
    number_of_recived_files = len(received_files)
    if number_of_files_in_portfolio == 0:
        return

    elif number_of_files_in_portfolio == 20:
        the_oldest = files[-number_of_recived_files:]
        for f in the_oldest:
            os.remove(f'{directory}/{f}')

    elif number_of_files_in_portfolio + number_of_recived_files > 20:
        number_of_files_to_delete = (number_of_files_in_portfolio + number_of_recived_files) - 20
        the_oldest = files[-number_of_files_to_delete:]
        for f in the_oldest:
            os.remove(f'{directory}/{f}')


