import base64
import os
import shutil
import random

from hairdressers_project.settings import MEDIA_ROOT
from users_app.services import (check_number_of_files_in_portfolio,
                                MAX_COUNT,
                                compress_images_in_portfolio)


def get_images(images: list, username: str) -> None:
    b_images = list(map(str.encode, images))
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
            name = f'img_{random.randrange(MAX_COUNT+1)}.jpg'
            if name not in files:
                break
        with open(f'{directory}/{name}', 'wb') as img:
            # try:
            img_dec = base64.decodebytes(value)
            img.write(img_dec)
            try:
                compress_images_in_portfolio(person_slug=username)
            except:
                print('no...')
                shutil.rmtree(f'{directory}/{name}')
