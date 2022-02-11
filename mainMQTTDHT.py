# Complete project details at https://RandomNerdTutorials.com/micropython-mqtt-publish-dht11-dht22-esp32-esp8266/

import time
from umqttsimple import MQTTClient
import ubinascii
import machine
import micropython
import network
import esp
from machine import Pin
import dht
from time import sleep
esp.osdebug(None)
import gc
gc.collect()

ssid = 'BHNTG1682G7F91'
password = '08a44639'


mqtt_server = '192.168.0.50'


client_id = ubinascii.hexlify(machine.unique_id())

topic_pub_temp = 'esp/dht/temperature'
topic_pub_hum = 'esp/dht/humidity'

last_message = 0
message_interval = 5

station = network.WLAN(network.STA_IF)

station.active(True)
sleep(3)
station.connect(ssid, password)

while station.isconnected() == False:
  pass

print('Connection successful')

sensor = dht.DHT22(Pin(14))
#sensor = dht.DHT11(Pin(14))

def connect_mqtt():
  global client_id, mqtt_server
  client = MQTTClient(client_id, mqtt_server)
  #client = MQTTClient(client_id, mqtt_server, user=your_username, password=your_password)
  client.connect()
  print('Connected to %s MQTT broker' % (mqtt_server))
  return client

def restart_and_reconnect():
  print('Failed to connect to MQTT broker. Reconnecting...')
  time.sleep(10)
  machine.reset()

def read_sensor():
  try:
    sensor.measure()
    temp = sensor.temperature()
    # uncomment for Fahrenheit
    #temp = temp * (9/5) + 32.0
    hum = sensor.humidity()
    if (isinstance(temp, float) and isinstance(hum, float)) or (isinstance(temp, int) and isinstance(hum, int)):
      temp = (b'{0:3.1f},'.format(temp))
      hum =  (b'{0:3.1f},'.format(hum))
      
      return temp, hum
    else:
      return('Invalid sensor readings.')
  except OSError as e:
    return('Failed to read sensor.')

try:
  client = connect_mqtt()
except OSError as e:
  restart_and_reconnect()

while True:
  try:
    if (time.time() - last_message) > message_interval:
      temp, hum = read_sensor()
      print(temp)
      print(hum)
      client.publish(topic_pub_temp, temp)
      client.publish(topic_pub_hum, hum)
      last_message = time.time()
  except OSError as e:
    restart_and_reconnect()