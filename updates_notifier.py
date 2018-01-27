import os
import json
import datetime
import sys
from collections import defaultdict

from gmail_handler import GmailHandler
from gmaps_handler import GmapsHandler
from gdrive_handler import GDriveHandler
from weather_handler import WeatherHandler
from plug_handler import PlugHandler
from utils import send_alert

def route_notifier(destination):
    obj = GmapsHandler()
    if destination == 'office':
        msg = obj.get_route(destination='office')
    elif destination == 'home':
        msg = obj.get_route(source='office', destination='home')

    send_alert(msg, True)

def email_notifier():
    obj = GmailHandler()
    msg = obj.get_unread(recent=True)
    send_alert(msg, True)

def weather_notifier(cityname):
    obj = WeatherHandler()
    msg = obj.get_temperature(city=cityname)
    send_alert(msg, True)

def plug_handler(state, appliance):
    obj = PlugHandler()
    if state == 'on':
        msg = obj.switch_on()
    elif state == 'off':
        msg = obj.switch_off()
    send_alert(appliance + ' ' + msg, True)

def clean_drive():
    obj = GDriveHandler()
    obj.delete_old_files()

if __name__ == '__main__':
    action =  sys.argv[1]
    if action == 'office':
        route_notifier(action)
    if action == 'home':
        route_notifier(action)
    if action == 'email':
        email_notifier()
    if action == 'weather':
        weather_notifier('Milpitas')
    if action == 'switch_on':
        plug_handler('on', 'Light')
    if action == 'switch_off':
        plug_handler('off', 'Light')
    if action == 'clean_gdrive':
        clean_drive()

