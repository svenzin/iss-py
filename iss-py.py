import requests
import lxml.html as html
from datetime import date,  datetime


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


class Pass:
    Azimuth = {
        'N': 0, 'NNE': 22.5, 'NE': 45, 'ENE': 67.5,
        'E': 90, 'ESE': 112.5, 'SE': 135, 'SSE': 157.5,
        'S': 180, 'SSW': 202.5, 'SW': 225, 'WSW': 247.5,
        'W': 270, 'WNW': 292.5, 'NW': 315, 'NNW': 337.5,
    }

    def __init__(self):
        self.Date = date.today()
        self.Magnitude = 0.0
        self.StartTime = datetime.now()
        self.StartAltitude = 0.0
        self.StartAzimuth = Pass.Azimuth['N']
        self.HighestTime = datetime.now()
        self.HighestAltitude = 0.0
        self.HighestAzimuth = Pass.Azimuth['N']
        self.EndTime = datetime.now()
        self.EndAltitude = 0.0
        self.EndAzimuth = Pass.Azimuth['N']

    def __repr__(self):
        return ' '.join([str(i) for i in [self.Date, self.Magnitude,
                         self.StartTime, self.StartAltitude,
                         self.StartAzimuth,
                         self.HighestTime, self.HighestAltitude,
                         self.HighestAzimuth,
                         self.EndTime, self.EndAltitude,
                         self.EndAzimuth]])


def makePass(cells):
    pass_date = datetime.strptime(cells[0][0].text, '%d %b').date().replace(year=date.today().year)
    p = Pass()
    p.Date = pass_date
    p.Magnitude = float(cells[1].text)
    p.StartTime = datetime.combine(pass_date, datetime.strptime(cells[2].text, '%H:%M:%S').time())
    p.StartAltitude = float(cells[3].text.split('°')[0])
    p.StartAzimuth = Pass.Azimuth[cells[4].text]
    p.HighestTime = datetime.combine(pass_date, datetime.strptime(cells[5].text, '%H:%M:%S').time())
    p.HighestAltitude = float(cells[6].text.split('°')[0])
    p.HighestAzimuth = Pass.Azimuth[cells[7].text]
    p.EndTime = datetime.combine(pass_date, datetime.strptime(cells[8].text, '%H:%M:%S').time())
    p.EndAltitude = float(cells[9].text.split('°')[0])
    p.EndAzimuth = Pass.Azimuth[cells[10].text]
    return p


class API:
    def get_next_passes():
        passes = []
        r = requests.get(URL.pass_summary, headers=Headers.firefox, params=Location.Pune)
        d = html.fromstring(r.text)
        for row in d.cssselect('.standardTable .clickableRow'):
            passes.append(makePass(row.cssselect('td')))
        return passes


def main():
    print('\n'.join((str(p) for p in API.get_next_passes())))


if __name__ == '__main__':
    main()
