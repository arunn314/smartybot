import time

from bs4 import BeautifulSoup
from selenium import webdriver

from config import ADT_CONFIG


class ADTHandler(object):
    def __init__(self):
        self.armed_status = ['Armed Away', 'Armed Stay']
        self.disarmed_status = ['Disarmed']

        service_args = [
            '--ignore-ssl-errors=true',
            '--ssl-protocol=tlsv1'
        ]
        self.driver = webdriver.PhantomJS(service_args=service_args)

        self.driver.get(ADT_CONFIG['url'])

        self.signin()

    def signin(self):
        if 'signin' in self.driver.current_url:
            username = self.driver.find_element_by_name('usernameForm')
            password = self.driver.find_element_by_name('passwordForm')
            username.send_keys(ADT_CONFIG['username'])
            password.send_keys(ADT_CONFIG['password'])
            password.submit()

    def get_status(self):
        if 'signin' in self.driver.current_url:
            self.signin()
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        value = soup.find('div', {'id': 'divOrbTextSummary'}) \
                    .find('span') \
                    .get_text()
        value = value.split('.')[0]
        print value
        return value

    def disarm(self):
        status = self.get_status()
        response_flag = 'Disarmed successfully'
        if status in self.armed_status:
            ele = self.driver.find_element_by_id('security_button_0')
            try:
                ele.click()
            except Exception as e:
                print e
                pass
            time.sleep(12)
            status = self.get_status()
            print status
            if status in self.disarmed_status:
                response_flag = 'Disarmed successfully'
        elif status in self.disarmed_status:
            response_flag = 'System is already disarmed'
        else:
            response_flag = 'Failure'

        return response_flag

    def arm_away(self):
        status = self.get_status()
        response_flag = 'Armed Away successfully'
        if status in self.disarmed_status:
            ele = self.driver.find_element_by_id('security_button_0')
            try:
                ele.click()
            except Exception as e:
                print e
                pass
            time.sleep(12)
            status = self.get_status()
            if status in self.armed_status:
                response_flag = 'Armed Away successfully'
        elif status in self.armed_status:
            response_flag = 'System is already armed'
        else:
            response_flag = 'Failure'

        return response_flag

    def arm_stay(self):
        status = self.get_status()
        response_flag = 'Armed Stay successfully'
        if status in self.disarmed_status:
            ele = self.driver.find_element_by_id('security_button_1')
            try:
                ele.click()
            except Exception as e:
                print e
                pass
            time.sleep(12)
            status = self.get_status()
            if status in self.armed_status:
                response_flag = 'Armed Stay successfully'
            print status
        elif status in self.armed_status:
            response_flag = 'System is already armed'
        else:
            response_flag = 'Failure'

        return response_flag


    def get_sensor_status(self):
        if 'signin' in self.driver.current_url:
            self.signin()
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        table = soup.find('div', id='orbSensorsList') \
                    .find('table') \
                    .find('tbody') \
                    .find_all('tr', recursive=False)

        sensor_dict = {}
        if len(table) == 4:
            for row in table:
                data = row.find_all('td')[-2:]
                door = data[0].get_text()
                door = door.replace(u'\xa0', u' ')
                door = str(door.strip())
                status = data[1].get_text()
                status = status.replace(u'\xa0', u' ')
                sensor_dict[door] = str(status.strip())

        result = ''
        header = ''
        for item in sensor_dict:
            if sensor_dict[item] not in ['Closed', 'Okay']:
                print len(sensor_dict[item]), sensor_dict[item]
                # print len(sensor_dict[item].trim()), sensor_dict[item].trim()
                header += 'Please check ' + item + '\n'
            result += item + ',\t' + sensor_dict[item]+ '\n'
        if header == '':
            header = 'All sensors are okay!\n\n'
        return header + result

    def __del__(self):
        """Destructor"""
        self.driver.quit()
