import urllib.parse
import urllib.request
import json

print('ISS-Py location configurator, powered with Nominatim (nominatim.openstreetmap.org)')
print('Enter your address:')
address = input()

print('Querying coordinates...')
api = 'https://nominatim.openstreetmap.org/search?'
params = 'q="{}"&format=json&addressdetails=1&namedetails=1'.format(urllib.parse.quote(address))
url = api + params
print(url)
with urllib.request.urlopen(url) as req:
    data = json.loads(req.read().decode())

print('Found {} candidates:'.format(len(data)))
for (i, d) in enumerate(data):
    print(' [{}] {}'.format(i, d['display_name']))

index = None
while index is None:
    print('Select the correct address: [0]')
    index = input()
    if len(index) == 0:
        index = 0
    try:
        index = int(index)
        if index >= len(data):
            index = None
    except:
        index = None

name = data[index]['display_name']
lat = data[index]['lat']
lon = data[index]['lon']

print('Enter the location\'s elevation in meters if known:')
elevation = input()
try:
    elevation = int(elevation)
except ValueError:
    print('Querying elevation...')
    try:
        api = 'https://api.open-elevation.com/api/v1/lookup?'
        params = 'locations={},{}|0,0'.format(d['lat'], d['lon'])
        url = api + params
        print(url)
        with urllib.request.urlopen(url) as req:
            data = json.loads(req.read().decode())
        elevation = int(data[0]['elevation'])
    except:
        print('Failed. Defaulting to zero.')
        elevation = 0

print('Name set to {}'.format(name))
print('Latitude set to {}'.format(lat))
print('Longitude set to {}'.format(lon))
print('Elevation set to {}'.format(elevation))
location = {
    'name': name,
    'lat': float(lat),
    'lng': float(lon),
    'alt': elevation,
    'tz': 'GMT'
}
print(json.dumps(location, indent=4))

print('Do you want to generate the ISS-Py config file with this data? [y/n]')
text = input()
if text.lower() in ['y', 'yes']:
    print('Generating config.json...')
    with open('config.json', 'w') as config:
        config.write(json.dumps(location, indent=4))

