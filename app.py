import os
import time
import requests
import json
import xml.etree.ElementTree as ET
from flask import Flask, render_template, jsonify
import random

app = Flask(__name__)

geo_cache = {}
news_cache = {}
social_cache = {}

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
    "Yeshwanthpur"
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
    "Yeshwanthpur": 9500
}

# Add coords for nearest neighbor calculation
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
    "Yeshwanthpur": [13.0285, 77.5409]
}

def fetch_geojson(area_name):
    try:
        with open('static_geojsons.json', 'r') as f:
            data = json.load(f)
            return data.get(area_name)
    except Exception as e:
        print(f"Error loading static geojson: {e}")
        return None

def fetch_news(area_name):
    if area_name in news_cache and time.time() - news_cache[area_name]['time'] < 3600:
        return news_cache[area_name]['data']

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

    news_cache[area_name] = {'time': time.time(), 'data': news_items}
    return news_items

def fetch_social_sentiment(area_name):
    if area_name in social_cache and time.time() - social_cache[area_name]['time'] < 3600:
        return social_cache[area_name]['data']
        
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
        
    social_cache[area_name] = {'time': time.time(), 'data': posts}
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
                
    prediction_change_percent = score * 1.5 
    prediction_change_percent += random.uniform(-1, 2)
    
    future_price = base_price * (1 + prediction_change_percent / 100)
    
    if prediction_change_percent > 0:
        trend = "Upward"
        reason = f"Positive market sentiments ({score} positive indicators) suggest price appreciation." if score > 0 else "General market appreciation expected."
    elif prediction_change_percent < 0:
        trend = "Downward"
        reason = f"Negative sentiments (e.g. infrastructure/traffic concerns) suggest temporary price correction." if score < 0 else "Slight market correction expected."
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

@app.route('/api/area_data/<area_name>')
def get_area_data(area_name):
    if area_name not in AREAS:
        return jsonify({"error": "Area not found"}), 404
        
    geojson = fetch_geojson(area_name)
    news = fetch_news(area_name)
    social = fetch_social_sentiment(area_name)
    base_price = BASE_PRICES.get(area_name, 10000)
    
    prediction = analyze_sentiment_and_predict(base_price, news, social)
    
    return jsonify({
        'area': area_name,
        'geojson': geojson,
        'news': news,
        'social': social,
        'financials': prediction
    })

import math
from flask import request

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

    # Format currency for summary
    cur_price = f"₹{prediction['current_price_sqft']:,}"
    
    # Generate 2-3 line summary
    trend_word = "appreciate" if prediction['change_percent'] > 0 else ("depreciate" if prediction['change_percent'] < 0 else "remain stable")
    
    summary = f"<b>{nearest}</b> zone.<br>"
    summary += f"The current average price is <b>{cur_price}/sqft</b>. "
    summary += f"Based on live news and Reddit sentiment, prices are expected to <b>{trend_word} by {abs(prediction['change_percent'])}%</b>.<br>"
    summary += f"<i>{prediction['reason']}</i>"

    return jsonify({
        'nearest_area': nearest,
        'summary': summary
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
