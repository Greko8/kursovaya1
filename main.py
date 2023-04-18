
import logging
from classes import YaUploader
from classes import VkClass

if __name__ == '__main__':
    token = 'vk1.a.72y7eJa5ULjMAVZ2KgWXITmjkO_zsvby1VJuTLaKnLa12r6jwp6mLLTO5LsZo10hSgXV1fk3sj34eKsBG3N4RdJ6PaRMx1iZrQU6a-0byzRKE0DgLm68vEDlclOMgZlxWqzfa85qka1BXdGvkjMCTh6shBxatt00WgbpFMY5WD_yCZ3I2TTIRs_ogNWgkJsYLbVJN33AEyxJvhSOUtY8BQ'
    logging.basicConfig(level=logging.INFO, filename="log.log",filemode="w", encoding='utf-8', format="%(asctime)s %(levelname)s %(message)s")
    owner_id = input('Введите ID пользователя в VK: ')
    ya_token = input('Введите токен с полигона Яндекс: ')
    getvklist = VkClass(token)
    res_vk = getvklist.download_photos(owner_id, 6)
    uploader = YaUploader(ya_token)
    res = uploader.upload(str(owner_id))






