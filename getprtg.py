import http.client
import xml.etree.ElementTree as ET
import RPi.GPIO as GPIO
import time
import sys
import ssl

username=""
passwordhash=""

server=""
urlpath="/api/getstatus.xml?id=0&username={}&passhash={}".format(username, passwordhash)
relay_gpio=12
noalarmsleep=60
alarmtriggersleep=300
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
		conn = http.client.HTTPSConnection(server, timeout=10,
		context = ssl._create_unverified_context())
		conn.request("GET", urlpath)
		response = conn.getresponse()

		if (response.status != 200):
			print("Got response {} from server".format(response.status))
			return -3
		data=response.read()

		root = ET.fromstring(data)
		for element in root.findall('Alarms'):
			alarms = element
		conn.close()

		if (element.text != None):
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
			duration = duration * 2
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
