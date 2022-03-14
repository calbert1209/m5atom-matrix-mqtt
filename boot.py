# This file is executed on every boot (including wake-boot from deepsleep)
# import esp
# esp.osdebug(None)
# import webrepl
# webrepl.start()
import network
from machine import Pin
from neopixel import NeoPixel
from time import sleep_ms
from secrets import AP_SSID, AP_PASS

np = NeoPixel(Pin(27, Pin.OUT), 25)

station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(AP_SSID, AP_PASS)

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
