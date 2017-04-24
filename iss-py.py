import requests
import lxml.html as html
import time
from datetime import date, datetime, timedelta
from sense_hat import SenseHat
import math


def info(*args):
    print(datetime.utcnow().strftime("[%y-%m-%d %H:%M:%S]"), *args)


class Location:
    Tintagel = {'name': 'Tintagel Castle',
                'lat': 50.6673,
                'lng': -4.7585,
                'alt': 39,
                'tz': 'GMT'}


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
        self.Date = None
        self.Magnitude = None
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
        return '{} | {} | {}° {} @ {} | {}° {} @ {} | {}° {} @ {}'.format(
            self.Date,
            self.Magnitude,
            self.StartAltitude,
            Azimuth.to_string(self.StartAzimuth),
            self.StartTime.strftime("%H:%M:%S"),
            self.HighAltitude,
            Azimuth.to_string(self.HighAzimuth),
            self.HighTime.strftime("%H:%M:%S"),
            self.EndAltitude,
            Azimuth.to_string(self.EndAzimuth),
            self.EndTime.strftime("%H:%M:%S"))


class HeavensAbove:
    def __init__(self, loc):
        self.location = loc

    def name(self):
        return "Heavens Above (www.heavens-above.com)"
    
    def get_next_visibles(self):
        passes = []
        r = requests.get('http://www.heavens-above.com/PassSummary.aspx',
                         params=HeavensAbove._from_location(self.location))
        d = html.fromstring(r.text)
        now = datetime.utcnow()
        for row in d.cssselect('.standardTable .clickableRow'):
            p = HeavensAbove._make_pass(row.cssselect('td'))
            if p.EndTime > now:
                passes.append(p)
        return passes

    @staticmethod
    def _from_location(loc):
        return {'satid': 25544,
                'lat': loc['lat'],
                'lng': loc['lng'],
                'loc': loc['name'],
                'alt': loc['alt'],
                'tz': 'UCT'}

    @staticmethod
    def _make_pass(cells):
        pass_date = datetime.strptime(cells[0][0].text, '%d %b')
        pass_date = pass_date.date()
        pass_date = pass_date.replace(year=date.today().year)

        p = Pass()
        p.Date = pass_date
        p.Magnitude = float(cells[1].text)
        start_time = datetime.strptime(cells[2].text, '%H:%M:%S').time()
        p.StartTime = datetime.combine(pass_date, start_time)
        p.StartAltitude = float(cells[3].text.split('°')[0])
        p.StartAzimuth = Azimuth.from_string(cells[4].text)
        high_time = datetime.strptime(cells[5].text, '%H:%M:%S').time()
        p.HighTime = datetime.combine(pass_date, high_time)
        p.HighAltitude = float(cells[6].text.split('°')[0])
        p.HighAzimuth = Azimuth.from_string(cells[7].text)
        end_time = datetime.strptime(cells[8].text, '%H:%M:%S').time()
        p.EndTime = datetime.combine(pass_date, end_time)
        p.EndAltitude = float(cells[9].text.split('°')[0])
        p.EndAzimuth = Azimuth.from_string(cells[10].text)
        return p


class TestProvider:
    def name(self):
        return "TestProvider"
    
    def get_next_visibles(self):
        now = datetime.utcnow()
        p = Pass()
        p.Date = date.today()
        p.Magnitude = -2.6
        p.StartTime = now + timedelta(minutes=1.2)
        p.StartAltitude = 10
        p.StartAzimuth = Azimuth.from_string('WNW')
        p.HighTime = p.StartTime + timedelta(minutes=1)
        p.HighAltitude = 37
        p.HighAzimuth = Azimuth.from_string('SW')
        p.EndTime = p.HighTime + timedelta(minutes=1)
        p.EndAltitude = 24
        p.EndAzimuth = Azimuth.from_string('S')
        return [p]


class API:
    _provider = None

    @staticmethod
    def set_provider(provider):
        API._provider = provider
        info('Provider set to "{}"'.format(provider.name()))

    @staticmethod
    def get_next_visibles():
        if API._provider is None:
            return []
        return API._provider.get_next_visibles()

    @staticmethod
    def get_next_visible():
        try:
            return API.get_next_visibles()[0]
        except IndexError:
            return None


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
        x = 1 - Tween.ease_out(1 - x)
        return x

    @staticmethod
    def ease_out(x):
        x = math.sin(3.14156 * x / 2)
        return x

    @staticmethod
    def ease(x):
        x = 0.5 - 0.5 * math.cos(3.14156 * x)
        return x

    @staticmethod
    def blink(x):
        x = math.sin(3.14156 * x)
        #x = Tween.ease(2 * x)
        return x

    @staticmethod
    def double(x):
        x = 2 * x % 1
        return x

    @staticmethod
    def back_and_forth(x):
        return 1 - abs(1 - 2 * x)


