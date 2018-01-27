import os
import json
import re
import requests
import sys
from config import PI_URL, num2words, ACCESS_TOKEN

def send_alert(message_text, audio_out=True):

    params = {
        "access_token": '1234'
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "object": 'local',
        "message": {
            "text": message_text,
            "audio_out": audio_out
        }
    })
    r = requests.post(PI_URL+'/alert', params=params, headers=headers, data=data)

    if r.status_code != 200:
        print r.status_code
        print r.text

def send_image(recipient_id, img_name, message_text='', audio_out=True):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": ACCESS_TOKEN
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "attachment":{
            "type":"image",
            "payload":{
                "url": PI_URL + "/static/"+img_name
            }}
        },
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if audio_out:
        speak(message_text)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

def send_message(recipient_id, message_text, audio_out=True):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": ACCESS_TOKEN
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text[:250]
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if audio_out:
        speak(message_text[:250])
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()

def speak_1(msg):
    cmd = 'espeak -ven-us+f4 -a 300 -s 120 "{0}"'.format(msg)
    os.system(cmd)

def n2w(n1):
    x = n1%100
    y = n1/100
    result = []
    if y:
        result.append(num2words[y])
    if y or (x-x%10):
        result.append(num2words[x-x%10])
    if (y or (x-x%10)) and x%10:
        result.append(num2words[x%10])

    if not result:
        result.append(num2words[x%10])
    return ' '.join(result)

def speak(msg):
    msg = msg.replace('"', '')
    msg = re.sub(r'mins', 'minutes', msg, flags=re.IGNORECASE)
    if 'fastest route' in msg:
        msg = re.sub(r'CA', 'C.A.', msg)
        msg = re.sub(r'US', 'U.S.', msg)
        msg = re.sub(r' W', ' west', msg)
        msg = re.sub(r' E', ' east', msg)
        msg = re.sub(r' S', ' south', msg)
        msg = re.sub(r' N', ' north', msg)
        nums = [int(s) for s in msg.split() if s.isdigit()]
        nums = re.findall(r'\d+', msg)
        for num in nums:
            msg = re.sub(num, n2w(int(num)), msg)
    if 'Temperature' in msg:
        msg = re.sub(r'(.*) (\d+) F.', r'\1 \2 degree Fahrenheit.', msg)
    cmd = 'flite -voice kal -t "{0}"'.format(msg)
    os.system(cmd)
