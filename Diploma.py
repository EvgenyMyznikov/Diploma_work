import requests
from tqdm import tqdm
import os
from pprint import pprint


class YaToVkUploader:
    def __init__(self, auth_token, token_vk, vk_id=input('input vk id: '), folder_name=input('input folder name: ')):
        self.ya_token = auth_token
        self.vk_token = token_vk
        self.folder_name = folder_name
        self.vk_id = vk_id
        self.headers = {"Authorization": f"OAuth {token}"}

    @staticmethod
    def get_largest_photo(photo_sizes):
        if photo_sizes['width'] >= photo_sizes['height']:
            return photo_sizes['width']
        else:
            return photo_sizes['height']

    @staticmethod
    def download_photo(url):
        response = requests.get(url, stream=True)
        photo_name = url.split('/')[3] + '.jpg'
        with open(photo_name, 'wb') as photo:
            for chunk in response.iter_content(4096):
                photo.write(chunk)

    def get_vk_photos(self):
        params = {'access_token': self.vk_token, 'owner_id': self.vk_id,
                  'album_id': 'wall', 'photo_sizes': 1, 'v': 5.52}
        response = requests.get('https://api.vk.com/method/photos.get', params=params)
        photos = response.json()['response']['items']

        for photo in tqdm(photos):
            sizes = photo['sizes']
            max_size_url = max(sizes, key=self.get_largest_photo)['src']
            self.download_photo(max_size_url)

    def new_folder(self):
        url_folder = "https://cloud-api.yandex.net/v1/disk/resources"
        params = {'path': self.folder_name, 'overwrite': True}
        response = requests.put(url=url_folder, params=params, headers=self.headers)
        return response

    def get_upload_url(self, file_name):
        url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        params = {'path': f"/{self.folder_name}/" + file_name, 'overwrite': True}
        url_upload = requests.get(url=url, params=params, headers=self.headers)
        return url_upload.json()['href']

    @staticmethod
    def upload(url, file_path):
        with open(file_path, 'rb') as f:
            response = requests.put(url, data=f)
            return response

    def ya_disk_info(self):
        url_disk = "https://cloud-api.yandex.net/v1/disk/resources"
        params = {'path': self.folder_name, 'fields': '_embedded.items.name,_embedded.items.size'}
        response = requests.get(url=url_disk, params=params, headers=self.headers)
        return response.json()["_embedded"]['items']


if __name__ == '__main__':
    token = input('input ya_disk token: ')
    vk_token = '958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008'
    vk_to_ya_upload = YaToVkUploader(token, vk_token)
    vk_to_ya_upload.get_vk_photos()
    files = os.listdir()
    for file in tqdm(files):
        if '.jpg' in file:
            path = file
            uploader = YaToVkUploader(token, vk_token)
            disk_folder = uploader.new_folder()
            upload_url = uploader.get_upload_url(file)
            result = uploader.upload(upload_url, path)
    info = YaToVkUploader(token, vk_token)
    print('======Photos successfully uploaded!======')
    pprint(info.ya_disk_info())
