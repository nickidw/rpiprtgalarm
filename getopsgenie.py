import datetime
import http.client
import xml.etree.ElementTree as ET
import RPi.GPIO as GPIO
import time
import sys
import ssl
import requests
import config

authorization = 'GenieKey ' + config.geniekey
relay_gpio=12
noalarmsleep=60
alarmtriggersleep=30
rechecksleep=30

def makeanoise(pin,seconds):
	 try:
	 	GPIO.setmode(GPIO.BOARD)
	 	GPIO.setup(pin, GPIO.OUT)

	 	p = GPIO.PWM(pin, 5)  # channel=12 frequency=50Hz
	 	p.start(50)
	 	time.sleep(seconds)
	 	p.stop()
	 finally:
	 	GPIO.cleanup()

def checkalarms():
	try:
		#Get younger than time from config
		timeto = datetime.datetime.now() - datetime.timedelta(minutes=config.alertolderthan)
		#Get older than time from config
		timefrom = datetime.datetime.now() - datetime.timedelta(minutes=config.alertyoungerthan)
		#convert to unix timestamp
		unixtimeto = int(round(time.mktime(timeto.timetuple()) * 1000))
		unixtimefrom = int(round(time.mktime(timefrom.timetuple()) * 1000))
		
        #Check all open and unacknowledged alerts older than 10 minutes
		url = "https://api.opsgenie.com/v2/alerts/count?query=status%3A%20open%20and%20acknowledged%20%3A%20false%20and%20createdAt%20%3C%20{}%20and%20createdAt%20%3E%20{}".format(unixtimeto, unixtimefrom)
		
		response = requests.get(url, headers = {'Authorization': authorization})

		if (response.status_code != 200):
			print("Got response {} from server".format(response.status))
			return -3
		data=response.json()

        #Check the count returned
		count = data['data']['count']

		if (count != 0):
			return 1

		return 0	
	except ConnectionError:
		print("Error: {}".format(sys.exc_info()[0]))
		return -1
	except Exception:
		print("Error: {}".format(sys.exc_info()[0]))
		return -2

makeanoise(relay_gpio, 0.2)

while 1<2:
	alarmsactive = checkalarms()

	if (alarmsactive == 1):
		makeanoise(relay_gpio, 0.2)
		print("active alarms, checking in {}s".format(alarmtriggersleep))
		time.sleep(alarmtriggersleep)
		alarmsactive = checkalarms()
		duration = 1	
		while (alarmsactive == 1):
			print("active alarms, making a noise!")
			makeanoise(relay_gpio,duration)
			print("rechecking in {}s".format(rechecksleep))
			time.sleep(rechecksleep)
			alarmsactive = checkalarms()
			duration = duration + 2
	elif (alarmsactive == -1):
		print("Connection error")
		makeanoise(relay_gpio, 0.1)
	elif (alarmsactive == -2):
		print("Other error")
		makeanoise(relay_gpio, 0.1)
	elif (alarmsactive == -3):
		print("Response code error")
		makeanoise(relay_gpio, 0.1)
	else:
		print("No alarms, going to sleep for {}s".format(noalarmsleep))

	time.sleep(noalarmsleep)
