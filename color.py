from sense_hat import SenseHat
import time

class Color:
    Red = [255, 0, 0]
    Green = [0, 255, 0]
    Blue = [0, 0, 255]
    White = [255, 255, 255]
    Black = [0, 0, 0]

    @staticmethod
    def scale(x, c):
        return [int(x * i) for i in c]

    @staticmethod
    def red(x):
        return Color.scale(x, Color.Red)

    @staticmethod
    def green(x):
        return Color.scale(x, Color.Green)

    @staticmethod
    def blue(x):
        return Color.scale(x, Color.Blue)

    @staticmethod
    def white(x):
        return Color.scale(x, Color.White)
    
pixels = [Color.Black] * 64
for i in range(64):
    pixels[i] = Color.scale(4 * (i + 1) / 256, [0, 0, 255])

try:
    sense = SenseHat()
    sense.set_pixels(pixels)
    for i in range(64):
        print(i)
    time.sleep(10)
    sense.clear()
except:
    SenseHat().clear()
    raise
