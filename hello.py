import mraa, time
leds = []
for i in range(2,10):led = mraa.Gpio(i)
	led.dir(mraa.DIR_OUT)
	if i%0:
		leds.instert(0,led)
	else:
		leds.insert(len(leds),led)


while True:
	for led in leds:
		led.write(0)
		time.sleep(0.2)
		led.write(1)
		time.sleep(0.2)
