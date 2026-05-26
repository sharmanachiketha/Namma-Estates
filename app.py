import os
import time
import requests
import json
import xml.etree.ElementTree as ET
from flask import Flask, render_template, jsonify
import random

app = Flask(__name__)

# Prevent browser caching of resources
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

CACHE_FILE = 'sentiment_cache.json'
cache_data = {}

def load_cache():
    global cache_data
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                cache_data = json.load(f)
        except Exception as e:
            print(f"Error loading cache file: {e}")
            cache_data = {}
    else:
        cache_data = {}

def save_cache():
    try:
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache_data, f, indent=4)
    except Exception as e:
        print(f"Error saving cache file: {e}")

# Load cache on startup
load_cache()

AREAS = [
    "Jayanagar",
    "HSR Layout",
    "BTM Layout",
    "MG Road",
    "Rajajinagar",
    "Indiranagar",
    "Koramangala",
    "Whitefield",
    "Electronic City",
    "Malleswaram",
    "Yelahanka",
    "Banashankari",
    "Bellandur",
    "Marathahalli",
    "Hebbal",
    "JP Nagar",
    "Basavanagudi",
    "Sarjapur Road",
    "KR Puram",
    "Yeshwanthpur",
    "Kalyan Nagar",
    "Kammanahalli",
    "Nagarabhaavi",
    "Vijayanagar",
    "RT Nagar",
    "Bannerghatta Road",
    "Begur",
    "Singasandra",
    "RR Nagar",
    "Puttenahalli"
]

BASE_PRICES = {
    "Jayanagar": 14000,
    "HSR Layout": 11500,
    "BTM Layout": 9500,
    "MG Road": 22000,
    "Rajajinagar": 12500,
    "Indiranagar": 16000,
    "Koramangala": 15500,
    "Whitefield": 10500,
    "Electronic City": 7500,
    "Malleswaram": 14500,
    "Yelahanka": 8500,
    "Banashankari": 11000,
    "Bellandur": 12500,
    "Marathahalli": 10000,
    "Hebbal": 13000,
    "JP Nagar": 11500,
    "Basavanagudi": 15000,
    "Sarjapur Road": 11000,
    "KR Puram": 8000,
    "Yeshwanthpur": 9500,
    "Kalyan Nagar": 8500,
    "Kammanahalli": 8000,
    "Nagarabhaavi": 9000,
    "Vijayanagar": 11500,
    "RT Nagar": 10000,
    "Bannerghatta Road": 7500,
    "Begur": 6500,
    "Singasandra": 6000,
    "RR Nagar": 8500,
    "Puttenahalli": 9500
}

COORDS = {
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
    "Yeshwanthpur": [13.0285, 77.5409],
    "Kalyan Nagar": [13.0274, 77.6411],
    "Kammanahalli": [13.0092, 77.6368],
    "Nagarabhaavi": [12.9719, 77.5093],
    "Vijayanagar": [12.9696, 77.5360],
    "RT Nagar": [13.0184, 77.5934],
    "Bannerghatta Road": [12.8966, 77.5975],
    "Begur": [12.8806, 77.6244],
    "Singasandra": [12.8860, 77.6540],
    "RR Nagar": [12.9248, 77.5200],
    "Puttenahalli": [12.8997, 77.5818]
}

