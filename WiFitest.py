


import network
from time import sleep
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.scan()

sta_if.connect('BHNTG1682G7F91', '08a44639')  # replace the strings with your own wifi ssid and password
sleep(3)
print('network config:', sta_if.ifconfig())



#sta_if = network.WLAN(network.STA_IF)
#sta_if.active(True)
#ssid = 'BHNTG1682G7F91'
#password = '08a44639'
#sta_if.connect(ssid, password)
#print('network config:', sta_if.ifconfig())