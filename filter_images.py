import io
import os
import json
import random
import sys
import time
import datetime

import cv2
import numpy as np
# from skimage.measure import compare_ssim as ssim
from clarifai.rest import ClarifaiApp
from clarifai.rest import Image as ClImage

from gdrive_handler import GDriveHandler
from utils import send_alert


app = ClarifaiApp(api_key='b4378218c77546dfae3e7e6d0790db46')
model = app.models.get('general-v1.3')
person_tags = set(['person', 'adult', 'man', 'woman', 'people'])
noperson_tags = set(['no person', 'light', 'spotlight', 'room', 'museum'])

gdrive = GDriveHandler()
folder_id = gdrive.get_today_folder()

exclusions_path = '/home/pi/projects/pi-bot/exclusions/'
img_path = '/home/pi/projects/pi-bot/images/'
#img_path = './images/'

last_notify = 0
notify_thresh = 10*60
chunk_size = 20

def formatter(x):
    x = x.replace('img_', '').replace('.jpg', '')
    #items = map(int, x.split('-'))
    items = [int(y) for y in x.split('-')]
    key = items[0]*3600 + items[1]*60 + items[2]
    return key

def mse(gray_img1, gray_img2, multichannel=False):
    assert gray_img1.shape == gray_img2.shape
    err = np.sum((gray_img1.astype("float") - gray_img2.astype("float")) ** 2)
    err /= float(gray_img1.shape[0] * gray_img1.shape[1])

    return err

def get_gray(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21,21), 0)
    return gray

def check_similar(gray_img1, gray_img2):
    dist = mse(gray_img1, gray_img2, multichannel=False)
    return dist < 1000

def get_exclusions():
    gray_refs = {'night': [], 'day': []}
    files = os.listdir(exclusions_path)
    for filename in files:
        image = cv2.imread(exclusions_path + filename)
        gray = get_gray(image)

        if filename.startswith('day'):
            gray_refs['day'].append(gray)
        elif filename.startswith('night'):
            gray_refs['night'].append(gray)
    return gray_refs

def day_or_night(gray_image, day_ref, night_ref):
    day_dist = mse(gray_image, day_ref, multichannel=False)
    night_dist = mse(gray_image, night_ref, multichannel=False)
    if day_dist > night_dist:
        return 'night'
    else:
        return 'day'

def use_clarifai(model, filename):
    image = ClImage(file_obj=open(filename, 'rb'))
    response = model.predict([image])
    print 'Using clarifai...'
    is_person = False
    if 'outputs' in response:
        concepts = response['outputs'][0]['data']['concepts'][:5]
        for item in concepts:
            print item['name'], item['value']
            if item['name'] in person_tags:
                is_person = True
                break
            if item['name'] in noperson_tags:
                is_person = False
                break
    else:
        print('No response from ClarifaiApp.')

    return is_person


def filter_exclusions(gray_refs, images, false_positives):

    if len(images) <= 0:
        return [], []

    print 'Filtering exclusions images...'
    image = cv2.imread(img_path + images[0]['title'])
    gray_img = get_gray(image)

    status = day_or_night(gray_img,
                          gray_refs['day'][0],
                          gray_refs['night'][0])
    print(status)
    exclusions = gray_refs[status]
    threshold = 1000
    last_ref = None
    candidates = []

    for img in images:
        image = cv2.imread(img_path + img['title'])
        gray_img = get_gray(image)

        skip = False
        if last_ref:
            dist = mse(gray_img, exclusions[last_ref], multichannel=False)
            if dist < threshold:
                print('Last Ref')
                skip = True

        if not skip:
            for i, gray_ref in enumerate(exclusions):
                if i == last_ref:
                    continue
                dist = mse(gray_img, gray_ref, multichannel=False)
                if dist < threshold:
                    skip = True
                    last_ref = i
                    print(last_ref, dist)
                    break

        if skip:
            false_positives.append(img['id'])
        else:
            candidates.append(img)

    print '#candidates = {0} #false positives = {1}'.format(
        len(candidates), len(false_positives))
    return candidates, false_positives


def filter_images(files, false_positives):
    global last_notify, notify_thresh

    if len(files) <= 0:
        return false_positives

    print 'Filtering similar adjacent images...'
    files = sorted(files, key=lambda x: formatter(x['title']))

    prev = None
    is_person = False
    for file1 in files:
        image = cv2.imread(img_path + file1['title'])
        gray = get_gray(image)

        is_similar = False
        if prev is not None:
            is_similar = check_similar(prev, gray)
        if is_similar:
            if not is_person:
                prev = gray
                false_positives.append(file1['id'])
        else:
            is_person = use_clarifai(model, img_path + file1['title'])
            if is_person:
                if (time.time() - last_notify) > notify_thresh:
                    send_alert('Alert! Person detected near front door.')
                    last_notify = time.time()
            else:
                prev = gray
                false_positives.append(file1['id'])

    print '#false positives = {0}'.format(len(false_positives))
    return false_positives


def filter_dups(seen, folder_id):
    if not folder_id:
        return [], set()
    files = gdrive.get_files_in_folder(folder_id)

    dedup = [f for f in files if f['title'] not in seen]
    new_titles = [ f['title'] for f in dedup]
    seen |= set(new_titles)
    return dedup, seen

def clear_directory(img_path):
    for f in os.listdir(img_path):
        os.remove(img_path+f)


seen = set()
false_positives = []
deduped = []
gray_refs = get_exclusions()
while True:
    try:
        if not folder_id:
            folder_id = gdrive.get_today_folder()
        deduped, seen = filter_dups(seen, folder_id)

        if not deduped:
            time.sleep(30)
        else:
            for i in range(0, len(deduped), chunk_size):
                candidates = deduped[i:i+chunk_size]

                # Download local copy
                gdrive.download_files(candidates, img_path)

                # Checking exclusions
                candidates, false_positives = filter_exclusions(gray_refs, candidates, false_positives)
                # Checking similarity of adjacent images
                false_positives = filter_images(candidates, false_positives)

                if false_positives:
                    print 'Deleting false positives...'
                    print '#false positives = {0}'.format(len(false_positives))
                    # Delete false positives
                    gdrive.delete_files(false_positives)

                # Clear local files
                print '\n'
                print str(datetime.datetime.now())
                sys.stdout.flush()
                clear_directory(img_path)
                false_positives = []
    except Exception as e:
        print e

