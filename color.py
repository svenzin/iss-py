from sense_hat import SenseHat
import time

def black(x): return [0, 0, 0]
def red(x): return [8 * x, 0, 0]
def green(x): return [0, 8 * x, 0]
def blue(x): return [0, 0, 8 * x]
def yellow(x): return [8 * x, 8 * x, 0]
def cyan(x): return [0, 8 * x, 8 * x]
def magenta(x): return [8 * x, 0, 8 * x]
def white(x): return [8 * x, 8 * x, 8 * x]

##def pixels(l, r, c):
##    return [c(l)] * 32 + [c(r)] * 32

def pixels(r, g, b):
    _ = black(0)
    w = white(r)
    y = yellow(r)
    return [y, y, _, _, _, y, y, _,
            y, y, _, _, _, y, y, _,
            y, y, _, w, _, y, y, _,
            y, w, w, w, w, w, y, _,
            y, y, _, w, _, y, y, _,
            y, y, _, w, _, y, y, _,
            y, y, _, _, _, y, y, _,
            _, _, _, _, _, _, _, _]
    return [y, _, y, _, _, y, _, y,
            y, _, y, _, _, y, _, y,
            y, _, y, w, w, y, _, y,
            y, w, w, w, w, w, w, y,
            y, w, w, w, w, w, w, y,
            y, _, y, w, w, y, _, y,
            y, _, y, _, _, y, _, y,
            y, _, y, _, _, y, _, y]
    return [[8 * r, 8 * g, 8 * b]] * 64

try:
    sense = SenseHat()
    #sense.gamma = [0, 1, 3, 10, 31] + [0] * 27
    color = white
    i, j = 0, 0
    r, g, b = 0, 0, 0
    while True:
        c = input('> ')
        if c == 'x': break
##        if c == 'r': color = red
##        if c == 'g': color = green
##        if c == 'b': color = blue
##        if c == 'y': color = yellow
##        if c == 'c': color = cyan
##        if c == 'm': color = magenta
##        if c == 'w': color = white
##        if c == '4' and i < 6: i += 1
##        if c == '1' and i > 0: i -= 1
##        if c == '6' and j < 6: j += 1
##        if c == '3' and j > 0: j -= 1
        if c == 'a' and r < 31: r += 1
        if c == 'q' and r > 0: r -= 1
        if c == 'z' and g < 31: g += 1
        if c == 's' and g > 0: g -= 1
        if c == 'e' and b < 31: b += 1
        if c == 'd' and b > 0: b -= 1
        print(r, g, b)
        sense.set_pixels(pixels(r, g, b))
    sense.clear()
    sense.gamma_reset()
except:
    SenseHat().clear()
    SenseHat().gamma_reset()
    raise
