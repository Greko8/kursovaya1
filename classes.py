import requests
import json
from pprint import pprint
import os
import time
import shutil
import logging
from tqdm import tqdm

class YaUploader:
    def __init__(self, token: str):
        self.token = token

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token)
        }

    def create_folder(self, folder_name):
        # Метод создает директорию на яндекс.диск, куда будут загружены файлы
        logging.info('Создаем папку в Яндекс.Диск')
        url = "https://cloud-api.yandex.net/v1/disk/resources/"
        headers = self.get_headers()
        res = requests.put(f'{url}?path={folder_name}', headers=headers)
        if res.status_code == 201:
            logging.info(f'Папка {folder_name} создана.')
        elif res.status_code == 409:
            logging.warning('Папка уже существует.')
        else:
            logging.error(f'Ошибка создания папки. Код ошибки: {res.status_code}')
            print('Ошибка выполнения программы.')
            exit()
        return res

    def get_upload_link(self, disk_file_path):
        # Метод получает ссылку для загрузки фото на яндекс.диск
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        params = {'path': disk_file_path, 'overwrite': 'true'}
        headers = self.get_headers()
        responce = requests.get(upload_url, headers=headers, params=params)
        data = responce.json()
        if responce.status_code == 200:
            href = data.get('href')
            return href
        else:
            logging.error(f'Ошибка полчения ссылки с Яндекс.Диск: {data.get("message")}')
            print('Ошибка выполнения программы.')
            exit()

    def upload(self, disk_file_path):
        res = self.create_folder(disk_file_path)
        logging.info('Загрузка фото на Яндекс.Диск') # Загружаем все файлы на яндекс.диск из временной папки
        print('Загрузка фото на Яндекс.Диск:')
        for file in tqdm(os.listdir(disk_file_path)):
            time.sleep(0.5)
            href = self.get_upload_link(f'{disk_file_path}/{file}')
            with open(os.path.join(disk_file_path, file), 'rb') as f:
                responce = requests.put(href, files={'file': f})
        try:
            shutil.rmtree(disk_file_path)
            logging.info(f'Временная папка {disk_file_path} удалена ')
        except Exception as er:
            logging.warning(f'Ошибка удаления временной папки {disk_file_path}')
        return responce

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
            with open('files_data.json', 'w') as file:
                json.dump(data, file)
            logging.info('Создан файл files_data.json с данными о фотографиях')
        else:
            logging.error(f'ошибка запроса в ВК, код ошибки: {photos_list["error"]["error_code"]}')
            print('Ошибка выполнения программы.')
            exit()