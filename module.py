import json
import logging

def write_json(data):
    with open('files_data.json', 'w') as file:
        json.dump(data, file)
    logging.info('Создан файл files_data.json с данными о фотографиях')