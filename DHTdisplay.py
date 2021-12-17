#library setup
import ssd1306
import dht
import micropython
#esp.osdebug(None)
import gc
gc.collect()
import machine
from machine import Pin
from machine import SoftI2C
#mqtt example code had us load entire time library. 
from time import sleep
import time
from umqttsimple import MQTTClient
import ubinascii
import network
import esp

#setup wifi
ssid = 'TSE GUEST'
password = '7275737676'
mqtt_server = 'dameant.com'

#assign unique client ID
client_id = ubinascii.hexlify(machine.unique_id())

#create mqtt topics for temp and humidity
topic_pub_temp = b'esp/dht/temperature'
topic_pub_hum = b'esp/dht/humidity'

#create variables for message timing
last_message = 0
message_interval = 5

#assign sensor pin
sensor =  dht.DHT11(Pin(14))
#sensor = dht.DHT22(Pin(14))

#assign i2c pin for ESP8266
i2c = SoftI2C(scl=Pin(5), sda=Pin(4))

#assign i2c pin for ESP32
#i2c = SoftI2C(scl=Pin(22), sda=Pin(21))

#screen specification
oled_width = 128
oled_height = 32
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

#connect to network
station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
  pass

print('Connection successful')
oled.text('WiFi good',0,0)
oled.show()
sleep(1)

#connect to mqtt broker
def connect_mqtt():
  global client_id, mqtt_server
  client = MQTTClient(client_id, mqtt_server)
  #client = MQTTClient(client_id, mqtt_server, user=your_username, password=your_password)
  client.connect()
  print('Connected to %s MQTT broker' % (mqtt_server))
  oled.fill(0)
  oled.text('MQTT good',0,0)
  oled.show()
  return client

#restart and reconnect if unable to connect to mqtt broker
def restart_and_reconnect():
  print('Failed to connect to MQTT broker. Reconnecting...')
  time.sleep(10)
  machine.reset()
  
try:
  client = connect_mqtt()
except OSError as e:
  restart_and_reconnect()

#sensor variables?? not sure why these are here
sensor.measure()
sensor.temperature()
sensor.humidity()

while True:
  try:
    sleep(2)
    oled.fill(0)
    sensor.measure()
    temp = sensor.temperature()
    hum = sensor.humidity()
    temp_f = temp * (9/5) + 32.0
    #create string from C temp for display
    oledtempC=str(temp)
    oledhum=str(hum)
    oledtempF=str(temp_f)
    print('Temperature: %3.1f C' %temp)
    print('Temperature: %3.1f F' %temp_f)
    print('Humidity: %3.1f %%' %hum)
    #display temp string
    oled.text('TEMP ' + oledtempF + 'F',0,0)
    oled.text('TEMP ' + oledtempC +'C',0,10)
    oled.text('RH ' + oledhum + '%',0,20)
    oled.show()
    #start mqtt portion of output
    if (time.time() - last_message) > message_interval:
        client.publish(topic_pub_temp, oledtempF)
        client.publish(topic_pub_hum, oledhum)
        last_message = time.time()
  except OSError as e:
    print('Failed to read sensor.')
    #restart_and_reconnect()