class Color:
    Red = [255, 0, 0]
    Green = [0, 255, 0]
    Blue = [0, 0, 255]
    White = [255, 255, 255]
    Black = [0, 0, 0]
    Yellow = [255, 255, 0]

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
    def yellow(x):
        return Color.scale(x, Color.Yellow)

    @staticmethod
    def white(x):
        return Color.scale(x, Color.White)


class Display:
    def __init__(self):
        self.sense_hat = SenseHat()
        self.sense_hat.rotation = 180
        self.pixels = [Color.Black] * 64
        self.enabled = True

    def disable(self):
        self.enabled = False
        self.sense_hat.clear()

    def enable(self):
        self.enabled = True

    def clear(self):
        for i in range(64):
            self.pixels[i] = Color.Black

    def show(self):
        if self.enabled:
            self.sense_hat.set_pixels(self.pixels)

    def set(self, x, y, c):
        self.pixels[8 * y + x] = c

    def pie(self, x, c):
        lut = [0.875, 0.901, 0.936, 0.977, 0.023, 0.064, 0.099, 0.125,
               0.849, 0.875, 0.914, 0.969, 0.031, 0.086, 0.125, 0.151,
               0.814, 0.836, 0.875, 0.949, 0.051, 0.125, 0.164, 0.186,
               0.773, 0.781, 0.801, 0.875, 0.125, 0.199, 0.219, 0.227,
               0.727, 0.719, 0.699, 0.625, 0.375, 0.301, 0.281, 0.273,
               0.686, 0.664, 0.625, 0.551, 0.449, 0.375, 0.336, 0.314,
               0.651, 0.625, 0.586, 0.531, 0.469, 0.414, 0.375, 0.349,
               0.625, 0.599, 0.564, 0.523, 0.477, 0.436, 0.401, 0.375]
        for i in range(64):
            if lut[i] <= x:
                self.pixels[i] = c

    def spot(self, x, c):
        r = 3.5 * 1.4142 * x
        r2 = int(r**2)
        r3 = int(1.4 * r**2)
        d2 = [24.5, 18.5, 14.5, 12.5, 12.5, 14.5, 18.5, 24.5,
              18.5, 12.5,  8.5,  6.5,  6.5,  8.5, 12.5, 18.5,
              14.5,  8.5,  4.5,  2.5,  2.5,  4.5,  8.5, 14.5,
              12.5,  6.5,  2.5,  0.5,  0.5,  2.5,  6.5, 12.5,
              12.5,  6.5,  2.5,  0.5,  0.5,  2.5,  6.5, 12.5,
              14.5,  8.5,  4.5,  2.5,  2.5,  4.5,  8.5, 14.5,
              18.5, 12.5,  8.5,  6.5,  6.5,  8.5, 12.5, 18.5,
              24.5, 18.5, 14.5, 12.5, 12.5, 14.5, 18.5, 24.5]
        for i in range(64):
            if d2[i] <= r2:
                self.pixels[i] = c
            elif d2[i] <= r3:
                z = (r3 - d2[i]) / (r3 - r2)
                self.pixels[i] = Color.scale(x, c)

    def edge(self, az, c):
        ai = int(az / 12.857143)
        x = [4, 5, 6, 7,
             7, 7, 7, 7, 7, 7, 7,
             6, 5, 4, 3, 2, 1, 0,
             0, 0, 0, 0, 0, 0, 0,
             1, 2, 3][ai]
        y = [0, 0, 0, 0,
             1, 2, 3, 4, 5, 6, 7,
             7, 7, 7, 7, 7, 7, 7,
             6, 5, 4, 3, 2, 1, 0,
             0, 0, 0][ai]
        self.set(x, y, c)

    def draw(self, mask, dx, dy, c):
        sy, sx = len(mask), len(mask[0])
        x0 = max(0, -dx)
        x1 = min(sx, 8 - dx) 
        y0 = max(0, -dy)
        y1 = min(sy, 8 - dy)
        for y in range(y0, y1):
            for x in range(x0, x1):
                if mask[y][x] > 0:
                    self.pixels[8 * (y + dy) + (x + dx)] = c

    def letter(self, l, dx, dy, c):
        print(l)
        l = S.get(l)
        print(l)
        if l:
            self.draw(l, dx, dy, c)


