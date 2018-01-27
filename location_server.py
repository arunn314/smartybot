import time
from datetime import datetime
import pickle
from collections import defaultdict

from bs4 import BeautifulSoup
from selenium import webdriver
from geopy.geocoders import Nominatim
from geopy.distance import vincenty

from config import LIFE360_CONFIG, LIFE360_PARAMS

from adt_handler import ADTHandler
from life360_handler import Life360Handler
from utils import send_alert

import time
from life360_handler import Life360Handler
from geopy.geocoders import Nominatim
from geopy.distance import vincenty

HOME = 'Home'
STATUS_AWAY = 'away'
STATUS_REACHED = 'reached'

def main():

    landmarks = LIFE360_PARAMS['landmarks']
    obj = Life360Handler()
    adt_handler = ADTHandler()

    users = ['user1', 'user2']
    state = defaultdict(lambda: defaultdict(str))
    state_change = False

    old_d = defaultdict(lambda: defaultdict(str))
    prev_d = defaultdict(lambda: defaultdict(str))

    try:
        x = obj.get_location()
        for user in users:
            p1 = (x[user]['latitude'], x[user]['longitude'])
            for place, coords in landmarks.iteritems():
                d1 = vincenty(p1, coords).miles
                prev_d[place][user] = d1
                old_d[place][user] = d1
                if d1 < 0.15:
                    state[place][user] = STATUS_REACHED
                if d1 > 0.15:
                    state[place][user] = STATUS_AWAY
        print 'Init'

        while True:
            adt_status = 'disarmed'

            x = obj.get_location()
            for user in users:
                p1 = (x[user]['latitude'], x[user]['longitude'])
                for place, coords in landmarks.iteritems():
                    d1 = vincenty(p1, coords).miles
                    print user, str(d1)
                    if d1 < 1 and state[place][user] != STATUS_REACHED and (0.5 < old_d[place][user] - d1):
                        state[place][user] = STATUS_REACHED
                        status_change(place, user, STATUS_REACHED)
                        if place == HOME:
                            state_change = True
                    elif d1 > 0.15 and state[place][user] != STATUS_AWAY and \
                            d1 > old_d[place][user] and old_d[place][user] < 0.1:
                        state[place][user] = STATUS_AWAY
                        status_change(place, user, STATUS_AWAY)
                        if place == HOME:
                            state_change = True

                    if d1 != prev_d[place][user]:
                        old_d[place][user] = prev_d[place][user]
                    prev_d[place][user] = d1

                if state_change:
                    adt_status = adt_handler.get_status()
                    # both left
                    if state[HOME]['user1'] == STATUS_AWAY and state[HOME]['user2'] == STATUS_AWAY:
                        if adt_status == 'Disarmed':
                            # arm_away()
                            send_alert('Both of you guys are out. So I am setting to arm away.')
                            response = adt_handler.arm_away()
                            send_alert(response)
                print state_change
                state_change = False

            time.sleep(60)
            print state
    except Exception as e:
        del obj
        del adt_handler
        return

def status_change(place, user, status):
    user = user.title()
    msg = ''
    if status == STATUS_REACHED:
        msg = user + ' reached ' + place + '.'
    if status == STATUS_AWAY:
        msg = user + ' left ' + place + '.'
    send_alert(msg, False)

if __name__ == '__main__':
    while True:
        main()

