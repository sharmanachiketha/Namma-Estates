"""Build static_geojsons.json + boundary_provenance.json.

Each area outline is the merge of the official GBA 2025 ward polygons listed in members.json
(wards: Greater Bengaluru Authority via OpenCity, "Other (Public Domain)"; KML downloaded from
https://data.opencity.in/dataset/gba-wards-delimitation-2025). Membership was chosen from ward-name
matches, OpenStreetMap place points inside each ward, and the site's area pin. It is a ward-based
approximation, not an official locality limit. HSR Layout uses its OpenStreetMap suburb outline
(osm_overrides.json, ODbL). Electronic City has no outline (outside the ward map).
Run: python build_boundaries.py
"""
import json
from shapely.geometry import Polygon, mapping
from shapely.ops import unary_union
wards = {w['n']: unary_union([Polygon(p).buffer(0) for p in w['p']]) for w in json.load(open('wards_opencity_gba.json'))}
members = json.load(open('members.json'))
over = json.load(open('osm_overrides.json'))
from shapely.geometry import shape
OSM_ONLY = {'HSR Layout'}
out, prov = {}, {}
for a, ws in members.items():
    ws = list(ws)
    if a in OSM_ONLY and a in over:
        out[a] = mapping(shape(over[a]).buffer(0).simplify(0.0001))
        prov[a] = {'outline_source': 'osm_suburb', 'approximate': False, 'wards': []}; continue
    if not ws:
        prov[a] = {'outline_source': 'none', 'approximate': True, 'wards': []}; continue
    u = unary_union([wards[w].buffer(0.0002) for w in ws]).buffer(-0.0002).simplify(0.0002)
    out[a] = mapping(u)
    prov[a] = {'outline_source': 'gba_wards', 'approximate': True, 'wards': sorted(ws)}
json.dump(out, open('static_geojsons.json', 'w'), separators=(',', ':'))
json.dump(prov, open('boundary_provenance.json', 'w'), indent=1)
print(len(out), sum(len(json.dumps(v)) for v in out.values()))
