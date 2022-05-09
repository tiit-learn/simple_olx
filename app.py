import os
import re
import requests
import json 
from lxml import html
from lxml.etree import _ElementUnicodeResult
from typing import List, Optional, Dict, Tuple
from time import time
import csv

from pprint import pprint

DIRS = ['debug', 'output']
AUTH_TOKEN = "" # need to get it from cookies in browser, name: a_access_token 
BASE_URL = "https://www.olx.kz/"
POSTS_XPATH = """//*/h4[@class="normal"]/*[contains(@class, 'link')]/@href"""
HEADERS = ["url", "id пользователя", "заголовок", "name", "телефон", "область", "город", "район", "категория", "подкатегория"]
OLX_API = {
    "user_info": lambda USER_ID: f"https://www.olx.kz/api/v1/users/{USER_ID}/",
    "user_offers": lambda USER_ID: f"https://www.olx.kz/api/v1/offers/?user_id={USER_ID}&offset=0"
}


class htmlRecipient :
    @staticmethod
    def open(url: str, headers: dict=None) -> str:
        if headers is None:
            Headers = {
               "authorization": f"Bearer {AUTH_TOKEN}"
            } 
        response = requests.get(url, headers=Headers)
        return response.text

class htmlParser:
    @staticmethod
    def parse_page_xpath(html_code: str, xpath_str: str) -> List[_ElementUnicodeResult]:
        parser = html.fromstring(html_code)
        return parser.xpath(xpath_str)
    
    @staticmethod
    def get_json_data(api_url: str) -> Dict:
        """Return converted json data as dict"""
        json_string = htmlRecipient.open(api_url)
        return json.loads(json_string)

    @staticmethod
    def get_offer_data(user_offers: dict, user_offer_id: str) -> Optional[Dict]:
        """Try to find and return ad id data in all offers of user"""
        if user_offers:
            for ad_data in user_offers.get('data', []):
                if str(ad_data.get('id', '')) == user_offer_id:
                    return ad_data
        return None

    @staticmethod
    def get_user_id(raw_html_element: str) -> Optional[str]:
        """Get USER ID from raw html data, using regex"""
        user_id_re_pattern = r'(?<=\\"id\\":)(\w+?)(?=,\\"name\\")'
        user_id = re.findall(user_id_re_pattern, raw_html_element)
        return user_id[0] if user_id else None

    @staticmethod
    def get_ad_id(raw_html_element: str) -> Optional[str]:
        """Get AD ID from raw html data, using xpath"""
        html_element = htmlParser.parse_page_xpath(
                 raw_html_element,
                "//*[@data-cy='ad-footer-bar-section']/span")
        return str(
            html_element[0].text_content().split(": ")[-1].strip()
            ) if html_element else None

    
class olxPostParser(htmlParser):
    def __init__(self, url: str) -> None:
        self.url = url
        self.html = htmlRecipient.open(self.url)
        self.ad_id = htmlParser.get_ad_id(self.html)
        self.user_id = htmlParser.get_user_id(self.html)
        if self.user_id is None:
            with open(f'debug/{time()}.html', 'w', encoding='utf-8') as f:
                f.write(self.html)
            print(f'Problem:\n\tself.ad_id: {self.ad_id}\n\tself.url: {self.url}')
            self.user_data = None
            self.user_offer_data = None
        else:
            self.user_data = htmlParser.get_json_data(OLX_API["user_info"](self.user_id))
            self.user_offer_data = htmlParser.get_offer_data(
                htmlParser.get_json_data(OLX_API["user_offers"](self.user_id)),
                self.ad_id
            )

    def get_all_data(self) -> Tuple:
        data = (
            self.url,
            self.get_user_id(),
            self.get_offer_title(),
            self.get_user_name(),
            self.get_phone_number(),
            self.get_region(),
            self.get_city(),
            self.get_district(),
            self.get_category(),
            self.get_sub_category()
            )
        return data

    def __result(self, xpath: str) -> str:
        data = htmlParser.parse_page_xpath(
            self.html,
            xpath
        )
        return data[0].text_content() if len(data) > 0 else ''

    def __get_location(self, type: str) -> str:
        if self.user_offer_data and self.user_offer_data.get('location', None):
            location = self.user_offer_data['location'].get(type, '')
            return location['name'] if location else location
        return ''

    def get_user_id(self) -> str:
        return self.user_id

    def get_user_name(self) -> str:
        if self.user_data:
            user_data = self.user_data.get('data')
            return user_data.get('name', '') if user_data else ''
        return ''

    def get_offer_title(self) -> str:
        if self.user_offer_data:
            return self.user_offer_data.get('title', '') if self.user_offer_data else ''
        return ''

    def get_phone_number(self) -> str:
        return "$$$"
    
    def get_region(self) -> str:
        return self.__get_location('region')

    def get_city(self) -> str:
        return self.__get_location('city')
    
    def get_district(self) -> str:
        return self.__get_location('district')
    
    def get_category(self) -> str:
        xpath = '//*[@id="root"]//ol[@data-testid="breadcrumbs"]/li[2]'
        return self.__result(xpath)

    def get_sub_category(self) -> str:
        xpath = '//*[@id="root"]//ol[@data-testid="breadcrumbs"]/li[3]'
        return self.__result(xpath)

if __name__ == "__main__":
    for dir in DIRS:
        if not os.path.exists(dir):
            os.makedirs(dir)
    
    start_time = time()
    print(f'Start time: {start_time}')
    
    html_code = htmlRecipient.open(BASE_URL)
    post_links = htmlParser.parse_page_xpath(html_code, POSTS_XPATH)
    
    data = {
        "parse": [dict(zip(
            HEADERS,
            olxPostParser(link).get_all_data())
            ) for link in post_links]}

    pprint(data)

    try:
        filename = f'output/data_parse_{time()}.csv'
        with open(filename, 'w',
                    encoding="utf-8",
                    newline='') as f:
            writer = csv.DictWriter(f, fieldnames=HEADERS)
            writer.writeheader()
            writer.writerows(data['parse'])
    except ValueError as err:
        print('Faild to write data to CSV file', err)
        os.remove(filename)

    print(f'Finished at: {time() - start_time} sec')
