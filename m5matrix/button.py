import machine
from micropython import const
import time

PRESS = const(0x01)
RELEASE = const(0x02)
LONG_PRESS = const(0x04)
DOUBLE_PRESS = const(0x08)
MULTI_PRESS = const(0x10)
PRESS_WAIT = const(0x20)

state_list = [PRESS, RELEASE, LONG_PRESS, DOUBLE_PRESS]


class BtnChild:
    def __init__(self, pin, db_time=20):
        self.pin = machine.Pin(pin, mode=machine.Pin.IN, pull=machine.Pin.PULL_UP)
        self._event = 0
        self._eventLast = 0
        self._valueLast = 1
        self._pressTime = 0
        self._releaseTime = 0
        self._doubleTime = 220
        self._db_time = db_time
        self._hold_time = 1000.0
        self._cbState = PRESS | RELEASE
        self._eventTime = {PRESS: 0, RELEASE: 0, LONG_PRESS: 0, DOUBLE_PRESS: 0}
        self.cb = {PRESS: None, RELEASE: None, LONG_PRESS: None, DOUBLE_PRESS: None}

    def was_double_press(self, callback=None):
        self._cbState |= DOUBLE_PRESS
        if callback:
            self.cb[DOUBLE_PRESS] = callback
        elif self._event & DOUBLE_PRESS:
            self._event -= DOUBLE_PRESS
            return True
        else:
            return False

    def press_for(self, hold_time=1.0, callback=None):
        self._hold_time = hold_time * 1000
        self._cbState |= LONG_PRESS
        if callback:
            self.cb[LONG_PRESS] = callback
        elif self._event & LONG_PRESS:
            self._event -= LONG_PRESS
            return True
        else:
            return False

    def was_released(self, callback=None):
        if callback:
            self.cb[RELEASE] = callback
        elif self._event & RELEASE:
            self._event -= RELEASE
            return True
        else:
            return False

    def was_pressed(self, callback=None):
        if callback:
            self.cb[PRESS] = callback
        elif self._event & PRESS:
            self._event -= PRESS
            return True
        else:
            return False

    def is_pressed(self):
        return not self.pin.value()

    def is_released(self):
        return self.pin.value()

    def restart(self):
        self._cbState = PRESS | RELEASE
        self.cb = {PRESS: None, RELEASE: None, LONG_PRESS: None, DOUBLE_PRESS: None}
        self._eventTime = {PRESS: 0, RELEASE: 0, LONG_PRESS: 0, DOUBLE_PRESS: 0}
        self._event = 0
        self._pressTime = 0
        self._releaseTime = 0
        self._valueLast = 1

    def deinit(self):
        pass

    def update(self):
        value = self.pin.value()
        state = self._eventLast ^ self._event
        if state:
            for i in state_list:
                if state & i:
                    if self._event & i:
                        self._eventTime[i] = 40
                    else:
                        self._eventTime[i] = 0
            self._eventLast = self._event

        for i in state_list:
            if self._eventTime[i] > 1:
                self._eventTime[i] -= 1
            elif self._eventTime[i] == 1:
                self._eventTime[i] = 0
                self._event &= ~i

        if value ^ self._valueLast:
            time_now = time.ticks_ms()
            self._valueLast = value
            if not value:
                if time_now - self._pressTime > self._db_time:
                    if self._cbState & DOUBLE_PRESS and time_now - self._pressTime < self._doubleTime:
                        self._event |= DOUBLE_PRESS
                    self._event |= PRESS_WAIT
                self._pressTime = time_now
            else:
                if time_now - self._releaseTime > self._db_time:
                    if self._cbState & LONG_PRESS and time_now - self._pressTime > self._hold_time:
                        self._event |= LONG_PRESS
                    else:
                        self._event |= RELEASE
                self._releaseTime = time_now


class Btn:
    def __init__(self, multi_time=50):
        self.timer = machine.Timer(1)
        self.timer.init(period=10, mode=self.timer.PERIODIC, callback=self.timerCb)
        self.btn = []
        self.multiList = []
        self._multi_time = multi_time

    def attach(self, pin):
        self.btn.append(BtnChild(pin))
        return self.btn[-1]

    def detach(self, btnIn):
        if btnIn in self.btn:
            self.btn.remove(btnIn)

    def restart(self):
        self.multiList = []
        self.btn = self.btn[:3]
        for i in self.btn:
            i.restart()

    def multiBtnCb(self, btn1, btn2, callback=None):
        self.multiList.append([btn1, btn2, callback])
        btn1._cbState |= MULTI_PRESS
        btn2._cbState |= MULTI_PRESS

    def timerCb(self, arg):
        time_now = time.ticks_ms()
        for i in self.btn:
            i.update()

        for i in self.multiList:
            if i[0]._event & PRESS_WAIT and i[1]._event & PRESS_WAIT:
                if abs(i[0]._pressTime - i[1]._pressTime) < self._multi_time:
                    i[0]._event &= ~PRESS_WAIT
                    i[1]._event &= ~PRESS_WAIT
                    i[2]()

        for i in self.btn:
            if i._event & DOUBLE_PRESS:
                if i.cb[DOUBLE_PRESS]:
                    i.cb[DOUBLE_PRESS]()
                    i._event &= ~PRESS_WAIT
                    i._event &= ~DOUBLE_PRESS

            if i._event & PRESS_WAIT:
                if i._cbState & DOUBLE_PRESS:
                    if time_now - i._pressTime > i._doubleTime:
                        i._event &= ~PRESS_WAIT
                        if i.cb[PRESS]:
                            i.cb[PRESS]()
                        else:
                            i._event |= PRESS
                            i._eventTime[0] = 40

                elif i._cbState & MULTI_PRESS:
                    if time_now - i._pressTime > self._multi_time:
                        i._event &= ~PRESS_WAIT
                        if i.cb[PRESS]:
                            i.cb[PRESS]()
                        else:
                            i._event |= PRESS

                else:
                    i._event &= ~PRESS_WAIT
                    if i.cb[PRESS]:
                        i.cb[PRESS]()
                    else:
                        i._event |= PRESS

            if i._event & LONG_PRESS:
                if i.cb[LONG_PRESS]:
                    i._event &= ~LONG_PRESS
                    i.cb[LONG_PRESS]()

            if i._event & RELEASE:
                if i.cb[RELEASE]:
                    i._event &= ~RELEASE
                    i.cb[RELEASE]()

    def deinit(self):
        pass