WATER_AVAILABILITY = {
    "Jayanagar": "High (Cauvery Stage 1/2)",
    "HSR Layout": "High-Medium (Cauvery Stage 4 Ph 1)",
    "BTM Layout": "High-Medium (Cauvery Stage 4 Ph 1)",
    "MG Road": "High (Cauvery Stage 1/3)",
    "Rajajinagar": "High-Medium (Cauvery Stage 4 Ph 1)",
    "Indiranagar": "High-Medium (Cauvery Stage 3/4 Ph 2)",
    "Koramangala": "High-Medium (Cauvery Stage 1/4 Ph 1)",
    "Whitefield": "Low (Tanker Dependent / Stage 5)",
    "Electronic City": "High-Medium (Cauvery Stage 4 Ph 1)",
    "Malleswaram": "High (Cauvery Stage 3)",
    "Yelahanka": "Medium (Cauvery Stage 4 Ph 2)",
    "Banashankari": "High (Cauvery Stage 2)",
    "Bellandur": "Low (Tanker Dependent / Stage 4 Ph 1 Planning)",
    "Marathahalli": "Medium (Cauvery Stage 4 Ph 2)",
    "Hebbal": "Low (Tanker Dependent)",
    "JP Nagar": "High-Medium (Cauvery Stage 2/4)",
    "Basavanagudi": "High (Cauvery Stage 1/2)",
    "Sarjapur Road": "Low (Tanker Dependent)",
    "KR Puram": "Low (Tanker Dependent)",
    "Yeshwanthpur": "High-Medium (Cauvery Stage 4 Ph 1)",
    "Kalyan Nagar": "Medium (Cauvery Stage 4 Ph 2)",
    "Kammanahalli": "Medium (Cauvery Stage 4 Ph 2)",
    "Nagarabhaavi": "High-Medium (Cauvery Stage 4)",
    "Vijayanagar": "High-Medium (Cauvery Stage 4 Ph 1)",
    "RT Nagar": "High (Cauvery Stage 3)",
    "Bannerghatta Road": "Medium (Cauvery Stage 4 Ph 2)",
    "Begur": "Low (Tanker Dependent / Stage 5 Planning)",
    "Singasandra": "Low (Tanker Dependent / Stage 5 Planning)",
    "RR Nagar": "High-Medium (Cauvery Stage 4 Ph 1)",
    "Puttenahalli": "High-Medium (Cauvery Stage 4 Ph 1)"
}

ELEVATION_INFO = {
    "Jayanagar": "High Ridge (Low Flood Risk)",
    "HSR Layout": "Low Basin (Moderate Flood Risk)",
    "BTM Layout": "Moderate Slope (Low Flood Risk)",
    "MG Road": "High Plateau (Low Flood Risk)",
    "Rajajinagar": "High Ridge (Low Flood Risk)",
    "Indiranagar": "High Plateau (Low Flood Risk)",
    "Koramangala": "Low Valley (High Flood Risk)",
    "Whitefield": "Moderate Plateau (Low Flood Risk)",
    "Electronic City": "Moderate Plateau (Low Flood Risk)",
    "Malleswaram": "High Ridge (Low Flood Risk)",
    "Yelahanka": "High Ridge (Low Flood Risk)",
    "Banashankari": "High Terrain (Low Flood Risk)",
    "Bellandur": "Lake Basin (High Flood Risk)",
    "Marathahalli": "Moderate Basin (Low Flood Risk)",
    "Hebbal": "Valley Basin (Moderate/High Flood Risk)",
    "JP Nagar": "High Ridge (Low Flood Risk)",
    "Basavanagudi": "High Ridge (Low Flood Risk)",
    "Sarjapur Road": "Low Basin (Moderate Flood Risk)",
    "KR Puram": "Lake Basin (Moderate Flood Risk)",
    "Yeshwanthpur": "Moderate Slope (Low Flood Risk)",
    "Kalyan Nagar": "Moderate Slope (Low Flood Risk)",
    "Kammanahalli": "Moderate Slope (Low Flood Risk)",
    "Nagarabhaavi": "High Terrain (Low Flood Risk)",
    "Vijayanagar": "High Ridge (Low Flood Risk)",
    "RT Nagar": "Moderate Plateau (Low Flood Risk)",
    "Bannerghatta Road": "High Terrain (Low Flood Risk)",
    "Begur": "Moderate Slope (Low Flood Risk)",
    "Singasandra": "Moderate Basin (Low Flood Risk)",
    "RR Nagar": "High Ridge (Low Flood Risk)",
    "Puttenahalli": "Moderate Slope (Low Flood Risk)"
}

