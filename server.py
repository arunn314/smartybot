#!/usr/bin/env python
import os
import sys
import time

import json
import requests
import logging
from flask import Flask, render_template, Response, request

from utils import send_alert, speak, send_image, send_message
from camera import Camera
from processor import Processor
from queryparser import Parser
from celery import Celery

from config import PI_URL, MESSENGER_ID, LOG_PATH, ACCESS_TOKEN

app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])

p = Processor()
parser = Parser()


@celery.task
def process_command(sender, message):
    """Background task to send an email with Flask-Mail."""

    intent = parser.get_intent(message.lower())
    args = parser.get_entities(message, intent)
    print intent
    print args
    if intent == 'time':
        send_message(sender, time.strftime('%I:%M %p'))
    elif intent == 'expense' and 'interval' in args:
        result = p.process(intent, args)
        if args['exp_type'] == 'all':
            send_image(sender, 'plot.png', result, True)
        else:
            send_message(sender, result, False)
    elif intent == 'echo' and 'message' in args:
        speak(args['message'])
    elif intent == 'snap' or intent == 'stream':
        url_link = get_link(intent)
        send_message(sender, url_link, False)
    elif intent == 'email' and 'action' in args:
        result = p.process(intent, args)
        print result
        send_message(sender, result)
    elif intent == 'security' and 'action' in args:
        result = p.process(intent, args)
        send_message(sender, result)
    elif intent == 'stock' and 'company' in args:
        result = p.process(intent, args)
        send_message(sender, result)
    elif intent == 'weather' and 'city' in args:
        result = p.process(intent, args)
        send_message(sender, result)
    elif intent == 'switch' and 'action' in args:
        result = p.process(intent, args)
        send_message(sender, result)
    elif intent == 'route' and 'destination' in args:
        result = p.process(intent, args)
        send_message(sender, result, not args['directions'])
    elif intent == 'wiki' and 'query' in args:
        result = p.process(intent, args)
        send_message(sender, result)
    else:
        result = 'Sorry, I didnt get that.'
        send_message(sender, result)


@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        # if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
        #     return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200

@app.route('/', methods=['POST'])
def handle_messages():
    payload = request.get_data()
    for sender, message in messaging_events(payload):
        print "Incoming from %s: %s" % (sender, message)
        process_command.delay(sender, message)

    return "ok"

@app.route('/alert', methods=['POST'])
def echo_messages():
    payload = request.get_data()
    payload = json.loads(payload)
    msg = payload['message']['text']
    audio_out = payload['message']['audio_out']
    if msg:
        send_message(MESSENGER_ID['user1'], msg, audio_out)
    else:
        print 'Alert msg'
        print msg
    return "ok"

def messaging_events(payload):
  """Generate tuples of (sender_id, message_text) from the
  provided payload.
  """
  data = json.loads(payload)
  messaging_events = data["entry"][0]["messaging"]
  for event in messaging_events:
    if "message" in event and "text" in event["message"] and \
            event["sender"]["id"] != MESSENGER_ID['smarty']:
        yield event["sender"]["id"], event["message"]["text"].encode('unicode_escape')
    else:
        print event


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


def get_link(data):
    if data == 'snap':
        return PI_URL+'/snap'
    elif data == 'stream':
        return PI_URL+'/video_feed'

def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    try: 
        return Response(gen(Camera()),
                        mimetype='multipart/x-mixed-replace; boundary=frame')
    except Exception as e:
        print e


@app.route('/snap')
def snap():
    """Video streaming route. Put this in the src attribute of an img tag."""
    try: 
        return Response(take_snap(),
                        mimetype='multipart/x-mixed-replace; boundary=frame')
    except Exception as e:
        print e

def take_snap():
    print 'taking snap'
    out = 'b1.jpg'
    os.system('raspistill -vf -hf -w 900 -h 600 -t 100 -o '+out)
    frame = open(out).read()
    yield (b'--frame\r\n'
           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


if __name__ == '__main__':
    logger = logging.getLogger('werkzeug')
    handler = logging.FileHandler(LOG_PATH+'access.log')
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    app.logger.addHandler(handler)
    app.run(debug=True, threaded=True)
