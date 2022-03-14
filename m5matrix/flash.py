from time import sleep_ms


def flash_on(neo, i):
    neo[i] = (0, 170, 130)
    neo.write()
    sleep_ms(100)


def flash_off(neo, i):
    neo[i] = (0, 0, 0)
    neo.write()
    sleep_ms(100)


def blink(neo, i, sleep):
    neo[i] = (0, 170, 130)
    neo.write()
    sleep_ms(sleep)
    neo[i] = (0, 0, 0)
    neo.write()
    sleep_ms(sleep)
