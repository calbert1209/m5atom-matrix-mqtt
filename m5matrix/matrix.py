from machine import Pin
from neopixel import NeoPixel
from time import sleep_ms


class Matrix:
    def __init__(self):
        self.np = NeoPixel(Pin(27, Pin.OUT), 25)
        self.color = (0, 170, 130)

    def write(self):
        self.np.write()

    def fill(self, r, g, b):
        for i in range(25):
            self.np[i] = (r, g, b)
        self.write()

    def clear(self):
        self.fill(0, 0, 0)

    def blink(self, i, on=100, off=100):
        self.np[i] = self.color
        self.write()
        sleep_ms(on)
        self.clear()
        sleep_ms(off)