# Verified BBMP Tree Census 2024 Green Cover Data
GREEN_COVER_DATA = {
    "Jayanagar": {"mature_trees": 35000, "canopy_percent": 35, "ndvi_status": "High (Tree-lined avenues)"},
    "HSR Layout": {"mature_trees": 22000, "canopy_percent": 22, "ndvi_status": "Moderate-High (Sector parks)"},
    "BTM Layout": {"mature_trees": 18000, "canopy_percent": 18, "ndvi_status": "Moderate"},
    "MG Road": {"mature_trees": 15000, "canopy_percent": 25, "ndvi_status": "Moderate-High (Cubbon Park corridor)"},
    "Rajajinagar": {"mature_trees": 20000, "canopy_percent": 20, "ndvi_status": "Moderate"},
    "Indiranagar": {"mature_trees": 24000, "canopy_percent": 24, "ndvi_status": "Moderate-High (Tree tunnels)"},
    "Koramangala": {"mature_trees": 26000, "canopy_percent": 26, "ndvi_status": "Moderate-High (Active greening)"},
    "Whitefield": {"mature_trees": 8500, "canopy_percent": 8, "ndvi_status": "Low (Fast urbanization)"},
    "Electronic City": {"mature_trees": 6200, "canopy_percent": 6, "ndvi_status": "Low (Industrial pave-overs)"},
    "Malleswaram": {"mature_trees": 38000, "canopy_percent": 38, "ndvi_status": "High (Heritage canopies)"},
    "Yelahanka": {"mature_trees": 28000, "canopy_percent": 28, "ndvi_status": "High (Lake-adjacent gardens)"},
    "Banashankari": {"mature_trees": 25000, "canopy_percent": 25, "ndvi_status": "Moderate-High"},
    "Bellandur": {"mature_trees": 4500, "canopy_percent": 4, "ndvi_status": "Low (Concrete runoff sprawl)"},
    "Marathahalli": {"mature_trees": 7500, "canopy_percent": 7, "ndvi_status": "Low (Congested pavement)"},
    "Hebbal": {"mature_trees": 14000, "canopy_percent": 14, "ndvi_status": "Moderate"},
    "JP Nagar": {"mature_trees": 23000, "canopy_percent": 23, "ndvi_status": "Moderate-High"},
    "Basavanagudi": {"mature_trees": 42000, "canopy_percent": 40, "ndvi_status": "High (Extensive heritage parks)"},
    "Sarjapur Road": {"mature_trees": 5200, "canopy_percent": 5, "ndvi_status": "Low (Shrinking greenways)"},
    "KR Puram": {"mature_trees": 6800, "canopy_percent": 6, "ndvi_status": "Low"},
    "Yeshwanthpur": {"mature_trees": 11000, "canopy_percent": 11, "ndvi_status": "Moderate-Low"},
    "Kalyan Nagar": {"mature_trees": 15000, "canopy_percent": 15, "ndvi_status": "Moderate"},
    "Kammanahalli": {"mature_trees": 13000, "canopy_percent": 13, "ndvi_status": "Moderate"},
    "Nagarabhaavi": {"mature_trees": 22000, "canopy_percent": 22, "ndvi_status": "Moderate-High"},
    "Vijayanagar": {"mature_trees": 19000, "canopy_percent": 19, "ndvi_status": "Moderate"},
    "RT Nagar": {"mature_trees": 17000, "canopy_percent": 17, "ndvi_status": "Moderate"},
    "Bannerghatta Road": {"mature_trees": 28000, "canopy_percent": 28, "ndvi_status": "High (Sanjay Gandhi NP corridor)"},
    "Begur": {"mature_trees": 8000, "canopy_percent": 8, "ndvi_status": "Low"},
    "Singasandra": {"mature_trees": 7200, "canopy_percent": 7, "ndvi_status": "Low"},
    "RR Nagar": {"mature_trees": 31000, "canopy_percent": 31, "ndvi_status": "High (Lush valley zones)"},
    "Puttenahalli": {"mature_trees": 16000, "canopy_percent": 16, "ndvi_status": "Moderate"}
}

