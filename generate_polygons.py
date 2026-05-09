import json
import math

coords = {
    "Jayanagar": [12.9250, 77.5938],
    "HSR Layout": [12.9116, 77.6388],
    "BTM Layout": [12.9165, 77.6101],
    "MG Road": [12.9718, 77.6010],
    "Rajajinagar": [12.9881, 77.5548],
    "Indiranagar": [12.9783, 77.6408],
    "Koramangala": [12.9279, 77.6271],
    "Whitefield": [12.9698, 77.7499],
    "Electronic City": [12.8399, 77.6770],
    "Malleswaram": [13.0031, 77.5701],
    "Yelahanka": [13.1007, 77.5963],
    "Banashankari": [12.9254, 77.5467],
    "Bellandur": [12.9304, 77.6784],
    "Marathahalli": [12.9569, 77.7011],
    "Hebbal": [13.0354, 77.5988],
    "JP Nagar": [12.9063, 77.5857],
    "Basavanagudi": [12.9406, 77.5738],
    "Sarjapur Road": [12.9238, 77.6705],
    "KR Puram": [13.0084, 77.7001],
    "Yeshwanthpur": [13.0285, 77.5409]
}

def generate_polygon(lat, lon, radius_km=1.5, num_points=8):
    # 1 deg lat approx 111 km
    # 1 deg lon approx 111 * cos(lat) km
    points = []
    for i in range(num_points):
        angle = 2 * math.pi * i / num_points
        # add some irregular shape
        r = radius_km * (0.8 + 0.4 * (i % 2)) 
        d_lat = r / 111.0
        d_lon = r / (111.0 * math.cos(math.radians(lat)))
        points.append([lon + d_lon * math.cos(angle), lat + d_lat * math.sin(angle)])
    # close the polygon
    points.append(points[0])
    return {
        "type": "Polygon",
        "coordinates": [points]
    }

geojsons = {}
for area, (lat, lon) in coords.items():
    # adjust sizes based on roughly known area size
    radius = 1.2
    if area in ["Whitefield", "Electronic City", "Yelahanka"]:
        radius = 2.5
    elif area in ["MG Road"]:
        radius = 0.5
    elif area in ["Koramangala", "HSR Layout", "Jayanagar"]:
        radius = 1.5
    
    geojsons[area] = generate_polygon(lat, lon, radius)

with open('static_geojsons.json', 'w') as f:
    json.dump(geojsons, f)

print("Generated static_geojsons.json")
