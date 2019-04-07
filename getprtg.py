import http.client
import xml.etree.ElementTree as ET
import RPi.GPIO as GPIO
import time
import sys

server="18.223.216.13"
urlpath="/getstatus.xml"
relay_gpio=17
noalarmsleep=60
alarmtriggersleep=300
rechecksleep=30

def makeanoise(pin,count,beepon,beepoff):
	try:
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(pin, GPIO.OUT)
		for x in range(count):
			GPIO.output(pin, GPIO.HIGH)
			time.sleep(beepon)
			GPIO.output(pin, GPIO.LOW)
			time.sleep(beepoff)
	finally:
		GPIO.cleanup()

def checkalarms():
	try:
		conn = http.client.HTTPConnection(server)
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

while 1<2:
	alarmsactive = checkalarms()

	if (alarmsactive == 1):
		print("active alarms, checking in {}s".format(alarmtriggersleep))
		time.sleep(alarmtriggersleep)
		alarmsactive = checkalarms()
	
		while (alarmsactive == 1):
			print("active alarms, making a noise!")
			makeanoise(relay_gpio,10,0.1,0.1)
			print("rechecking in {}s".format(rechecksleep))
			time.sleep(rechecksleep)
			alarmsactive = checkalarms()
	elif (alarmsactive == -1):
		print("Connection error")
	elif (alarmsactive == -2):
		print("Other error")
	elif (alarmsactive == -3):
		print("Response code error")
	else:
		print("No alarms, going to sleep for {}s".format(noalarmsleep))

	time.sleep(noalarmsleep)