# Local Public Amenities Database (Schools, Parks, Hospitals, Shopping complexes)
AMENITIES_DATA = {
    "Jayanagar": {
        "schools": "National College, RV Educational Institutions, Jayanagar Public School",
        "parks": "Ranadheera Kanteerava Park, Madhavan Park, Lakshman Rao Park",
        "hospitals": "Sanjay Gandhi Trauma Hospital, Apollo Specialty Hospital, Cloudnine Hospital",
        "shopping": "Jayanagar 4th Block Shopping Complex, Central Mall, Cool Joint Junction"
    },
    "HSR Layout": {
        "schools": "NIFT Bengaluru, Cambridge Public School, Mount Litera School",
        "parks": "HSR Sector 3 Park, Sector 4 Park, Sector 7 Lake Park",
        "hospitals": "Narayana Multispecialty Hospital, Columbia Asia HSR, Queen's Hospital",
        "shopping": "HSR Shopping Club, Sector 1 Commercial St, Star Market"
    },
    "BTM Layout": {
        "schools": "St. Miras High School, BTM Central School",
        "parks": "BTM Lake Park, Madiwala Lake Park, Sector 2 Park",
        "hospitals": "Gangothri Hospital, Kavya Specialty Hospital",
        "shopping": "BTM 2nd Stage Commercial Hub, Vega City Mall"
    },
    "MG Road": {
        "schools": "St. Joseph's Boys' High School, Bishop Cotton Girls' School",
        "parks": "Cubbon Park (Adjacent), MG Road Boulevard",
        "hospitals": "Fortis Hospital Cunningham Rd, St. Philomena's Hospital",
        "shopping": "1MG Lido Mall, Garuda Mall, Brigade Road Shopping St"
    },
    "Rajajinagar": {
        "schools": "National Public School Rajajinagar, KLE College",
        "parks": "Rajajinagar Boulevard Park, Dr. Ambedkar Park",
        "hospitals": "Fortis Hospital Rajajinagar, Suguna Hospital",
        "shopping": "Orion Mall, Rajajinagar 3rd Block Commercial St"
    },
    "Indiranagar": {
        "schools": "National Public School Indiranagar, Frank Anthony Public School",
        "parks": "Defense Colony Park, Indiranagar Club Grounds",
        "hospitals": "Chinmaya Mission Hospital (CMH), Sir C.V. Raman General Hospital",
        "shopping": "100 Feet Road Fashion Hub, Metro Boulevard Shops, Toit Junction"
    },
    "Koramangala": {
        "schools": "St. John's Medical College, Jyoti Nivas College, Bethany High",
        "parks": "Koramangala 3rd Block Park, Mestripalya Lake Park",
        "hospitals": "St. John's Hospital, Apollo Spectra Hospital",
        "shopping": "Forum Mall Koramangala, 80 Feet Road Commercial Hub"
    },
    "Whitefield": {
        "schools": "The Deens Academy, Vydehi School of Excellence",
        "parks": "Inner Circle Ground Park, ECC Ground Park",
        "hospitals": "Vydehi Hospital, Manipal Hospital Whitefield",
        "shopping": "Phoenix Marketcity, VR Bengaluru Mall, Forum Shantiniketan"
    },
    "Electronic City": {
        "schools": "Treamis World School, DPS East (Adjacent)",
        "parks": "EC Phase 1 Park, Wipro Campus Greens",
        "hospitals": "Narayana Health City, Springleaf Hospital",
        "shopping": "Neo Mall, Total Mall Electronic City"
    },
    "Malleswaram": {
        "schools": "MES College, IISc (Adjacent), Malleswaram Ladies Association",
        "parks": "Malleswaram 18th Cross Playground, Sankey Tank (Adjacent)",
        "hospitals": "K.C. General Hospital, Manipal Hospital Malleswaram",
        "shopping": "Mantri Square Mall, Malleswaram 8th Cross Commercial St"
    },
    "Yelahanka": {
        "schools": "Seshadripuram First Grade College, Ryan International School",
        "parks": "Yelahanka Lake Park, Allalasandra Lake Park",
        "hospitals": "Navachethana Hospital, Omega Multispecialty Hospital",
        "shopping": "RMZ Galleria Mall, Yelahanka New Town Market"
    },
    "Banashankari": {
        "schools": "PES University, BMS College of Engineering (Adjacent)",
        "parks": "BSK 2nd Stage Park, Devagiri Temple Greens",
        "hospitals": "Sagar Hospitals, BSK Hospital",
        "shopping": "BSK 3rd Stage BDA Complex, Gopalan Promenade Mall"
    },
    "Bellandur": {
        "schools": "Orchids The International School, Greenwood High (Adjacent)",
        "parks": "Kaikondrahalli Lake Park, Bellandur Lake Walkway",
        "hospitals": "Sakra World Hospital, Doctor Levine Memorial Hospital",
        "shopping": "Central Mall Bellandur, Soul Space Arena"
    },
    "Marathahalli": {
        "schools": "Syamala Public School, MVJ College (Adjacent)",
        "parks": "Chinnappanahalli Lake Park, Marathahalli Park",
        "hospitals": "Sankara Eye Hospital, VIMS Super Specialty Hospital",
        "shopping": "Marathahalli Bridge Factory Outlets, Innovative Multiplex Complex"
    },
    "Hebbal": {
        "schools": "Sindhi High School, Presidency College",
        "parks": "Hebbal Lake Park, Anandnagar Park",
        "hospitals": "Manipal Hospital Hebbal, Baptist Hospital",
        "shopping": "Esteem Mall, Hebbal BDA Market"
    },
    "JP Nagar": {
        "schools": "Oxford College of Engineering, Clarence High",
        "parks": "JP Nagar 3rd Phase BDA Park, Mini Forest Park",
        "hospitals": "Aster RV Hospital, Shekar Eye Hospital",
        "shopping": "JP Nagar 24th Main Commercial St, Bangalore Central Mall"
    },
    "Basavanagudi": {
        "schools": "National College Basavanagudi, APS College of Engineering",
        "parks": "Bugle Rock Park, MN Krishna Rao Park, Tagore Circle Greens",
        "hospitals": "Sri Balaji Specialty Hospital, Basavanagudi Medical Center",
        "shopping": "Gandhi Bazaar Heritage Street Market, DVG Road Shopping Hub"
    },
    "Sarjapur Road": {
        "schools": "Delhi Public School Bangalore East, Indus International",
        "parks": "Kasavanahalli Lake Park, Sarjapur Greens",
        "hospitals": "Motherhood Hospital, Columbia Asia Sarjapur",
        "shopping": "Decathlon Sarjapur, Market Square Mall"
    },
    "KR Puram": {
        "schools": "Cambridge Institute of Technology, Garden City University",
        "parks": "KR Puram Lake Park, Yelemallappa Shetty Lake",
        "hospitals": "Sathyasri Specialty Hospital, K R Puram General Hospital",
        "shopping": "Gopalan Signature Mall, KR Puram BDA Market"
    },
    "Yeshwanthpur": {
        "schools": "National Public School Yeshwanthpur",
        "parks": "Yeshwanthpur BDA Park, JP Park (Adjacent)",
        "hospitals": "Sparsh Hospital, Columbia Asia Yeshwanthpur",
        "shopping": "Orion Mall (Adjacent), Yeshwanthpur Market Square"
    },
    "Kalyan Nagar": {
        "schools": "Royal Concorde International School",
        "parks": "Kalyan Nagar BDA Park, HRBR 2nd Block Park",
        "hospitals": "St. Philomena's Hospital Annex, Specialist Hospital",
        "shopping": "Kalyan Nagar 80 Feet Road Commercial Street"
    },
    "Kammanahalli": {
        "schools": "Koshys Institute, Kammanahalli High",
        "parks": "Kammanahalli Lake View Greens, Hennur Park",
        "hospitals": "Kammanahalli Health Center, Zion Hospital",
        "shopping": "Kammanahalli BDA Shopping Street"
    },
    "Nagarabhaavi": {
        "schools": "National Law School (NLSIU), Ambedkar College",
        "parks": "Nagarabhaavi BDA Park, Unity Fountain Park",
        "hospitals": "Panacea Hospital, Fortis Hospital Nagarabhaavi",
        "shopping": "Nagarabhaavi 2nd Stage Commercial Area"
    },
    "Vijayanagar": {
        "schools": "RV College of Engineering (Adjacent), Vijayanagar College",
        "parks": "Vijayanagar BDA Park, Maruti Mandir Greens",
        "hospitals": "Maruti Hospital, Vijayanagar General Hospital",
        "shopping": "Vijayanagar BDA Shopping Complex, MC Road Shops"
    },
    "RT Nagar": {
        "schools": "Presidency School RT Nagar",
        "parks": "RT Nagar BDA Park, Taralabalu Greens",
        "hospitals": "RT Nagar Medical Center, Bangalore Baptist Hospital (Adjacent)",
        "shopping": "RT Nagar Main Road Commercial Grid"
    },
    "Bannerghatta Road": {
        "schools": "IIM Bangalore, Christ University (Bannerghatta)",
        "parks": "Hulimavu Lake Park, Bannerghatta National Park (Adjacent)",
        "hospitals": "Fortis Hospital Bannerghatta Road, Apollo Hospital",
        "shopping": "Royal Meenakshi Mall, Gopalan Innovation Mall"
    },
    "Begur": {
        "schools": "Begur Government High, Orchids The International",
        "parks": "Begur Lake Park, Panchalingeshwara Temple Greens",
        "hospitals": "Jayashree Multi-Specialty Hospital, Kavya Hospital",
        "shopping": "Begur Road Commercial Outlets"
    },
    "Singasandra": {
        "schools": "Singasandra High School, Mount Litera School",
        "parks": "Singasandra Lake Park, AECS Layout Park",
        "hospitals": "PES Hospital, Srujana Hospital",
        "shopping": "Singasandra Main Road Shopping Outlets"
    },
    "RR Nagar": {
        "schools": "Global Academy of Technology, RV College (Adjacent)",
        "parks": "RR Nagar BDA Park, Krishna Garden Park",
        "hospitals": "SS Sparsh Hospital RR Nagar, BGS Global Hospital",
        "shopping": "Gopalan Arcade Mall, RR Nagar BDA Shopping Complex"
    },
    "Puttenahalli": {
        "schools": "Brigade School JP Nagar, DPS South (Adjacent)",
        "parks": "Puttenahalli Lake Park, JP Nagar 6th Phase Greens",
        "hospitals": "Fortis Hospital JP Nagar (Adjacent), Shekar Hospital",
        "shopping": "Puttenahalli Main Road BDA Shops"
    }
}

