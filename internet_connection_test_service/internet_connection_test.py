#!/usr/bin/python
import mraa, time, socket, sys
from datetime import datetime as dt
import signal

leds = []
def termination_handler(signum, frame):
    for led in leds:
        led.write(1)
    sys.exit(0)

# Since this is a service we want to know if it was terminated
signal.signal(signal.SIGTERM, termination_handler)

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
