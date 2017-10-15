#!/usr/bin/python
import mraa, time, socket, sys
from datetime import datetime as dt
import signal

leds = []
for i in range(2,10):
    led = mraa.Gpio(i)
    led.dir(mraa.DIR_OUT)
		leds.append(led)
		led.write(1)


while True:
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(("8.8.8.8", 80))
		leds[0].write(0)
		leds[len(leds)-1].write(1)
	except:
		leds[0].write(1)
		leds[len(leds)-1].write(0)
	time.sleep(5)
