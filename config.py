GMAIL_CONFIG = {
    'username': 'xxx',
    'password': 'yyy'
}

ADT_CONFIG = {
    'username': 'xxx',
    'password': 'yyy',
    'url': 'https://portal.adtpulse.com/myhome/6.18.0-238/access/signin.jsp'
}

LIFE360_CONFIG = {
    'username': 'xxx',
    'phone': 'zzz',
    'password': 'yyy',
    'url': 'https://www.life360.com/circles/#/',
    'user_xpath': '//input[@name="username" and @type="email"]',
    'pwd_xpath': '//input[@name="password" and @type="password"]',
    'login_button_xpath': '//button[@type="submit" and @class="btn login"]'
}

LIFE360_PARAMS = {
    'device_id': {
        'device_id1': 'user1',
        'device_id2': 'user2'
    },
    'landmarks': {
        'Office': (47.418836975, -102.146152895),
        'Home': (87.4188634, -111.9011286),
        'Office2': (32.3874612,-124.0443219)
    }
}

STOCK_SYMBOLS = {
    'apple': 'AAPL',
    'google': 'GOOG',
    'facebook': 'FB',
    'snap': 'SNAP',
    'amazon': 'AMZN',
    'microsoft': 'MSFT'
}

PI_URL = ''

MESSENGER_ID = {
    'your name': 'xxx',
    'smarty': 'xxx'
}

OWM_API = 'xxx'

LOG_PATH = '/home/pi/logs/'

REDIS_KEY = 'plaid_txns'

ACCESS_TOKEN = 'xxx'

num2words = {1: 'One', 2: 'Two', 3: 'Three', 4: 'Four', 5: 'Five', \
             6: 'Six', 7: 'Seven', 8: 'Eight', 9: 'Nine', 10: 'Ten', \
            11: 'Eleven', 12: 'Twelve', 13: 'Thirteen', 14: 'Fourteen', \
            15: 'Fifteen', 16: 'Sixteen', 17: 'Seventeen', 18: 'Eighteen', \
            19: 'Nineteen', 20: 'Twenty', 30: 'Thirty', 40: 'Forty', \
            50: 'Fifty', 60: 'Sixty', 70: 'Seventy', 80: 'Eighty', \
            90: 'Ninety', 0: 'Zero'}


def get_pi_url_raw():
    import os
    import json
    os.system("curl  http://localhost:4040/api/tunnels > /home/pi/tunnels.json")

    with open('/home/pi/tunnels.json') as data_file:
        datajson = json.load(data_file)

    msg = ''
    for i in datajson['tunnels']:
        if 'public_url' in i:
            msg = i['public_url']
            break
    if msg.startswith('http'):
        msg = 'https:'+msg.split(':')[1]
    else:
        msg = ''
    return msg

def get_pi_url():
    with open('/home/pi/piurl.txt') as f:
        data = f.read().strip()
    return data

PI_URL = get_pi_url()
