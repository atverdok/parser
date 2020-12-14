import datetime
from collections import namedtuple
import os
import urllib.parse

import bs4
import requests
import dateparser

from page_load_manager import PageLoadManager
from exporter import ExportSpiderData, ExportCsv, ExportJson


InnerBlock = namedtuple('Block', 'title,price,date,district,url,img')


class Block(InnerBlock):

    def __str__(self):
        return f'{self.title}\t{self.price}\t{self.date}\t{self.district}\t{self.url}\t{self.img}'


class OlxParser:

    def __init__(self, url_base: str = None, exporter: ExportSpiderData = None):
        self.url_base = url_base if url_base else 'https://www.olx.ua/nedvizhimost/kvartiry-komnaty/arenda-kvartir-komnat/kvartira/kiev/?'

        # self.session = requests.Session()
        # self.session.headers = {
        #     'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:83.0) Gecko/20100101 Firefox/83.0',
        #     'Accept-Language': 'en-US,en;q=0.5',
        # }
        self.load_manager = PageLoadManager()
        self.exporter = exporter if exporter else ExportCsv()

    def get_page(self, page: int = None):
        params = {
            'search[district_id]': 3,
        }
        if page and page > 1:
            params['page'] = page

        # r = self.session.get(self.url_base, params=params)
        r = self.load_manager.get(
            f'{self.url_base}{urllib.parse.urlencode(params)}')
        return r

    def get_data(self):
        html = self.get_page()
        soup = bs4.BeautifulSoup(html, 'lxml')
        data = []

        container = soup.select(
            '#offers_table tbody tr td div table tbody')
        for item in container:
            block = self.parse_block(item)
            # print(block)
            data.append(block)
        if data:
            self.exporter.export('test', data)

    def parse_block(self, item):
        url = item.select_one('h3 a')
        if url:
            url = url.get('href')
        else:
            url = None

        title = item.select_one('h3')
        if title:
            title = title.text.strip()
        else:
            url = None

        price = item.select_one('p.price')
        if price:
            price = price.text.strip()
        else:
            url = None

        img = item.select_one('img')
        if img:
            img = img.get('src')
        else:
            img = None

        bottom_cel = item.select('.bottom-cell .breadcrumb.x-normal')
        if bottom_cel and bottom_cel[0]:
            district = bottom_cel[0].text.strip()
        else:
            district = None

        if bottom_cel and bottom_cel[1]:
            date = str(dateparser.parse(bottom_cel[1].text.strip()))
        else:
            date = None
        return Block(title, price, date, district, url, img)


def main():
    # print(Block('test', '2000', 'now', 'https://test.com'))

    olx = OlxParser()
    # print(olx.get_page()[:50])
    olx.get_data()


if __name__ == "__main__":
    main()