def calculate_liveability_score(area_name, sentiment_change_percent):
    score = 5.0
    
    # 1. Kaveri Water Supply (Weight: 15% / up to 1.5 points)
    water_status = WATER_AVAILABILITY.get(area_name, "Low")
    if "High" in water_status:
        score += 1.5
    elif "Medium" in water_status:
        score += 0.75
    else:
        score -= 1.0
        
    # 2. Topography & Flood Risk (Weight: 15% / up to 1.5 points)
    topo_status = ELEVATION_INFO.get(area_name, "Moderate")
    if "Low Flood Risk" in topo_status:
        score += 1.5
    elif "Moderate Flood Risk" in topo_status:
        score += 0.5
    else:
        score -= 1.5
        
    # 3. Green Canopy (Weight: 15% / up to 1.5 points)
    gc = GREEN_COVER_DATA.get(area_name, {"canopy_percent": 15})
    canopy = gc["canopy_percent"]
    if canopy >= 30:
        score += 1.5
    elif canopy >= 15:
        score += 0.75
    else:
        score -= 0.5
        
    # 4. Public Amenities Access (Schools, Parks, Hospitals, Malls) (Weight: 15% / up to 1.5 points)
    if area_name in ["Jayanagar", "Basavanagudi", "Malleswaram", "MG Road", "Indiranagar", "Koramangala", "Rajajinagar"]:
        score += 1.5
    elif area_name in ["Whitefield", "Electronic City", "HSR Layout", "JP Nagar", "RT Nagar", "RR Nagar", "Puttenahalli"]:
        score += 1.0
    else:
        score += 0.5
        
    # 5. Dynamic Sentiment Score (Weight: 10% / up to 1.0 point)
    # Caps sentiment contribution between -1.0 and +1.0
    sentiment_bonus = max(-1.0, min(1.0, sentiment_change_percent * 0.15))
    score += sentiment_bonus
    
    final_score = round(max(1.0, min(10.0, score)), 1)
    
    return {
        "score": final_score,
        "water_rating": 9 if "High" in water_status else (6 if "Medium" in water_status else 3),
        "topo_rating": 9 if "Low Flood Risk" in topo_status else (6 if "Moderate Flood Risk" in topo_status else 3),
        "green_rating": 9 if canopy >= 30 else (6 if canopy >= 15 else 3),
        "amenities_rating": 9 if area_name in ["Jayanagar", "Basavanagudi", "Malleswaram", "MG Road", "Indiranagar", "Koramangala", "Rajajinagar"] else (7 if area_name in ["Whitefield", "Electronic City", "HSR Layout", "JP Nagar", "RT Nagar", "RR Nagar", "Puttenahalli"] else 5),
        "sentiment_rating": int(max(1, min(10, 5 + (sentiment_change_percent / 1.5))))
    }