class S:
    iss_body = [[0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 1, 0, 0, 0],
                [0, 1, 1, 1, 1, 1, 0],
                [0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0]]
    iss_panels = [[1, 1, 0, 0, 0, 1, 1],
                  [1, 1, 0, 0, 0, 1, 1],
                  [1, 1, 0, 0, 0, 1, 1],
                  [1, 0, 0, 0, 0, 0, 1],
                  [1, 1, 0, 0, 0, 1, 1],
                  [1, 1, 0, 0, 0, 1, 1],
                  [1, 1, 0, 0, 0, 1, 1]]
    email = [[1, 1, 1, 1, 1, 1, 1],
             [1, 1, 0, 0, 0, 1, 1],
             [1, 0, 1, 0, 1, 0, 1],
             [1, 0, 0, 1, 0, 0, 1],
             [1, 0, 0, 0, 0, 0, 1],
             [1, 1, 1, 1, 1, 1, 1]]
    data = 'eNp1kgkOACEIA4f/f3o3HqWixBjkKlgggvgvQzLe0ilvWD' \
           'ZWfFzyeUbCxs4a21cvVlE1h0Q6Myx9Xe0Z1nhWX4bH05tI' \
           '+oNxIT2srzjR9FeSg9oX4RgUW+Xo4IueL8O+Ypw/MmvH2p' \
           'zItop+VuLFnvrec+KeP2V/RGXYzt28yQaPPer5+gAhdQFn'
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789'
    letters = {}
    digits = []

    @staticmethod
    def init():
        import zlib, base64
        pixels = zlib.decompress(base64.b64decode(S.data))
        pixels = [pixels[152*i:152*(i+1)] for i in range(5)]
        S.letters = {}
        for i in range(len(S.alphabet)):
            l = S.alphabet[i]
            letter = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
            for y in range(5):
                for x in range(4):
                    letter[y][x] = pixels[y][4 * i + x]
            S.letters[l] = letter
        for n in range(10):
            d = str(n)
            S.digits.append(S.letters[d])

    @staticmethod
    def letter(l):
        try:
            return S.letters[l]
        except KeyError:
            return None

    @staticmethod
    def digit(n):
        try:
            return S.digits[n]
        except IndexError:
            return None


class T:
    # Test scenario
##    BlinkUp = 0.1
##    StatusUpdate = 1
##    OnlineUpdate = 10
##    SpinStep = 0.1
##    AnimationUpdate = 0.01
##    CountdownDuration = timedelta(seconds=6)
##    SetupDuration = timedelta(seconds=2)

    # Highrez
    BlinkUp = 0.1
    StatusUpdate = 2
    OnlineUpdate = 10
    SpinStep = 0.1
    AnimationUpdate = 0.1
    CountdownDuration = timedelta(seconds=60)
    SetupDuration = timedelta(seconds=15)

    # Lowrez
##    BlinkUp = 0.1
##    StatusUpdate = 10
##    OnlineUpdate = 60
##    SpinStep = 0.1
##    AnimationUpdate = 1
##    CountdownDuration = timedelta(seconds=300)
##    SetupDuration = timedelta(seconds=60)

class Action:
    def __init__(self):
        self.display = None

    def run(self):
        pass

    def spin_until(self, t, step=T.SpinStep):
        while datetime.utcnow() < t:
            time.sleep(step)

    def blink(self, display, c):
        display.set(7, 7, c)
        display.show()

        time.sleep(T.BlinkUp)

        display.set(7, 7, Color.Black)
        display.show()


class Search(Action):
    def __init__(self):
        super().__init__()

    def run(self, display):
        display.clear()
        display.show()

        t0 = datetime.fromordinal(1)
        while True:
            t = datetime.utcnow()
            if t >= t0:
                display.set(0, 0, Color.yellow(0.5))
                display.show()

                next_pass = API.get_next_visible()

                display.set(0, 0, Color.Black)
                display.show()

                if next_pass is not None:
                    return next_pass

                t0 = t + timedelta(seconds=T.OnlineUpdate)

            self.blink(display, Color.red(0.5))
            time.sleep(T.StatusUpdate)


class Standby(Action):
    def __init__(self, next_pass):
        super().__init__()
        self.next_pass = next_pass

    def run(self, display):
        display.clear()
        display.show()

        t0 = self.next_pass.StartTime - T.CountdownDuration - T.SetupDuration
        while True:
            t = datetime.utcnow()
            if t >= t0: return

            self.blink(display, Color.green(0.5))
            time.sleep(T.StatusUpdate)
        

