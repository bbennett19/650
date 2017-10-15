#!/usr/bin/python
import time, socket, sys
from datetime import datetime as dt
import paho.mqtt.client as paho
import signal

# Deal with control-c
def control_c_handler(signum, frame):
	#print('saw control-c')
	mqtt_client.disconnect()
	mqtt_client.loop_stop()  # waits until DISCONNECT message is sent out
	#print "Now I am done."
	sys.exit(0)

signal.signal(signal.SIGINT, control_c_handler)

# Get your IP address
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
ip_addr = str(s.getsockname()[0])
#print('IP address: {}'.format(ip_addr))
s.close()

def on_connect(client, userdata, flags, rc):
	1==1
	#print('connected')

def on_disconnect(client, userdata, rc):
	#print("Disconnected in a normal way")
	1==1
	#graceful so won't send will

def on_log(client, userdata, level, buf):
	#print("log: {}".format(buf)) # only semi-useful IMHO
	1==1

# Instantiate the MQTT client
mqtt_client = paho.Client()

# set up handlers
mqtt_client.on_connect = on_connect
mqtt_client.on_disconnect = on_disconnect

mqtt_topic = 'cis650/Ben/ip_addr'  # don't change this or you will screw it up for others
mqtt_client.will_set(mqtt_topic, '______________Will of Bens IP Address Publisher _________________\n\n', 0, False)
broker = 'sansa.cs.uoregon.edu'  # Boyana's server
mqtt_client.connect(broker, '1883')
mqtt_client.loop_start()  # just in case - starts a loop that listens for incoming data and keeps client alive

while True:
	timestamp = dt.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S.%f')
	mqtt_message = "[%s] %s " % (timestamp,ip_addr)  # don't change this or you will screw it up for others
	mqtt_client.publish(mqtt_topic, mqtt_message)  # by doing this publish, we should keep client alive
	#print("published ip addr")
	time.sleep(3)
