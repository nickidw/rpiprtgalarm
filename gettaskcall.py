from datetime import datetime, timedelta, timezone
import http.client
import xml.etree.ElementTree as ET
import RPi.GPIO as GPIO
import time
import sys
import ssl
import requests
import config

authorization = 'token ' + config.api_key   # ← changed to TaskCall format

# TaskCall services to monitor (name: service_ref_id)
# To add a service later, add a line: "Name": "service_ref_id",
services = {
    "N-central":        "Nh2UngdOT1uzqgUKhy1l9A",
    "PLUS":             "0j-Zq-GNQ8u74FcA0kdaLg",
}

relay_gpio = 12
noalarmsleep = 60
alarmtriggersleep = 30
rechecksleep = 30

def makeanoise(pin, seconds):
    try:
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(pin, GPIO.OUT)
        p = GPIO.PWM(pin, 5)  # channel=12 frequency=5Hz
        p.start(50)
        time.sleep(seconds)
        p.stop()
    finally:
        GPIO.cleanup()

def checkalarms():
    now_utc = datetime.now(timezone.utc)
    # Get younger than time from config (closer to now)
    time_newer = now_utc - timedelta(minutes=config.alertyoungerthan)
    # Get older than time from config (farther back)
    time_older = now_utc - timedelta(minutes=config.alertolderthan)

    # Format as TaskCall expects: string "YYYY-MM-DD HH:MM:SS" (UTC, no timezone)
    start_timestamp   = time_newer.strftime("%Y-%m-%d %H:%M:%S")   # start = now - alertyoungerthan
    end_timestamp = time_older.strftime("%Y-%m-%d %H:%M:%S")   # end   = now - alertolderthan


    url = "https://incidents-api.taskcallapp.com/incidents/list"
    error_code = 0
    alarm_found = False

    for name, ref_id in services.items():
        try:
            payload = {
                "status": "OPEN",
                "service_ref_id": ref_id,
                "start_timestamp": start_timestamp,
                "end_timestamp": end_timestamp
            }

            response = requests.post(
                url,
                json=payload,
                headers={'Authorization': authorization, 'Content-Type': 'application/json'},
                timeout=30
            )

            if response.status_code != 200:
                print("{}: Got response {} from server".format(name, response.status_code))
                error_code = -3
                continue

            data = response.json()

            # TaskCall returns array of incidents → count how many
            count = len(data) if isinstance(data, list) else 0

            if count != 0:
                print("{}: {} open incident(s)".format(name, count))
                alarm_found = True
                break   # unacknowledged incident found → stop checking and beep now

        except requests.exceptions.ConnectionError:
            print("{}: Error: {}".format(name, sys.exc_info()[0]))
            error_code = -1
        except Exception:
            print("{}: Error: {}".format(name, sys.exc_info()[0]))
            error_code = -2

    if alarm_found:
        return 1
    return error_code

makeanoise(relay_gpio, 0.2)

while 1 < 2:
    alarmsactive = checkalarms()
    if alarmsactive == 1:
        makeanoise(relay_gpio, 0.2)
        print("active alarms, checking in {}s".format(alarmtriggersleep))
        time.sleep(alarmtriggersleep)
        alarmsactive = checkalarms()
        duration = 1
        while alarmsactive == 1:
            print("active alarms, making a noise!")
            makeanoise(relay_gpio, duration)
            print("rechecking in {}s".format(rechecksleep))
            time.sleep(rechecksleep)
            alarmsactive = checkalarms()
            duration = duration + 2
    elif alarmsactive == -1:
        print("Connection error")
        makeanoise(relay_gpio, 0.1)
        time.sleep(noalarmsleep)
    elif alarmsactive == -2:
        print("Other error")
        makeanoise(relay_gpio, 0.1)
        time.sleep(noalarmsleep)
    elif alarmsactive == -3:
        print("Response code error")
        makeanoise(relay_gpio, 0.1)
        time.sleep(noalarmsleep)
    else:
        print("No alarms, going to sleep for {}s".format(noalarmsleep))
        time.sleep(noalarmsleep)
