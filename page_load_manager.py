import os
import re
import glob

from pathlib import Path
from urllib.parse import urlparse

import requests
from loguru import logger


RAW_DATA_FOLDER = 'raw_data/'
OUTPUT_FOLDER = 'output/'

logger.add('error.log', format='{time} {level} {message}',
           level='ERROR', rotation='3 MB', compression='zip')


class PageLoad:
    def get(self, url):
        """
        docstring
        """
        raise NotImplementedError


def get_path_to_file(url: str):
    parse_url = urlparse(url)
    path = parse_url.path
    # file_name = re.sub('[\W]+', '', parse_url.query)
    file_name = parse_url.query
    if not file_name:
        path = Path(parse_url.path)
        file_name = path.name if path.name else 'index'
        path = f"{str(path.parent) if str(path.parent) != '/' else ''}/"
    return f'{RAW_DATA_FOLDER}{parse_url.hostname}{path}{file_name}'


class PageLoadFromFile(PageLoad):

    def get(self, url):
        template_find_path = f'{get_path_to_file(url)}*'
        file_path = glob.glob(template_find_path)[0]
        with open(file_path, 'r') as f:
            contents = f.read()
        logger.debug(
            'Get from file {}', file_path, feature='f-strings')
        return contents

    def get_path_to_url(self, url):
        parse_url = urlparse(url)
        return parse_url.hostname + parse_url.path

    def is_file_exist(self, url: str):
        return len(glob.glob(f'{get_path_to_file(url)}*'))


class PageLoadFromWeb:

    def __init__(self, headers: dict = None):
        self.session = requests.Session()
        # todo: ротация User-Agent
        self.session.headers = headers if headers else {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:83.0) Gecko/20100101 Firefox/83.0',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        self._response = requests.Response()

    def load(self, url: str, params: dict = None):
        # todo: обернуть в блок try
        params = params if params else {}
        self._response = self.session.get(url, params=params)
        logger.debug(
            'Load url {} Status: {}', self._response.url, self._response.status_code, feature='f-strings')

    def _get_response_type(self):
        return self._response.headers['Content-Type'].split(';')[0].split('/')[1]

    def get_raw_response(self):
        return self._response

    def get_text(self):
        return self._response.text

    def save_response_to_file(self):
        if self._response.ok:
            file_path = Path(
                f'{get_path_to_file(self._response.url)}.{self._get_response_type()}')
            if not file_path.parent.exists():
                file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w') as f:
                f.write(self.get_text())
            logger.debug('Save response to {}', file_path, feature='f-strings')
        else:
            raise Exception(f'Return code {self._response.status_code}')


class PageLoadManager:
    def __init__(self):
        self.local_manager = PageLoadFromFile()
        self.web_manager = PageLoadFromWeb()

    def get(self, url: str):
        # file_path = local_manager.get_path_to_url(url)
        if self.local_manager.is_file_exist(url):
            return self.local_manager.get(url)
        else:
            self.web_manager.load(url)
            self.web_manager.save_response_to_file()
            return self.web_manager.get_text()


@logger.catch
def main():
    # url = 'https://www.olx.ua/nedvizhimost/kvartiry-komnaty/arenda-kvartir-komnat/kvartira/kiev/?search%5Bdistrict_id%5D=3'
    # url = 'https://www.olx.ua/nedvizhimost/kvartiry-komnaty/arenda-kvartir-komnat/kvartira/kiev/'
    url = 'https://attack.mitre.org/'
    # url = 'https://www.olx.ua/nedvizhimost/kvartiry-komnaty/arenda-kvartir-komnat/kvartira/kiev/?search%5Bdistrict_id%5D=3'
    web_manager = PageLoadFromWeb()

    page_load_manager = PageLoadManager()

    print(page_load_manager.get(url)[:50])


if __name__ == "__main__":
    main()