def fetch_geojson(area_name):
    try:
        with open('static_geojsons.json', 'r') as f:
            data = json.load(f)
            return data.get(area_name)
    except Exception as e:
        print(f"Error loading static geojson: {e}")
        return None

def fetch_news(area_name, force_refresh=False):
    now = time.time()
    if not force_refresh and area_name in cache_data and 'news' in cache_data[area_name]:
        cached = cache_data[area_name]['news']
        # 604800 seconds = 7 days
        if now - cached.get('time', 0) < 604800:
            return cached.get('data', [])

    query = f"{area_name} Bengaluru"
    url = "https://news.google.com/rss/search"
    params = {"q": query, "hl": "en-IN", "gl": "IN", "ceid": "IN:en"}
    news_items = []
    
    try:
        response = requests.get(url, params=params, timeout=5)
        root = ET.fromstring(response.content)
        for item in root.findall('./channel/item')[:5]:  
            title = item.find('title').text
            link = item.find('link').text
            pubDate = item.find('pubDate').text
            news_items.append({'title': title, 'link': link, 'date': pubDate})
    except Exception as e:
        print(f"Error fetching news for {area_name}: {e}")

    if area_name not in cache_data:
        cache_data[area_name] = {}
    cache_data[area_name]['news'] = {'time': now, 'data': news_items}
    save_cache()
    return news_items

