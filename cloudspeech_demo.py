#!/usr/bin/env python3
# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""A demo of the Google CloudSpeech recognizer."""
# NOTE: Add cloud_speech.json in home folder from google cloud console.
import os
import sys
import json
import re
import requests


import aiy.audio
import aiy.cloudspeech
import aiy.voicehat

def get_pi_url():
    with open('/home/pi/piurl.txt') as f:
        data = f.read().strip()
    return data

PI_URL = get_pi_url()
print(PI_URL)

def send_voice_command(message_text):
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
            "audio_out": False
        }
    })

    r = requests.post(PI_URL+'/voice', params=params, headers=headers, data=data)

    if r.status_code != 200:
        print(r.status_code)
        print(r.text)

def main():
    recognizer = aiy.cloudspeech.get_recognizer()
    recognizer.expect_phrase('turn off the light')
    recognizer.expect_phrase('turn on the light')
    recognizer.expect_phrase('blink')

    button = aiy.voicehat.get_button()
    led = aiy.voicehat.get_led()
    aiy.audio.get_recorder().start()

    while True:
        print('Press the button and speak')
        button.wait_for_press()
        print('Listening...')
        text = recognizer.recognize()
        if not text:
            print('Sorry, I did not hear you.')
        else:
            text = text.strip()
            print('You said "', text, '"')
            send_voice_command(text)

if __name__ == '__main__':
    main()

