import time
from umqttsimple import MQTTClient
import ubinascii
import machine
import micropython
import network
import esp
from machine import Pin, I2C
import ssd1306
import dht
from machine import Pin
from machine import SoftI2C
from time import sleep

#honestly not sure what this is
esp.osdebug(None)
import gc
gc.collect()

#assign i2c pin for ESP8266
i2c = SoftI2C(scl=Pin(5), sda=Pin(4))
#assign i2c pin for ESP32
#i2c = SoftI2C(scl=Pin(22), sda=Pin(21))

#assign I2C pin for sensor 
#sensor =  dht.DHT11(Pin(14))
sensor = dht.DHT22(Pin(14))

#Setup SSD1306 screen
oled_width = 128
oled_height = 32
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

#setup wifi and MQTT broker
ssid = 'BHNTG1682G7F91'
password = '08a44639'
mqtt_server = '192.168.0.50'
#port = 1883

#assign unique client ID
client_id = ubinascii.hexlify(machine.unique_id())

#create MQTT topics
topic_pub_temp = b'esp/%s/dht/temperature' % client_id 
topic_pub_hum = b'esp/%s/dht/humidity' % client_id
topic_sub_location = b'esp/%s/dht/location' % client_id
#location = topic_sub_location

#wifi connection
station = network.WLAN(network.STA_IF)

station.active(True)
sleep(3)
station.connect(ssid, password)

while station.isconnected() == False:
  pass

print('Connection successful')
oled.text('WiFi Connected',0,0)
oled.show()


#MQTT Connection function
def connect_mqtt():
  global client_id, mqtt_server
  client = MQTTClient(client_id, mqtt_server)
  #client = MQTTClient(client_id, mqtt_server, user=your_username, password=your_password)
  client.connect()
  print('Connected to %s MQTT broker' % (mqtt_server))
  oled.fill(0)
  oled.text('%s Connected' % (mqtt_server),0,0)
  oled.text('Connected' ,0,10)
  oled.show()
  return client

#restarts controller if unable to connect to MQTT broker
def restart_and_reconnect():
  print('Failed to connect to MQTT broker. Reconnecting...')
  time.sleep(10)
  machine.reset()
 
#sensor read function
def read_sensor():
  try:
    sensor.measure()
    temp = sensor.temperature()
    # Uncomment to convert to fahrenheit
    # temp = tempC * (9/5) + 32.0
    hum = sensor.humidity()
    return temp, hum
    
  except OSError as e:
    return('Failed to read sensor.')
 
try:
    client = connect_mqtt()
except OSError as e:
    restart_and_reconnect()

#create variables for message timing
last_message = 0
message_interval = 1

#sensor read loop
while True:
    
  try:
    if (time.time() - last_message) > message_interval:
      temp, hum = read_sensor()
      print('Temp = %s F' % (temp*1.8+32))
      print('Humidity = %s' % hum)      
      #
      oled.fill(0)
      #oled.text('Location %s' % location ,0,00)
      oled.text('Temp %s F' % (temp*1.8+31),0,10)
      oled.text('Hum %s %%' % hum,0,20)
      oled.show()
      client.publish(topic_pub_temp, '%s' % ((temp*1.8)+32))
      client.publish(topic_pub_hum, '%s' % hum)      
      last_message = time.time()
  except OSError as e:
    restart_and_reconnect()


