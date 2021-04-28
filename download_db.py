import requests
import re
import os
from urllib.parse import urlencode
from tqdm import tqdm


def download_db(files):
    os.mkdir('db')
    os.chdir('db')
    for public_key, name_db in files:
        cloud_api = 'https://cloud-api.yandex.net/' \
                    'v1/disk/public/resources/download?'
        final_url = cloud_api + urlencode(dict(public_key=public_key))
        response = requests.get(final_url)
        download_url = response.json()['href']
        file_size = int(re.search(r'size=(.+?)&', download_url)[1])
        num_bars = int(file_size / 1024)
        download_response = requests.get(download_url, stream=True)
        with open(name_db, 'wb') as f:
            for chunk in tqdm(
                    download_response.iter_content(1024),
                    total=num_bars,
                    unit='KB',
                    desc=name_db,
                    leave=True):
                f.write(chunk)


if __name__ == '__main__':
    download_db([('https://yadi.sk/d/s69rV4Ub3yW6pg', 'geocoder.db'),
                 ('https://yadi.sk/d/H3tXEgrJf6hahg', 'kdtree.txt')])