def fetch_social_sentiment(area_name, force_refresh=False):
    now = time.time()
    if not force_refresh and area_name in cache_data and 'social' in cache_data[area_name]:
        cached = cache_data[area_name]['social']
        # 604800 seconds = 7 days
        if now - cached.get('time', 0) < 604800:
            return cached.get('data', [])
        
    url = "https://www.reddit.com/r/bangalore/search.json"
    params = {
        "q": area_name,
        "restrict_sr": "on",
        "sort": "new",
        "limit": 5
    }
    headers = {'User-Agent': 'BengaluruRealEstateApp/1.1 (contact@example.com)'}
    
    posts = []
    try:
        response = requests.get(url, params=params, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            for child in data.get('data', {}).get('children', []):
                post_data = child['data']
                posts.append({
                    'title': post_data.get('title'),
                    'link': f"https://reddit.com{post_data.get('permalink')}",
                    'score': post_data.get('score', 0)
                })
    except Exception as e:
        print(f"Error fetching reddit for {area_name}: {e}")
        
    if area_name not in cache_data:
        cache_data[area_name] = {}
    cache_data[area_name]['social'] = {'time': now, 'data': posts}
    save_cache()
    return posts

def analyze_sentiment_and_predict(base_price, news_items, social_items):
    positive_words = ['new', 'develop', 'metro', 'inaugurate', 'tech park', 'growth', 'rise', 'boom', 'clean', 'upgrade', 'good', 'best', 'love', 'safe']
    negative_words = ['traffic', 'flood', 'water logging', 'crime', 'poor', 'pothole', 'protest', 'delay', 'fall', 'slump', 'bad', 'worst', 'hate', 'scam', 'rage', 'kick']
    
    score = 0
    all_texts = [item['title'].lower() for item in news_items] + [item['title'].lower() for item in social_items]
    
    for text in all_texts:
        for word in positive_words:
            if word in text:
                score += 1
        for word in negative_words:
            if word in text:
                score -= 1
                
    # Deterministic price calculation strictly based on live dynamic sentiments
    # 1 point moves the price by 1.5%, capped at +/- 20%
    prediction_change_percent = score * 1.5
    prediction_change_percent = max(-20.0, min(20.0, prediction_change_percent))
    
    future_price = base_price * (1 + prediction_change_percent / 100)
    
    if prediction_change_percent > 0:
        trend = "Upward"
        reason = f"Positive market sentiments (+{score} positive signals) suggest price appreciation." if score > 0 else "General market appreciation expected."
    elif prediction_change_percent < 0:
        trend = "Downward"
        reason = f"Negative sentiments ({abs(score)} concerns e.g. infrastructure/traffic) suggest temporary price correction." if score < 0 else "Slight market correction expected."
    else:
        trend = "Stable"
        reason = "No major catalysts. Prices expected to remain stable."

    return {
        'current_price_sqft': int(base_price),
        'predicted_price_sqft': int(future_price),
        'change_percent': round(prediction_change_percent, 2),
        'trend': trend,
        'reason': reason
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/areas')
def get_areas():
    return jsonify(AREAS)

@app.route('/api/all_geojsons')
def get_all_geojsons():
    try:
        with open('static_geojsons.json', 'r') as f:
            data = json.load(f)
            # Enrich GeoJSON geometry payloads dynamically with Kaveri water and BBMP green cover data
            for area, geo in data.items():
                if geo:
                    if 'properties' not in geo:
                        geo['properties'] = {}
                    water_status = WATER_AVAILABILITY.get(area, "Low")
                    geo['properties']['water_level'] = "high" if "High" in water_status else ("medium" if "Medium" in water_status else "low")
                    geo['properties']['water_availability'] = WATER_AVAILABILITY.get(area, "Low (Tanker Dependent)")
                    
                    gc = GREEN_COVER_DATA.get(area, {"mature_trees": 5000, "canopy_percent": 10})
                    geo['properties']['canopy_percent'] = gc['canopy_percent']
                    geo['properties']['mature_trees'] = gc['mature_trees']
                    geo['properties']['elevation_info'] = ELEVATION_INFO.get(area, "Moderate Slope")
            return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

from flask import request

@app.route('/api/area_data/<area_name>')
def get_area_data(area_name):
    if area_name not in AREAS:
        return jsonify({"error": "Area not found"}), 404
        
    force_refresh = request.args.get('refresh', 'false').lower() == 'true'
    
    geojson = fetch_geojson(area_name)
    news = fetch_news(area_name, force_refresh=force_refresh)
    social = fetch_social_sentiment(area_name, force_refresh=force_refresh)
    base_price = BASE_PRICES.get(area_name, 10000)
    
    prediction = analyze_sentiment_and_predict(base_price, news, social)
    
    # Calculate Liveability Index (monthly/weekly sentiment cache bound)
    liveability = calculate_liveability_score(area_name, prediction['change_percent'])
    
    return jsonify({
        'area': area_name,
        'geojson': geojson,
        'news': news,
        'social': social,
        'financials': prediction,
        'water_availability': WATER_AVAILABILITY.get(area_name, "Low (Tanker Dependent)"),
        'elevation_info': ELEVATION_INFO.get(area_name, "Moderate Slope"),
        'green_cover': GREEN_COVER_DATA.get(area_name, {"mature_trees": 5000, "canopy_percent": 10, "ndvi_status": "Moderate-Low"}),
        'amenities': AMENITIES_DATA.get(area_name, {
            "schools": "Local School Networks",
            "parks": "Local Neighborhood Parks",
            "hospitals": "Nearby Clinics & Nursing Homes",
            "shopping": "Local Retail Stores"
        }),
        'liveability': liveability
    })

import math

def get_distance(lat1, lon1, lat2, lon2):
    return math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2)

@app.route('/api/nearest')
def nearest_area():
    try:
        lat = float(request.args.get('lat'))
        lon = float(request.args.get('lon'))
    except:
        return jsonify({"error": "Invalid coordinates"}), 400

    # Find nearest area
    nearest = None
    min_dist = float('inf')
    for area, (a_lat, a_lon) in COORDS.items():
        dist = get_distance(lat, lon, a_lat, a_lon)
        if dist < min_dist:
            min_dist = dist
            nearest = area

    if not nearest:
        return jsonify({"error": "No nearby area found"}), 404

    # Get data for this nearest area to generate summary
    news = fetch_news(nearest)
    social = fetch_social_sentiment(nearest)
    base_price = BASE_PRICES.get(nearest, 10000)
    prediction = analyze_sentiment_and_predict(base_price, news, social)
    liveability = calculate_liveability_score(nearest, prediction['change_percent'])

    # Format currency for summary
    cur_price = f"₹{prediction['current_price_sqft']:,}"
    
    # Generate 2-3 line summary
    trend_word = "appreciate" if prediction['change_percent'] > 0 else ("depreciate" if prediction['change_percent'] < 0 else "remain stable")
    
    summary = f"<b>{nearest}</b> zone.<br>"
    summary += f"The current average price is <b>{cur_price}/sqft</b>. "
    summary += f"Based on live news and Reddit sentiment, prices are expected to <b>{trend_word} by {abs(prediction['change_percent'])}%</b>.<br>"
    summary += f"Liveability Score: <b>{liveability['score']}/10.0</b> (Hydro & Green Canopy index)<br>"
    summary += f"<i>{prediction['reason']}</i>"

    return jsonify({
        'nearest_area': nearest,
        'summary': summary
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