class Countdown(Action):
    def __init__(self, next_pass):
        super().__init__()
        self.next_pass = next_pass

    def run(self, display):
        display.clear()
        display.show()

        t0 = self.next_pass.StartTime - T.CountdownDuration - T.SetupDuration
        t1 = self.next_pass.StartTime - T.SetupDuration

        self.spin_until(t0)
        
        while True:
            t = datetime.utcnow()
            if t >= t1: return
            
            x = (t1 - t).total_seconds() / (t1 - t0).total_seconds()
            display.clear()
            display.pie(x, Color.red(0.5))
            dt = int((t1 - t).total_seconds())
            if (dt < 100):
                display.draw(S.digit(dt // 10), 1, 1, Color.White)
                display.draw(S.digit(dt % 10), 4, 1, Color.White)
            display.show()
            time.sleep(T.AnimationUpdate)


class Setup(Action):
    def __init__(self, next_pass):
        super().__init__()
        self.next_pass = next_pass

    def run(self, display):
        display.clear()
        display.show()

        t0 = self.next_pass.StartTime
        while datetime.utcnow() < t0:
            display.clear()
            display.edge(Azimuth.from_string('N'), Color.Blue)
            display.show()
            time.sleep(0.2)
            display.clear()
            display.edge(Azimuth.from_string('N'), Color.Blue)
            display.edge(self.next_pass.StartAzimuth, Color.red(0.5))
            display.show()
            time.sleep(0.2)


class Monitor(Action):
    def __init__(self, next_pass):
        super().__init__()
        self.next_pass = next_pass

    def run(self, display):
        display.clear()
        display.show()

        t0 = self.next_pass.StartTime
        t1 = self.next_pass.HighTime
        t2 = self.next_pass.EndTime

        self.spin_until(t0)

        da1 = self.next_pass.HighAzimuth - self.next_pass.StartAzimuth
        if da1 > 180:
            da1 = da1 - 360
        da2 = self.next_pass.EndAzimuth - self.next_pass.HighAzimuth
        if da2 > 180:
            da2 = da2 - 360

        while True:
            t = datetime.utcnow()
            if t >= t2: return

            if t < t1:
                x = (t - t0).total_seconds() / (t1 - t0).total_seconds()
                az = self.next_pass.StartAzimuth + x * da1
                if az < 0:
                    az = az + 360
            else:
                x = (t2 - t).total_seconds() / (t2 - t1).total_seconds()
                az = self.next_pass.EndAzimuth - x * da2
                if az < 0:
                    az = az + 360

            display.clear()
            display.spot(Tween.distinv(x), Color.White)
            display.edge(Azimuth.from_string('N'), Color.Blue)
            display.edge(az, Color.Red)
            display.show()
            time.sleep(T.AnimationUpdate)

def splash_screen(display):
    for i in range(20):
        x = Tween.ease(Tween.back_and_forth(i / 20))
        display.clear()
        display.draw(S.iss_panels, 0, 0, Color.yellow(x))
        display.draw(S.iss_body, 0, 0, Color.white(x))
        display.show()
        time.sleep(0.1)
    
    
def debug(display):
    for l in S.alphabet:
        display.clear()
        display.letter(l, 0, 0, Color.Red)
        display.show()
        time.sleep(0.05)

    display.clear()
    display.draw(S.iss_panels, 0, 0, Color.Yellow)
    display.draw(S.iss_body, 0, 0, Color.White)
    display.show()
    time.sleep(1)

    display.clear()
    display.draw(S.email, 0, 0, Color.White)
    display.show()
    time.sleep(1)

    for x in range(8):
        display.clear()
        display.draw(S.email, x, 0, Color.White)
        display.show()
        time.sleep(0.1)
        
class IssPy:
    def __init__(self):
        self.display = Display()
        self.next_pass = None
        
##        debug(self.display)
        splash_screen(self.display)

    def step(self):
        if self.next_pass is None:
            self.next_pass = Search().run(self.display)
            info("Next pass:", self.next_pass)

        if self.next_pass is not None:
            Standby(self.next_pass).run(self.display)
            Countdown(self.next_pass).run(self.display)
            Setup(self.next_pass).run(self.display)
            Monitor(self.next_pass).run(self.display)
            self.next_pass = None


def main(arguments):
    import argparse
    import json
    parser = argparse.ArgumentParser('IssPy - ISS monitoring system')
    parser.add_argument('-f', type=open, dest='file')
##    args = parser.parse_args(arguments[1:])
##    args = parser.parse_args('-f marcellaz.json'.split())
    args = parser.parse_args('-f pune.json'.split())

    settings = None
    if args.file:
        settings = json.load(args.file)

    location = Location.Tintagel
    if settings:
        location = settings
    info('Location set to "{}"'.format(location['name']))

    S.init()

    try:
        provider = TestProvider()
        API.set_provider(TestProvider())
##        API.set_provider(HeavensAbove(location))
        isspy = IssPy()
        while True:
            data = isspy.step()
    except:
        SenseHat().clear()
        raise


if __name__ == '__main__':
    import sys
    main(sys.argv)
