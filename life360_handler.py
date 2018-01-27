import time
import pickle
from collections import defaultdict

from bs4 import BeautifulSoup
from selenium import webdriver
from geopy.geocoders import Nominatim
from geopy.distance import vincenty

from config import LIFE360_CONFIG, LIFE360_PARAMS


class Life360Handler(object):
    def __init__(self):

        service_args = [
            '--ignore-ssl-errors=true',
            '--ssl-protocol=any'
        ]
        self.driver = webdriver.PhantomJS(service_args=service_args)

        self.driver.get(LIFE360_CONFIG['url'])

        button = self.driver.find_element_by_xpath(
            '//*[@id="loginForm"]/div/div[4]/button')
        print button
        username = self.driver.find_element_by_name(
            'phone')

        password = self.driver.find_element_by_name(
            'password')

        username.send_keys(LIFE360_CONFIG['phone'])
        password.send_keys(LIFE360_CONFIG['password'])
        button.click()

        current_url = self.driver.current_url
        wait_timer = 0
        while current_url == self.driver.current_url and wait_timer < 5:
            time.sleep(1)
            wait_timer += 1
        time.sleep(1)

    def get_location(self):
        device_user_map = LIFE360_PARAMS['device_id']

        location_map = {}
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        for ele in soup.find_all('pre'):
            items = ele.text.split('\n')

            temp_dict = {}
            keys = ['ID', 'latitude', 'longitude']
            for item in items:
                content = item.strip()
                if ':' in content:
                    key, value = content.split(':')
                    if key in keys:
                        key = key.strip()
                        value = value.strip()
                        temp_dict[key] = value

            if 'ID' in temp_dict:
                device_id = temp_dict['ID']
                location_map[device_user_map[device_id]] = temp_dict

        if 'user1' in location_map and 'user2' in location_map:
            print location_map['user1']
            print location_map['user2']

        return location_map

    def __del__(self):
        """Destructor"""
        self.driver.quit()
