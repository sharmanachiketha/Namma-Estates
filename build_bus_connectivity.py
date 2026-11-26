"""Build bus_connectivity.json: for each of the 30 area centre points, count the BMTC bus stops
and distinct base bus route numbers (first digits in the first word of the feed route name, so 293, 293-A, 293-B, G-293 and "293 KBS-X" count once) within 1.5 km, from the Reclaim City / Vonter Bengaluru GTFS feed.
Counts only: which stops and routes exist. No timetable, frequency or wait-time is used.
Usage: python build_bus_connectivity.py /path/to/unzipped/gtfs  (needs app.py COORDS)"""
import csv, json, math, sys, re
G = sys.argv[1]
src = open('app.py', encoding='utf-8').read()
m = re.search(r'^COORDS = \{(.*?)^\}', src, re.S | re.M)
COORDS = eval('{' + m.group(1) + '}')
R = 1500.0
def base(name):
    w = (name.split() or [''])[0]
    m = re.search(r'\d+', w)
    return m.group(0) if m else w  # '293-A', 'G-293', '293E' -> '293'; names without digits stay as is
def hav(a, b, c, d):
    p = math.pi / 180
    x = math.sin((c - a) * p / 2) ** 2 + math.cos(a * p) * math.cos(c * p) * math.sin((d - b) * p / 2) ** 2
    return 12742000 * math.asin(math.sqrt(x))
routes = {r['route_id']: base(r['route_short_name']) for r in csv.DictReader(open(G + '/routes.txt', encoding='utf-8'))}
trip_route = {r['trip_id']: r['route_id'] for r in csv.DictReader(open(G + '/trips.txt', encoding='utf-8'))}
stops = {s['stop_id']: (float(s['stop_lat']), float(s['stop_lon'])) for s in csv.DictReader(open(G + '/stops.txt', encoding='utf-8'))}
near = {a: set() for a in COORDS}
for sid, (la, lo) in stops.items():
    for a, (cl, co) in COORDS.items():
        if abs(la - cl) < 0.02 and abs(lo - co) < 0.02 and hav(la, lo, cl, co) <= R:
            near[a].add(sid)
want = {}
for a, ss in near.items():
    for s in ss: want.setdefault(s, []).append(a)
served = {a: set() for a in COORDS}
used = {a: set() for a in COORDS}
for r in csv.DictReader(open(G + '/stop_times.txt', encoding='utf-8')):
    s = r['stop_id']
    if s in want:
        rt = routes.get(trip_route.get(r['trip_id']))
        if rt:
            for a in want[s]:
                served[a].add(rt); used[a].add(s)
out = {a: {'stops': len(used[a]), 'routes': len(served[a])} for a in COORDS}
json.dump(out, open('bus_connectivity.json', 'w'), indent=1, sort_keys=True)
for a, v in sorted(out.items(), key=lambda x: -x[1]['routes']): print(a, v)
