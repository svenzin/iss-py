import time
import math
from datetime import datetime, timedelta
from sense_hat import SenseHat


class Azimuth:
    Names = {
        'N': 0, 'NNE': 22.5, 'NE': 45, 'ENE': 67.5,
        'E': 90, 'ESE': 112.5, 'SE': 135, 'SSE': 157.5,
        'S': 180, 'SSW': 202.5, 'SW': 225, 'WSW': 247.5,
        'W': 270, 'WNW': 292.5, 'NW': 315, 'NNW': 337.5,
    }

    @staticmethod
    def from_string(az):
        try:
            return Azimuth.Names[az]
        except KeyError:
            return None

    @staticmethod
    def to_string(az):
        while az < 0:
            az = az + 360
        name = None
        dist = 360
        for key in Azimuth.Names:
            d = abs(az - Azimuth.Names[key])
            if d < dist:
                dist = d
                name = key
        return name


class Pass:
    def __init__(self):
        self.StartTime = None
        self.StartAltitude = None
        self.StartAzimuth = None
        self.HighTime = None
        self.HighAltitude = None
        self.HighAzimuth = None
        self.EndTime = None
        self.EndAltitude = None
        self.EndAzimuth = None

    def __str__(self):
        return '{} | {}° {} @ {} | {}° {} @ {} | {}° {} @ {}'.format(
            self.StartTime.date(),
            self.StartAltitude,
            Azimuth.to_string(self.StartAzimuth),
            self.StartTime.strftime("%H:%M:%S"),
            self.HighAltitude,
            Azimuth.to_string(self.HighAzimuth),
            self.HighTime.strftime("%H:%M:%S"),
            self.EndAltitude,
            Azimuth.to_string(self.EndAzimuth),
            self.EndTime.strftime("%H:%M:%S"))


class Tween:
    @staticmethod
    def linear(x):
        return x

    @staticmethod
    def ramp(x):
        x = 4.898979 * (1 - x)
        x = (1 / math.sqrt(1 + x * x) - 0.2) / 0.8
        return x

    @staticmethod
    def distinv(x):
        x = 6 * (1 - x)
        x = 1 / math.sqrt(1 + x * x)
        return x

    @staticmethod
    def ease_in(x):
        x = 1 - ease_out(1 - x)
        return x

    @staticmethod
    def ease_out(x):
        x = math.sin(3.14156 * x / 2)
        return x

    @staticmethod
    def ease(x):
        x = 0.5 - 0.5 * math.cos(3.14156 * x)
        return x


class C:
    R = [255, 0, 0]
    G = [0, 255, 0]
    B = [0, 0, 255]
    W = [255, 255, 255]
    K = [0, 0, 0]


def border(angle):
    a = int(angle / 12.857143)
    x = [7,7,7,7,6,5,4,3,2,1,0,0,0,0,0,0,0,0,1,2,3,4,5,6,7,7,7,7][a]
    y = [4,5,6,7,7,7,7,7,7,7,7,6,5,4,3,2,1,0,0,0,0,0,0,0,0,1,2,3][a]
    return x, y

def fill(x, f):
    n = int(64.99 * f(x))
    return [C.W] * n + [C.K] * (64 - n)

def spot(x, f):
    pixels = [C.K] * 64
    r = 3.5 * 1.4142 * f(x)
    r2 = int(r**2)
    r3 = int(1.4 * r**2)
    for x in range(8):
        for y in range(8):
            d = (x - 3.5)**2 + (y - 3.5)**2
            if d <= r2:
                pixels[8 * y + x] = C.W
            elif d <= r3:
                z = int(256 * (r3 - d) / (r3 - r2))
                pixels[8 * y + x] = [z, z, z]
    return pixels

def spiral(x, f):
    pixels = [C.K] * 64
    n = int(64.99 * f(x))
    x, y = 3, 3
    i, d, r = 0, 0, 1
    dx = [1, 0, -1, 0]
    dy = [0, 1, 0, -1]
    while n > 0:
        pixels[8 * y + x] = C.W
        if r == 0:
            i = i + 1
            r = int(i / 2) + 1
            d = (d + 1) % 4
        x = x + dx[d]
        y = y + dy[d]
        r = r - 1
        n = n - 1
    return pixels

def monitor_pass(pass_details):
    sense = SenseHat()
    sense.clear()

    p = pass_details
    
    t0 = p.StartTime
    t1 = p.HighTime
    t2 = p.EndTime

    pixels = [C.K] * 64

    nx, ny = 0, 0
    while True:
        time.sleep(0.1)
        t = datetime.utcnow()
        if t >= t0: break

        pixels[8 * ny + nx] = C.K
        nx, ny = border(Azimuth.from_string('N'))
        pixels[8 * ny + nx] = C.B

        sense.set_pixels(pixels)

    while True:
        time.sleep(0.1)
        t = datetime.utcnow()
        if t > t2: break

        if t < t1:
            x = (t - t0).total_seconds() / (t1 - t0).total_seconds()
            a = x * p.HighAzimuth + (1 - x) * p.StartAzimuth
            if a > 180:
                a = a - 360
        else:
            x = (t2 - t).total_seconds() / (t2 - t1).total_seconds()
            a = x * p.HighAzimuth + (1 - x) * p.EndAzimuth
            if a > 180:
                a = a - 360

        #print('{0:0.3f} {1:0.3f}'.format(x, distinv(x)))
        #pixels = spot(x, distinv)
        #pixels = spiral(x, ramp)
        pixels = spot(x, Tween.distinv)

        nx, ny = border(Azimuth.from_string('N'))
        pixels[8 * ny + nx] = C.B

        px, py = border(a)
        pixels[8 * py + px] = C.R

        sense.set_pixels(pixels)

    sense.clear()

p = Pass()
p.StartTime = datetime.utcnow() + timedelta(seconds=2)
p.StartAltitude = 10
p.StartAzimuth = Azimuth.from_string('S')
p.HighTime = p.StartTime + timedelta(seconds=5)
p.HighAltitude = 90
p.HighAzimuth = Azimuth.from_string('W')
p.EndTime = p.HighTime + timedelta(seconds=5)
p.EndAltitude = 10
p.EndAzimuth = Azimuth.from_string('ESE')
print(p)

try:
    monitor_pass(p)
except:
    SenseHat().clear()
    raise
    
