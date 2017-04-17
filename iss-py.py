import requests
import lxml.html as html
import time
from datetime import date, datetime, timedelta
from sense_hat import SenseHat
import math


class URL:
    pass_summary = 'http://www.heavens-above.com/PassSummary.aspx'


class Headers:
    firefox = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0'
    }


class Location:
    Unspecified = {'satid': 25544,
                   'lat': 0,
                   'lng': 0,
                   'loc': 'Unspecified',
                   'alt': 0,
                   'tz': 'UCT'}
    Pune = {'satid': 25544,
            'lat': 18.5204,
            'lng': 73.8567,
            'loc': 'Pune',
            'alt': 560,
            'tz': 'UCTm5colon30'}
    Marcellaz = {'satid': 25544,
                 'lat': 46.1453,
                 'lng': 6.355,
                 'loc': 'Marcellaz',
                 'alt': 647,
                 'tz': 'CET'}


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


def makePass(cells):
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


class API:
    @staticmethod
    def get_next_visibles():
        passes = []
        r = requests.get(URL.pass_summary, headers=Headers.firefox, params=Location.Pune)
        d = html.fromstring(r.text)
        for row in d.cssselect('.standardTable .clickableRow'):
            passes.append(makePass(row.cssselect('td')))
        return passes

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

    @staticmethod
    def blink(x):
        x = math.sin(3.14156 * x)
        #x = Tween.ease(2 * x)
        return x

    @staticmethod
    def double(x):
        x = 2 * x % 1
        return x


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


class Display:
    def __init__(self):
        self.sense_hat = SenseHat()
        self.pixels = [Color.Black] * 64

    def clear(self):
        for i in range(64):
            self.pixels[i] = Color.Black

    def show(self):
        self.sense_hat.set_pixels(self.pixels)

    def set(self, x, y, c):
        self.pixels[8 * y + x] = c

    def pie(self, x, c):
        lut = [0.625, 0.651, 0.686, 0.727, 0.773, 0.814, 0.849, 0.875,
               0.599, 0.625, 0.664, 0.719, 0.781, 0.836, 0.875, 0.901,
               0.564, 0.586, 0.625, 0.699, 0.801, 0.875, 0.914, 0.936,
               0.523, 0.531, 0.551, 0.625, 0.875, 0.949, 0.969, 0.977,
               0.477, 0.469, 0.449, 0.375, 0.125, 0.051, 0.031, 0.023,
               0.436, 0.414, 0.375, 0.301, 0.199, 0.125, 0.086, 0.064,
               0.401, 0.375, 0.336, 0.281, 0.219, 0.164, 0.125, 0.099,
               0.375, 0.349, 0.314, 0.273, 0.227, 0.186, 0.151, 0.125]
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
        x = [7, 7, 7, 7,
             6, 5, 4, 3, 2, 1, 0,
             0, 0, 0, 0, 0, 0, 0,
             1, 2, 3, 4, 5, 6, 7,
             7, 7, 7][ai]
        y = [4, 5, 6, 7,
             7, 7, 7, 7, 7, 7, 7,
             6, 5, 4, 3, 2, 1, 0,
             0, 0, 0, 0, 0, 0, 0,
             1, 2, 3][ai]
        self.set(x, y, c)


class Action:
    def __init__(self):
        self.display = None

    def run(self):
        pass

    def spin_until(self, t, step=0.1):
        while datetime.utcnow() < t:
            time.sleep(step)


class Standby(Action):
    def __init__(self, next_pass):
        super().__init__()
        self.next_pass = next_pass

    def run(self, display):
        display.clear()
        display.show()
        
        t0 = self.next_pass.StartTime - timedelta(seconds=6)
        while True:
            t = datetime.utcnow()
            if t >= t0: return

            display.set(0, 0, Color.Green)
            display.show()
            time.sleep(0.1)

            display.set(0, 0, Color.Black)
            display.show()
            time.sleep(0.9)


class Countdown(Action):
    def __init__(self, next_pass):
        super().__init__()
        self.next_pass = next_pass

    def run(self, display):
        display.clear()
        display.show()

        t0 = self.next_pass.StartTime - timedelta(seconds=7)
        t1 = self.next_pass.StartTime - timedelta(seconds=2)

        self.spin_until(t0)
        
        while True:
            t = datetime.utcnow()
            if t >= t1: return
            
            x = (t1 - t).total_seconds() / (t1 - t0).total_seconds()
            display.clear()
            display.pie(x, Color.scale(0.5, Color.Red))
            display.show()
            time.sleep(0.01)


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
            display.edge(self.next_pass.StartAzimuth, Color.scale(0.25, Color.Red))
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
            time.sleep(0.01)

        
class IssPy:
    def __init__(self):
        self.display = Display()
        self.next_pass = None

    def step(self):
        if self.next_pass is None:
            #self.next_pass = API.get_next_visible()
            now = datetime.utcnow()
            dt2 = timedelta(seconds=2)
            dt10 = timedelta(seconds=10)
            p = Pass()
            p.Date = date.today()
            p.Magnitude = 0
            p.StartTime = now + dt10
            p.StartAltitude = 10
            p.StartAzimuth = Azimuth.from_string('S')
            p.HighTime = now + dt10 + dt2
            p.HighAltitude = 90
            p.HighAzimuth = Azimuth.from_string('W')
            p.EndTime = now + dt10 + 3 * dt2
            p.EndAltitude = 10
            p.EndAzimuth = Azimuth.from_string('ESE')
            self.next_pass = p
            return 1, self.next_pass

        Standby(self.next_pass).run(self.display)
        Countdown(self.next_pass).run(self.display)
        Setup(self.next_pass).run(self.display)
        Monitor(self.next_pass).run(self.display)
        t = datetime.utcnow()

        if self.next_pass.EndTime < t:
            self.next_pass = None

        return 1, None


def main(args):
    try:
        isspy = IssPy()
        while True:
            dt, data = isspy.step()
            if data is not None:
                print(datetime.utcnow(), dt, data)
            time.sleep(dt)
    except:
        SenseHat().clear()
        raise


if __name__ == '__main__':
    import sys
    main(sys.argv)
