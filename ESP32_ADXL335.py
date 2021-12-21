#ADXL335 accelerometer to ESP32

from machine import ADC, Pin
from time import sleep
#ESP32 default resolution in 12 bit, 0-4095

#create objects for each axis
xaxis= ADC(Pin(39))
yaxis= ADC(Pin(35))
zaxis= ADC(Pin(34))

# set to 3.3v full range
xaxis.atten(ADC.ATTN_11DB)
yaxis.atten(ADC.ATTN_11DB)
zaxis.atten(ADC.ATTN_11DB)

#loop to read and print values to terminal
while True:
    xaxis_value=xaxis.read()*3.3/4095
    yaxis_value=yaxis.read()*3.3/4095
    zaxis_value=zaxis.read()*3.3/4095
    #print("x value", xaxis_value)
    #print("y value", yaxis_value)
    #print("z value", zaxis_value)
    print("Raw XYZ: {0}, {1}, {2}".format(xaxis_value,yaxis_value,zaxis_value))
    sleep(0.25)