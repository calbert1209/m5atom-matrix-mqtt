# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()
import json
import network
from machine import Pin
from neopixel import NeoPixel
from time import sleep_ms

np = NeoPixel(Pin(27, Pin.OUT), 25)

ssid = ''
password = ''
with open('config.json', 'r') as f:
    config = json.load(f)
    ssid = config['ssid']
    password = config['password']


station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(ssid, password)

while not station.isconnected():
    np[0] = (50, 30, 0)
    np.write()
    sleep_ms(200)
    np[0] = (0, 0, 0)
    np.write()
    sleep_ms(200)

np[0] = (0, 50, 0)
np.write()
sleep_ms(1000)
np[0] = (0, 0, 0)
np.write()
