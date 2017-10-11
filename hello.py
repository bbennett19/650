import mraa, time

def control_c_handler(signum, frame):
	print('saw control-c')
	print("Turning off all LEDS...")
	for led in leds:
		led.write(1)
	print("Exiting")
	sys.exit(0)

signal.signal(signal.SIGINT, control_c_handler)

leds = []
for i in range(2,10):
	led = mraa.Gpio(i)
	led.dir(mraa.DIR_OUT)
  if i%2 == 0:
    leds.insert(0,led)
  else:
    leds.insert(len(leds),led)


while True:
  for led in leds:
		led.write(0)
		time.sleep(0.2)
		led.write(1)
		time.sleep(0.2)
