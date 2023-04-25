import requests
import json
import os
import time
import logging
from tqdm import tqdm
import module

class VkClass:
    def __init__(self, token: str):
        self.token = token

    def get_photos(self, owner_id, count=5):
        logging.info('Получаем список фото для загрузки')
        URL = 'http://api.vk.com/method/photos.get'
        params = {
            'owner_id' : owner_id,
            'album_id' : 'profile',
            'extended' : 1,
            'rev' : 1,
            'count' : count,
            'photo_sizes' : 1,
            'access_token' : self.token,
            'v' : '5.131'
        }
        result = requests.get(URL, params=params)
        photos_list = result.json()
        return result.json()

    def download_photos(self, owner_id, count=5):
        photos_list = self.get_photos(owner_id, count)
        if 'response' in photos_list:
            logging.info('Список фото получен успешно.')
            file_names = []
            likes_list = []
            files_list = {}
            # Получаем название файла, выбираем максимальный размер файла
            for item in photos_list['response']['items']:
                likes = item['likes']['count']
                date = item['date']
                likes_list.append(likes)
                if likes in likes_list[:-1:]:
                    filename = str(likes) + '_' + str(date) + '.jpg'
                else:
                    filename = str(likes) + '.jpg'
                height_list = []
                max_height = 0
                # Получаем ссылку на файл с максимальным разрешением
                for size in item['sizes']:
                    height_list.append(size['height'])
                    max_height = max(height_list)
                    if size['height'] >= max_height:
                        url_photo = size['url']
                        type = size['type']
                files_list[filename] = [url_photo, type]
            print('Скачиваем фото из ВК...')
            if not os.path.isdir(str(owner_id)): # Создаем временную папку для хранения скачанных файлов
                os.mkdir(str(owner_id))
                logging.info(f'Временная папка {owner_id} создана')
            data = []
            # Скачиваем фото с профиля в ВК в временную папку
            for name, url in tqdm(files_list.items()):
                time.sleep(0.2)
                r = requests.get(url[0])
                file_data = {}
                with open(os.path.join(str(owner_id), name), 'wb') as f:
                    f.write(r.content)
                file_data['filename'] = name
                file_data['size'] = url[1]
                data.append(file_data)
            logging.info('Фотографии с профиля ВК скачаны во временную папку')
            module.write_json(data)
        else:
            logging.error(f'ошибка запроса в ВК, код ошибки: {photos_list["error"]["error_code"]}')
            print('Ошибка выполнения программы.')
            exit()