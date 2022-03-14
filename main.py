from m5matrix import Matrix, Btn

btn = Btn()
btnA = btn.attach(39)
matrix = Matrix()


def on_pressed():
    matrix.fill(25, 10, 10)


def on_released():
    matrix.clear()


while True:
    btnA.was_pressed(on_pressed)
    btnA.was_released(on_released)
