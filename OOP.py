from pprint import pprint
import requests
from datetime import datetime
import json
import os
TOKEN = str(input('Введите токен ВК: '))
TOKEN_yan = str(input('Введите токен Яндекс диска: '))
class VKAPICllient:
    API_BASE_URL = 'https://api.vk.com/method'

    def __init__(self, token, user_id, size):
        self.token = token
        self.user_id = user_id
        self.size = size
       
    def _build_url(self, api_method):
        return f"{self.API_BASE_URL}/{api_method}"

    def get_common_params(self):
        return {
            'access_token': self.token,
            'v': '5.131'
                }
    
    def get_profile_photos(self):
        params = self.get_common_params()
        photos_params = ({'owner_id': self.user_id, 'album_id': 'profile', 'extended': 1, 'photo_sizes': 1})
        response = requests.get(self._build_url('photos.get'), params={**params, **photos_params})
        return response.json()
       
    def download_dis(self):
        """скачать в текущую папку на диске и создание json файла"""
        profile_photos = self.get_profile_photos()
        for photos in profile_photos['response']['items']:
            maximum_size = self.size
            filtered_list = list(filter(lambda d: maximum_size in d.values(), photos['sizes']))
            for max_size in filtered_list:
                post_date = datetime.fromtimestamp(photos['date'])
                names = photos['likes']['count']
                url_ = max_size['url']
                response = requests.get(url_)
                name = f"{str(names)}.jpg"
                if os.path.exists(name):
                    name = f"{str(names)}_{post_date.strftime('%d %B %Y')}.jpg"
                with open(name, 'wb') as photo_file:
                    photo_file.write(response.content)
                json_data = {'name': name, 'date': post_date.strftime('%d %B %Y'), 'url': url_}
                json_filename = 'photo_data.json'
                if os.path.exists(json_filename):
                    with open(json_filename, 'r') as json_file:
                        json_data_list = json.load(json_file)
                        json_data_list.append(json_data)
                    with open(json_filename, 'w') as json_file:
                        json.dump(json_data_list, json_file, indent=4)
                else:
                    with open(json_filename, 'w') as json_file:
                        json.dump([json_data], json_file, indent=4)


class YandexDisk:
    API_BASE_YANDEX = 'https://cloud-api.yandex.net'

    def __init__(self, token, new_folder):
        self.token = token
        self.new_folder = new_folder

    def _build_yandex(self, api_method):
        """Функция для составления запросов"""
        return f"{self.API_BASE_YANDEX}/{api_method}"
    
    def _headers(self):
        """Функция для авторизации"""
        author = f"OAuth {self.token}"
        headers = {'Authorization': author}
        return headers

    def create_dir(self):
        """создание папки на яндекс диске"""
        params = {'path': self.new_folder}
        response = requests.put(self._build_yandex('v1/disk/resources'), params=params, headers=self._headers())
        return response.json()
    
    def download_yandex(self):
        url_for_upload = self._build_yandex('v1/disk/resources/upload')       
        with open('photo_data.json', 'r') as f:
            json_string = f.read()
        data = json.loads(json_string)
        for d in data:
            params = {'path': f"{self.new_folder}/{d['name']}"}
            response = requests.get(url_for_upload, params=params, headers = self._headers())
            upload_ = response.json().get('href')
            name = d['name']
            with open(name, 'rb') as file:
                response = requests.put(upload_, files={'file': file})


if __name__ ==  '__main__':
    user_id = input('введите id пользователя: ')
    size = str(input('введите желаемый размер фото: s, m, x, y, z, 0: '))
    n_folder = input('Введите название папки для яндекс диска: ')
    yan_disk = YandexDisk(TOKEN_yan, n_folder)
    vk_client = VKAPICllient(TOKEN, user_id, size)
    folder = yan_disk.create_dir()
    pprint(vk_client.download_dis())
    pprint(yan_disk.download_yandex())

