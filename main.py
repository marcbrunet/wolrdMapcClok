import time

import requests
import json
import datetime
import pytz

from PIL import Image


def getSolarTimes(lat, lng, date="today"):
    """
    lat (float): Latitude in decimal degrees. Required.
    lng (float): Longitude in decimal degrees. Required.
    date (string): Date in YYYY-MM-DD format. Also accepts other date formats and even relative date formats. If not
    present, date defaults to current date. Optional.
    callback (string): Callback function name for JSONP response. Optional.
    formatted (integer): 0 or 1 (1 is default). Time values in response will be expressed following ISO 8601 and
    day_length will be expressed in seconds. Optional.
    :return: list of sunrise(datatime), sunset(datatime), day_length(timedelta)
    """
    print('get')
    url = 'https://api.sunrise-sunset.org/json?lat=' + str(lat) + '&lng=' + str(lng) + '&date=' + str(
        date) + '&formatted=0'
    r = requests.get(url)
    if r.status_code == 200:
        d = json.loads(r.content.decode())
        if d['status'] == "OK":
            datetimeFormat = "%Y-%m-%dT%H:%M:%S%z"
            sunrise = datetime.datetime.strptime(d['results']['sunrise'], datetimeFormat)
            sunset = datetime.datetime.strptime(d['results']['sunset'], datetimeFormat)
            day_length = datetime.timedelta(seconds=d['results']['day_length'])
            return [sunrise, sunset, day_length]
    return 'ERROR'

def time2rgb(time):
    """
    chage time obget to rgb color
    Warning to morning not next day
    :param time:
    :return: tuple (RGB)
    """
    sunrise = time[0]
    sunset = time[1]
    day_length = int(time[2].seconds / 60)
    im = Image.open("test.bmp")
    pixels = [im.getpixel((x, int(im.height / 2))) for x in range(im.width)]
    im.close()
    now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    if sunrise < now < sunset:
        if len(pixels) > day_length:
            pixels = pixels[:int(day_length / 2)] + pixels[int(day_length / 2) - day_length:]
        delta = sunset - now
        return pixels[int(delta.seconds / 60)]
    else:
        return 0, 0, 0

def updateWorlTimeMap(worlMap, timeMap={}):
    for led, cord in worlMap.items():
        if led in timeMap.keys():
            if timeMap[led][1] < datetime.datetime.utcnow().replace(tzinfo=pytz.utc):
                newtimes = getSolarTimes(cord[0], cord[1])
                if timeMap[led] == newtimes:
                    newtimes = getSolarTimes(cord[0], cord[1], "tomorrow")
                timeMap[led] = newtimes
        else:
            timeMap[led] = getSolarTimes(cord[0], cord[1])
    return timeMap

def getLedMap(timeMap):
    ledMap = {}
    for k, v in timeMap.items():
        ledMap[k] = time2rgb(v)
    return ledMap

def updateMap(worlMap, timeMap):
    timeMap = updateWorlTimeMap(worlMap, timeMap)
    ledMap = getLedMap(timeMap)
    print(ledMap)


worlMap = {
    '1': [36.721898, 150.969401],
    '2': [33.000000, 65.000000],
    '3': [42.500000, 1.600000],
    '4': [19.397555, -155.879595]
}
timeMap = {}
lastTime = datetime.datetime.now()
while True:
    if datetime.datetime.now()-lastTime > datetime.timedelta(seconds=30):
        lastTime = datetime.datetime.now()
        updateMap(worlMap, timeMap)
    time.sleep(1)
