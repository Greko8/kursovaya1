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

