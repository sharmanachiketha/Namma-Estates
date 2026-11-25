import re
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

# ---------------------------------------------------------------------------
# Market data, fetched 25 Nov 2026. Every figure is an ASKING price from a public portal page.
# mb  = MagicBricks locality page, Multistorey Apartment average per sqft (p = period shown on page)
# sy  = Square Yards locality page, Apartment row (v = rate per sqft, chg = change % shown beside it)
# mbp = MagicBricks locality page, Residential Plot average, quoted per sq yard; v = that figure / 9 per sqft
# listings = Square Yards resale plot listings that passed the audit rules in About data
# ---------------------------------------------------------------------------
PRICE_DATA_DATE = "25 Nov 2026"
MARKET = {'Jayanagar': {'zone': 'South',
               'mb': {'v': 14028, 'p': 'Q3 2026', 'u': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Jayanagar-in-Bangalore'},
               'sy': {'v': 19850, 'chg': 5.1, 'u': 'https://www.squareyards.com/property-rates/jayanagar-bangalore'},
               'mbp': {'v': 10530,
                       'sqyd': 94769,
                       'p': 'Q3 2026',
                       'u': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Jayanagar-in-Bangalore'},
               'listings': [{'url': 'https://www.squareyards.com/resale-1200-sq-ft-plot-in-jayanagar/10624955',
                             'psf': 37500,
                             'plot_sqft': 1200,
                             'locality': 'Jayanagar, Central Bangalore, Jayanagar'},
                            {'url': 'https://www.squareyards.com/resale-1203-sq-ft-plot-in-jayanagar/10344124',
                             'psf': 2200,
                             'plot_sqft': 1203,
                             'locality': 'Jayanagar'},
                            {'url': 'https://www.squareyards.com/resale-1217-sq-ft-plot-in-jayanagar/10350339',
                             'psf': 6495,
                             'plot_sqft': 1217,
                             'locality': 'Jayanagar'},
                            {'url': 'https://www.squareyards.com/resale-2000-sq-ft-plot-in-jayanagar/10281932',
                             'psf': 45000,
                             'plot_sqft': 2000,
                             'locality': 'Jayanagar 7th Block, Jayanagar'}]},
 'HSR Layout': {'zone': 'South',
                'mb': {'v': 9486, 'p': 'Q3 2026', 'u': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-HSR-Layout-in-Bangalore'},
                'sy': {'v': 17638, 'chg': 41.5, 'u': 'https://www.squareyards.com/property-rates/hsr-layout-bangalore'},
                'mbp': {'v': 17127,
                        'sqyd': 154144,
                        'p': 'Q3 2026',
                        'u': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-HSR-Layout-in-Bangalore'},
                'listings': [{'url': 'https://www.squareyards.com/resale-1200-sq-ft-plot-in-hsr-layout/10664851',
                              'psf': 37167,
                              'plot_sqft': 1200,
                              'locality': 'Hsr Layout'},
                             {'url': 'https://www.squareyards.com/resale-1200-sq-ft-plot-in-hsr-layout/10665065',
                              'psf': 38000,
                              'plot_sqft': 1200,
                              'locality': 'Hsr Layout'},
                             {'url': 'https://www.squareyards.com/resale-1500-sq-ft-plot-in-hsr-layout/10649109',
                              'psf': 18000,
                              'plot_sqft': 1500,
                              'locality': 'Hsr Layout'},
                             {'url': 'https://www.squareyards.com/resale-2400-sq-ft-plot-in-hsr-layout-sector-2/10665014',
                              'psf': 37500,
                              'plot_sqft': 2400,
                              'locality': 'Hsr Layout Sector 2'},
                             {'url': 'https://www.squareyards.com/resale-2400-sq-ft-plot-in-hsr-layout-sector-3/10664898',
                              'psf': 37500,
                              'plot_sqft': 2400,
                              'locality': 'Hsr Layout Sector 3'},
                             {'url': 'https://www.squareyards.com/resale-2400-sq-ft-plot-in-hsr-layout/10673722',
                              'psf': 4500,
                              'plot_sqft': 2400,
                              'locality': 'Hsr Layout'},
                             {'url': 'https://www.squareyards.com/resale-3300-sq-ft-plot-in-hsr-layout/9909766',
                              'psf': 40000,
                              'plot_sqft': 3300,
                              'locality': 'Hsr Layout'},
                             {'url': 'https://www.squareyards.com/resale-3690-sq-ft-plot-in-hsr-layout/9910409',
                              'psf': 40000,
                              'plot_sqft': 3690,
                              'locality': 'Hsr Layout'},
                             {'url': 'https://www.squareyards.com/resale-3725-sq-ft-plot-in-hsr-layout/9910418',
                              'psf': 40000,
                              'plot_sqft': 3725,
                              'locality': 'Hsr Layout'},
                             {'url': 'https://www.squareyards.com/resale-4220-sq-ft-plot-in-hsr-layout/9857297',
                              'psf': 40000,
                              'plot_sqft': 4220,
                              'locality': 'Hsr Layout'},
                             {'url': 'https://www.squareyards.com/resale-4271-sq-ft-plot-in-hsr-layout/9857716',
                              'psf': 39991,
                              'plot_sqft': 4271,
                              'locality': 'Hsr Layout'},
                             {'url': 'https://www.squareyards.com/resale-4373-sq-ft-plot-in-hsr-layout/9857722',
                              'psf': 39995,
                              'plot_sqft': 4373,
                              'locality': 'Hsr Layout'}]},
 'BTM Layout': {'zone': 'South',
                'mb': {'v': 10550,
                       'p': 'Q3 2026',
                       'u': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Btm-Layout-in-Bangalore'},
                'sy': {'v': 14150, 'chg': 2.1, 'u': 'https://www.squareyards.com/property-rates/btm-layout-bangalore'},
                'mbp': {'v': 8185,
                        'sqyd': 73664,
                        'p': 'Q3 2026',
                        'u': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Btm-Layout-in-Bangalore'},
                'listings': [{'url': 'https://www.squareyards.com/resale-1200-sq-ft-plot-in-btm-layout/9318622',
                              'psf': 30000,
                              'plot_sqft': 1200,
                              'locality': 'Btm Layout'},
                             {'url': 'https://www.squareyards.com/resale-2400-sq-ft-plot-in-btm-layout-1/10524667',
                              'psf': 33750,
                              'plot_sqft': 2400,
                              'locality': 'Btm Layout 1'},
                             {'url': 'https://www.squareyards.com/resale-2400-sq-ft-plot-in-btm-layout-stage-2/10589404',
                              'psf': 32000,
                              'plot_sqft': 2400,
                              'locality': 'Btm Layout Stage 2, Btm Layout, Btm Layout Stage 2'},
                             {'url': 'https://www.squareyards.com/resale-2400-sq-ft-plot-in-btm-layout-stage-2/9890215',
                              'psf': 26000,
                              'plot_sqft': 2400,
                              'locality': 'Btm Layout Stage 2'},
                             {'url': 'https://www.squareyards.com/resale-6700-sq-ft-plot-in-btm-layout-stage-2/9541068',
                              'psf': 20000,
                              'plot_sqft': 6700,
                              'locality': 'Ashok Plot, Btm Layout Stage 2'}]},
 'MG Road': {'zone': 'Central',
             'mb': {'v': 16222,
                    'p': 'Q3 2026',
                    'u': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Mahatma-Gandhi-Road-in-Bangalore'},
             'sy': {'v': 20100, 'chg': -1.1, 'u': 'https://www.squareyards.com/property-rates/mg-road-bangalore'},
             'listings': []},
 'Rajajinagar': {'zone': 'West',
                 'mb': {'v': 23414,
                        'p': 'Q3 2026',
                        'u': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Rajajinagar-in-Bangalore'},
                 'sy': {'v': 13714, 'chg': -16.4, 'u': 'https://www.squareyards.com/property-rates/rajajinagar-bangalore'},
                 'mbp': {'v': 16735,
                         'sqyd': 150614,
                         'p': 'Q3 2026',
                         'u': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Rajajinagar-in-Bangalore'},
                 'listings': []},
 'Indiranagar': {'zone': 'Central',
                 'mb': {'v': 18753,
                        'p': 'Q3 2026',
                        'u': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Indiranagar-in-Bangalore'},
                 'sy': {'v': 18750, 'chg': 7.6, 'u': 'https://www.squareyards.com/property-rates/indiranagar-bangalore'},
                 'mbp': {'v': 13355,
                         'sqyd': 120198,
                         'p': 'Q3 2026',
                         'u': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Indiranagar-in-Bangalore'},
                 'listings': [{'url': 'https://www.squareyards.com/resale-8000-sq-ft-plot-in-indiranagar/10469142',
                               'psf': 62500,
                               'plot_sqft': 8000,
                               'locality': 'Indiranagar, Central Bangalore, Indiranagar'}]},
 'Koramangala': {'zone': 'South',
                 'mb': {'v': 15253,
                        'p': 'Q3 2026',
                        'u': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Koramangala-in-Bangalore'},
                 'sy': {'v': 18750, 'chg': -3.8, 'u': 'https://www.squareyards.com/property-rates/koramangala-bangalore'},
                 'mbp': {'v': 7695,
                         'sqyd': 69252,
                         'p': 'Q3 2026',
                         'u': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Koramangala-in-Bangalore'},
                 'listings': [{'url': 'https://www.squareyards.com/resale-1800-sq-ft-plot-in-koramangala/10786732',
                               'psf': 10278,
                               'plot_sqft': 1800,
                               'locality': 'Koramangala'},
                              {'url': 'https://www.squareyards.com/resale-2440-sq-ft-plot-in-koramangala/9866500',
                               'psf': 35984,
                               'plot_sqft': 2440,
                               'locality': 'Koramangala'},
                              {'url': 'https://www.squareyards.com/resale-2500-sq-ft-plot-in-koramangala/9868693',
                               'psf': 34000,
                               'plot_sqft': 2500,
                               'locality': 'Koramangala'},
                              {'url': 'https://www.squareyards.com/resale-3300-sq-ft-plot-in-koramangala/9972699',
                               'psf': 30303,
                               'plot_sqft': 3300,
                               'locality': 'Koramangala'},
                              {'url': 'https://www.squareyards.com/resale-3325-sq-ft-plot-in-koramangala/9996866',
                               'psf': 32000,
                               'plot_sqft': 3325,
                               'locality': 'Koramangala, Central Bangalore, Koramangala'},
                              {'url': 'https://www.squareyards.com/resale-3355-sq-ft-plot-in-koramangala/9996867',
                               'psf': 31982,
                               'plot_sqft': 3355,
                               'locality': 'Koramangala, Central Bangalore, Koramangala'},
                              {'url': 'https://www.squareyards.com/resale-3500-sq-ft-plot-in-koramangala/9894813',
                               'psf': 45714,
                               'plot_sqft': 3500,
                               'locality': 'Koramangala, Central Bangalore, Koramangala'},
                              {'url': 'https://www.squareyards.com/resale-4220-sq-ft-plot-in-koramangala/9862968',
                               'psf': 35521,
                               'plot_sqft': 4220,
                               'locality': 'Koramangala'},
                              {'url': 'https://www.squareyards.com/resale-4322-sq-ft-plot-in-koramangala/9862994',
                               'psf': 35516,
                               'plot_sqft': 4322,
                               'locality': 'Koramangala'},
                              {'url': 'https://www.squareyards.com/resale-4373-sq-ft-plot-in-koramangala/9862997',
                               'psf': 35536,
                               'plot_sqft': 4373,
                               'locality': 'Koramangala'}]},
 'Whitefield': {'zone': 'East',
                'mb': {'v': 13394,
                       'p': 'Q3 2026',
                       'u': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Whitefield-in-Bangalore'},
                'sy': {'v': 14500, 'chg': -0.7, 'u': 'https://www.squareyards.com/property-rates/whitefield-bangalore'},
                'mbp': {'v': 7512,
                        'sqyd': 67612,
                        'p': 'Q3 2026',
                        'u': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Whitefield-in-Bangalore'},
                'listings': [{'url': 'https://www.squareyards.com/resale-1500-sq-ft-plot-in-whitefield/10346998',
                              'psf': 2699,
                              'plot_sqft': 1500,
                              'locality': 'Whitefield'}]},
 'Electronic City': {'zone': 'South',
                     'mb': {'v': 8732,
                            'p': 'Q3 2026',
                            'u': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Electronic-City-in-Bangalore'},
                     'sy': {'v': 9350, 'chg': 0.6, 'u': 'https://www.squareyards.com/property-rates/electronic-city-bangalore'},
                     'mbp': {'v': 6218,
                             'sqyd': 55964,
                             'p': 'Q3 2026',
                             'u': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Electronic-City-in-Bangalore'},
                     'listings': [{'url': 'https://www.squareyards.com/resale-1200-sq-ft-plot-in-electronic-city-phase-i/9723984',
                                   'psf': 5938,
                                   'plot_sqft': 1200,
                                   'locality': 'Electronic City Phase i, Electronic City Phase I'},
                                  {'url': 'https://www.squareyards.com/resale-1200-sq-ft-plot-in-electronic-city-phase-i/9762882',
                                   'psf': 5777,
                                   'plot_sqft': 1200,
                                   'locality': 'Electronic City Phase I'},
                                  {'url': 'https://www.squareyards.com/resale-1200-sq-ft-plot-in-electronic-city-phase-ii/10093554',
                                   'psf': 4667,
                                   'plot_sqft': 1200,
                                   'locality': 'Ranjith Luxury Plots, Electronic City Phase ii'},
                                  {'url': 'https://www.squareyards.com/resale-1200-sq-ft-plot-in-electronic-city-phase-ii/10093994',
                                   'psf': 4000,
                                   'plot_sqft': 1200,
                                   'locality': 'Rj Villa Plot, Electronic City Phase ii'},
                                  {'url': 'https://www.squareyards.com/resale-1200-sq-ft-plot-in-electronic-city-phase-ii/10103620',
                                   'psf': 4558,
                                   'plot_sqft': 1200,
                                   'locality': 'Rj Premium Villa Plot, Electronic City Phase ii'},
                                  {'url': 'https://www.squareyards.com/resale-1200-sq-ft-plot-in-electronic-city-phase-ii/10110024',
                                   'psf': 4583,
                                   'plot_sqft': 1200,
                                   'locality': 'Ranjith Villa Plot, Electronic City Phase ii'},
                                  {'url': 'https://www.squareyards.com/resale-1200-sq-ft-plot-in-electronic-city/10150689',
                                   'psf': 5499,
                                   'plot_sqft': 1200,
                                   'locality': 'Electronic City, Electronic City'}]},
 'Malleswaram': {'zone': 'Central',
                 'mb': {'v': 15218,
                        'p': 'Q3 2026',
                        'u': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Malleshwaram-in-Bangalore'},
                 'sy': {'v': 13050, 'chg': -10.0, 'u': 'https://www.squareyards.com/property-rates/malleswaram-bangalore'},
                 'mbp': {'v': 10033,
                         'sqyd': 90296,
                         'p': 'Q3 2026',
                         'u': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Malleshwaram-in-Bangalore'},
                 'listings': [{'url': 'https://www.squareyards.com/resale-3420-sq-ft-plot-in-abhishek-apartments-malleshwaram/10429331',
                               'psf': 30994,
                               'plot_sqft': 3420,
                               'locality': 'Abhishek Apartments Malleshwaram, Malleswaram'}]},
 'Yelahanka': {'zone': 'North',
               'mb': {'v': 10164, 'p': 'Q3 2026', 'u': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Yelahanka-in-Bangalore'},
               'sy': {'v': 10100, 'chg': 0.7, 'u': 'https://www.squareyards.com/property-rates/yelahanka-bangalore'},
               'mbp': {'v': 8146,
                       'sqyd': 73312,
                       'p': 'Q3 2026',
                       'u': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Yelahanka-in-Bangalore'},
               'listings': [{'url': 'https://www.squareyards.com/resale-1200-sq-ft-plot-in-yelahanka/10326754',
                             'psf': 2000,
                             'plot_sqft': 1200,
                             'locality': 'Yelahanka'},
                            {'url': 'https://www.squareyards.com/resale-1200-sq-ft-plot-in-yelahanka/10595882',
                             'psf': 6167,
                             'plot_sqft': 1200,
                             'locality': 'Yelahanka, North Bangalore, Yelahanka'},
                            {'url': 'https://www.squareyards.com/resale-1200-sq-ft-plot-in-yelahanka/9464438',
                             'psf': 2898,
                             'plot_sqft': 1200,
                             'locality': 'Rera And Bmrda Approved P, Yelahanka'},
                            {'url': 'https://www.squareyards.com/resale-1200-sq-ft-plot-in-yelahanka/9465364',
                             'psf': 2876,
                             'plot_sqft': 1200,
                             'locality': 'Rera And Bmrda Approved P, Yelahanka'},
                            {'url': 'https://www.squareyards.com/resale-1200-sq-ft-plot-in-yelahanka/9465452',
                             'psf': 2906,
                             'plot_sqft': 1200,
                             'locality': 'Rera And Bmrda Approved P, Yelahanka'},
                            {'url': 'https://www.squareyards.com/resale-1500-sq-ft-plot-in-yelahanka/9840299',
                             'psf': 25000,
                             'plot_sqft': 1500,
                             'locality': 'Yelahanka'},
                            {'url': 'https://www.squareyards.com/resale-2400-sq-ft-plot-in-yelahanka/10212545',
                             'psf': 13000,
                             'plot_sqft': 2400,
                             'locality': 'A G Akshay Site, Yelahanka'},
                            {'url': 'https://www.squareyards.com/resale-880-sq-ft-plot-in-yelahanka-new-town/10602415',
                             'psf': 15909,
                             'plot_sqft': 880,
                             'locality': 'Yelahanka New Town, North Bangalore, Yelahanka New Town'}]},
 'Banashankari': {'zone': 'South',
                  'mb': {'v': 11120,
                         'p': 'Q3 2026',
                         'u': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Banashankari-in-Bangalore'},
                  'sy': {'v': 13500, 'chg': 0.4, 'u': 'https://www.squareyards.com/property-rates/banashankari-bangalore'},
                  'mbp': {'v': 12360,
                          'sqyd': 111239,
                          'p': 'Q3 2026',
                          'u': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Banashankari-in-Bangalore'},
                  'listings': [{'url': 'https://www.squareyards.com/resale-1200-sq-ft-plot-in-banashankari-6th-stage/9800531',
                                'psf': 16667,
                                'plot_sqft': 1200,
                                'locality': 'Banashankari 6th Stage'},
                               {'url': 'https://www.squareyards.com/resale-1200-sq-ft-plot-in-banashankari/9765585',
                                'psf': 12500,
                                'plot_sqft': 1200,
                                'locality': 'Star City, Banashankari'},
                               {'url': 'https://www.squareyards.com/resale-1200-sq-ft-plot-in-banashankari/9801340',
                                'psf': 12500,
                                'plot_sqft': 1200,
                                'locality': 'Vr Star Plots, Banashankari'},
                               {'url': 'https://www.squareyards.com/resale-1500-sq-ft-plot-in-banashankari/9760180',
                                'psf': 12467,
                                'plot_sqft': 1500,
                                'locality': 'Star City, Banashankari'},
                               {'url': 'https://www.squareyards.com/resale-1800-sq-ft-plot-in-banashankari-3rd-stage/10732732',
                                'psf': 14500,
                                'plot_sqft': 1800,
                                'locality': 'Banashankari 3rd Stage'},
                               {'url': 'https://www.squareyards.com/resale-1892-sq-ft-plot-in-banashankari/9984595',
                                'psf': 12474,
                                'plot_sqft': 1892,
                                'locality': 'Banashankari, Central Bangalore, Banashankari'},
                               {'url': 'https://www.squareyards.com/resale-1999-sq-ft-plot-in-banashankari/9765246',
                                'psf': 12456,
                                'plot_sqft': 1999,
                                'locality': 'Star City Plots, Banashankari'},
                               {'url': 'https://www.squareyards.com/resale-2400-sq-ft-plot-in-banashankari/9801352',
                                'psf': 12500,
                                'plot_sqft': 2400,
                                'locality': 'Star Lands, Banashankari'},
                               {'url': 'https://www.squareyards.com/resale-2400-sq-ft-plot-in-banashankari/9801375',
                                'psf': 12500,
                                'plot_sqft': 2400,
                                'locality': 'Star Plots, Banashankari'}]},
 'Bellandur': {'zone': 'East',
               'mb': {'v': 15521, 'p': 'Q3 2026', 'u': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Bellandur-in-Bangalore'},
               'sy': {'v': 16050, 'chg': 0.0, 'u': 'https://www.squareyards.com/property-rates/bellandur-bangalore'},
               'listings': []},
 'Marathahalli': {'zone': 'East',
                  'mb': {'v': 8192,
                         'p': 'Jul-Sep 2025 (older version of page)',
                         'u': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Marathahalli-in-Bangalore'},
                  'sy': {'v': 17050, 'chg': 11.4, 'u': 'https://www.squareyards.com/property-rates/marathahalli-bangalore'},
                  'mbp': {'v': 12624,
                          'sqyd': 113619,
                          'p': 'Jul-Sep 2025 (older version of page)',
                          'u': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Marathahalli-in-Bangalore'},
                  'listings': []},
 'Hebbal': {'zone': 'North',
            'mb': {'v': 16103, 'p': 'Q3 2026', 'u': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Hebbal-in-Bangalore'},
            'sy': {'v': 17350, 'chg': 1.5, 'u': 'https://www.squareyards.com/property-rates/hebbal-bangalore'},
            'mbp': {'v': 2986,
                    'sqyd': 26873,
                    'p': 'Q3 2026',
                    'u': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Hebbal-in-Bangalore'},
            'listings': [{'url': 'https://www.squareyards.com/resale-1200-sq-ft-plot-in-hebbal/10608342',
                          'psf': 7500,
                          'plot_sqft': 1200,
                          'locality': 'Hebbal, Central Bangalore, Hebbal'},
                         {'url': 'https://www.squareyards.com/resale-1200-sq-ft-plot-in-hebbal/9464516',
                          'psf': 3938,
                          'plot_sqft': 1200,
                          'locality': 'Ready For Construction, Hebbal'},
                         {'url': 'https://www.squareyards.com/resale-1200-sq-ft-plot-in-hebbal/9834193', 'psf': 25000, 'plot_sqft': 1200, 'locality': 'Hebbal'},
                         {'url': 'https://www.squareyards.com/resale-1300-sq-ft-plot-in-hebbal/10667910', 'psf': 8462, 'plot_sqft': 1300, 'locality': 'Hebbal'},
                         {'url': 'https://www.squareyards.com/resale-1350-sq-ft-plot-in-hebbal/10615063',
                          'psf': 11111,
                          'plot_sqft': 1350,
                          'locality': 'Hebbal, Central Bangalore, Hebbal'},
                         {'url': 'https://www.squareyards.com/resale-1500-sq-ft-plot-in-hebbal/10016793',
                          'psf': 26000,
                          'plot_sqft': 1500,
                          'locality': 'Hebbal'},
                         {'url': 'https://www.squareyards.com/resale-1500-sq-ft-plot-in-hebbal/10622503',
                          'psf': 22000,
                          'plot_sqft': 1500,
                          'locality': 'Hebbal, Central Bangalore, Hebbal'},
                         {'url': 'https://www.squareyards.com/resale-1600-sq-ft-plot-in-hebbal/10604850',
                          'psf': 25000,
                          'plot_sqft': 1600,
                          'locality': 'Hebbal, Central Bangalore, Hebbal'},
                         {'url': 'https://www.squareyards.com/resale-1600-sq-ft-plot-in-hebbal/10608679',
                          'psf': 22000,
                          'plot_sqft': 1600,
                          'locality': 'Hebbal, Central Bangalore, Hebbal'},
                         {'url': 'https://www.squareyards.com/resale-2000-sq-ft-plot-in-hebbal/10637323',
                          'psf': 18000,
                          'plot_sqft': 2000,
                          'locality': 'Hebbal, Central Bangalore, Hebbal'},
                         {'url': 'https://www.squareyards.com/resale-2400-sq-ft-plot-in-hebbal/10633742',
                          'psf': 17000,
                          'plot_sqft': 2400,
                          'locality': 'Hebbal, Central Bangalore, Hebbal'},
                         {'url': 'https://www.squareyards.com/resale-4000-sq-ft-plot-in-hebbal/9894543',
                          'psf': 23000,
                          'plot_sqft': 4000,
                          'locality': 'Hebbal'}]},
 'JP Nagar': {'zone': 'South',
              'mb': {'v': 9919, 'p': 'Q3 2026', 'u': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-JP-Nagar-in-Bangalore'},
              'sy': {'v': 11900, 'chg': 4.9, 'u': 'https://www.squareyards.com/property-rates/jp-nagar-bangalore'},
              'mbp': {'v': 12599,
                      'sqyd': 113388,
                      'p': 'Q3 2026',
                      'u': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-JP-Nagar-in-Bangalore'},
              'listings': [{'url': 'https://www.squareyards.com/resale-1200-sq-ft-plot-in-jp-nagar/10525866',
                            'psf': 17583,
                            'plot_sqft': 1200,
                            'locality': 'Jp Nagar 6th Phase Puttanahalli Plot, Jp Nagar'},
                           {'url': 'https://www.squareyards.com/resale-1200-sq-ft-plot-in-jp-nagar/9754219',
                            'psf': 12000,
                            'plot_sqft': 1200,
                            'locality': 'Star City, Jp Nagar'},
                           {'url': 'https://www.squareyards.com/resale-1600-sq-ft-plot-in-jp-nagar-phase-9/10120677',
                            'psf': 25000,
                            'plot_sqft': 1600,
                            'locality': 'Jp Nagar Phase 9, Jp Nagar, Jp Nagar Phase 9'},
                           {'url': 'https://www.squareyards.com/resale-2400-sq-ft-plot-in-jp-nagar-phase-7/9943553',
                            'psf': 15000,
                            'plot_sqft': 2400,
                            'locality': 'Jp Nagar Phase 7, Jp Nagar, Jp Nagar Phase 7'},
                           {'url': 'https://www.squareyards.com/resale-2400-sq-ft-plot-in-jp-nagar/10051876',
                            'psf': 22917,
                            'plot_sqft': 2400,
                            'locality': 'Jp Nagar'},
                           {'url': 'https://www.squareyards.com/resale-2400-sq-ft-plot-in-jp-nagar/10545504',
                            'psf': 22000,
                            'plot_sqft': 2400,
                            'locality': 'Jp Nagar'}]},
 'Basavanagudi': {'zone': 'Central',
                  'mb': {'v': 14913,
                         'p': 'Q3 2026',
                         'u': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Basavanagudi-in-Bangalore'},
                  'sy': {'v': 16100, 'chg': -2.5, 'u': 'https://www.squareyards.com/property-rates/basavanagudi-bangalore'},
                  'mbp': {'v': 3602,
                          'sqyd': 32418,
                          'p': 'Q3 2026',
                          'u': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Basavanagudi-in-Bangalore'},
                  'listings': [{'url': 'https://www.squareyards.com/resale-1201-sq-ft-plot-in-basavanagudi/10391588',
                                'psf': 3250,
                                'plot_sqft': 1201,
                                'locality': 'Basavanagudi'},
                               {'url': 'https://www.squareyards.com/resale-2400-sq-ft-plot-in-basavanagudi/10796240',
                                'psf': 42000,
                                'plot_sqft': 2400,
                                'locality': 'Basavanagudi, Basavanagudi'}]},
 'Sarjapur Road': {'zone': 'East',
                   'mb': {'v': 11978,
                          'p': 'Q3 2026',
                          'u': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Sarjapur-Road-in-Bangalore'},
                   'sy': {'v': 12200, 'chg': -0.6, 'u': 'https://www.squareyards.com/property-rates/sarjapur-road-bangalore'},
                   'mbp': {'v': 7968,
                           'sqyd': 71709,
                           'p': 'Q3 2026',
                           'u': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Sarjapur-Road-in-Bangalore'},
                   'listings': [{'url': 'https://www.squareyards.com/resale-1499-sq-ft-plot-in-sarjapur-road/9548179',
                                 'psf': 4536,
                                 'plot_sqft': 1499,
                                 'locality': 'Sarjapur Road'}]},
 'KR Puram': {'zone': 'East',
              'mb': {'v': 10543, 'p': 'Q3 2026', 'u': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-KR-Puram-in-Bangalore'},
              'sy': {'v': 11500, 'chg': 0.5, 'u': 'https://www.squareyards.com/property-rates/kr-puram-bangalore'},
              'mbp': {'v': 7769,
                      'sqyd': 69921,
                      'p': 'Q3 2026',
                      'u': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-KR-Puram-in-Bangalore'},
              'listings': [{'url': 'https://www.squareyards.com/resale-1200-sq-ft-plot-in-kr-puram/9704509',
                            'psf': 1132,
                            'plot_sqft': 1200,
                            'locality': 'Villa Plots Are Available, Kr Puram'},
                           {'url': 'https://www.squareyards.com/resale-1200-sq-ft-plot-in-kr-puram/9705010',
                            'psf': 2083,
                            'plot_sqft': 1200,
                            'locality': 'Maa Plots, Kr Puram'}]},
 'Yeshwanthpur': {'zone': 'North',
                  'mb': {'v': 12908,
                         'p': 'Q3 2026',
                         'u': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Yeshwanthpur-in-Bangalore'},
                  'sy': {'v': 12200, 'chg': -5.5, 'u': 'https://www.squareyards.com/property-rates/yeshwanthpur-bangalore'},
                  'listings': [{'url': 'https://www.squareyards.com/resale-1500-sq-ft-plot-in-yeshwanthpur/10642017',
                                'psf': 4500,
                                'plot_sqft': 1500,
                                'locality': 'Yeshwanthpur'}]},
 'Kalyan Nagar': {'zone': 'North',
                  'mb': {'v': 9255,
                         'p': 'Q3 2026',
                         'u': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Kalyan-Nagar-in-Bangalore'},
                  'sy': {'v': 7900, 'chg': -4.6, 'u': 'https://www.squareyards.com/property-rates/kalyan-nagar-bangalore'},
                  'mbp': {'v': 9624,
                          'sqyd': 86617,
                          'p': 'Q3 2026',
                          'u': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Kalyan-Nagar-in-Bangalore'},
                  'listings': [{'url': 'https://www.squareyards.com/resale-2000-sq-ft-plot-in-kalyan-nagar/10637229',
                                'psf': 18000,
                                'plot_sqft': 2000,
                                'locality': 'Kalyan Nagar, Central Bangalore, Kalyan Nagar'}]},
 'Kammanahalli': {'zone': 'North',
                  'mb': {'v': 17122,
                         'p': 'Q3 2026',
                         'u': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Kammanahalli-in-Bangalore'},
                  'sy': {'v': 19550, 'chg': 1.5, 'u': 'https://www.squareyards.com/property-rates/kammanahalli-bangalore'},
                  'listings': [{'url': 'https://www.squareyards.com/resale-1300-sq-ft-plot-in-kammanahalli/10637114',
                                'psf': 25000,
                                'plot_sqft': 1300,
                                'locality': 'Kammanahalli, Central Bangalore, Kammanahalli'},
                               {'url': 'https://www.squareyards.com/resale-1652-sq-ft-plot-in-kammanahalli/10222711',
                                'psf': 13983,
                                'plot_sqft': 1652,
                                'locality': 'Kammanahalli, Central Bangalore, Kammanahalli'},
                               {'url': 'https://www.squareyards.com/resale-3300-sq-ft-plot-in-nandi-homes-kammanahalli/10317972',
                                'psf': 6061,
                                'plot_sqft': 3300,
                                'locality': 'Nandi Homes Kammanahalli, Kammanahalli'},
                               {'url': 'https://www.squareyards.com/resale-880-sq-ft-plot-in-kammanahalli/10493612',
                                'psf': 12500,
                                'plot_sqft': 880,
                                'locality': 'Kammanahalli, Central Bangalore, Kammanahalli'}]},
 'Nagarabhaavi': {'zone': 'West',
                  'mb': {'v': 7022,
                         'p': 'Q3 2026',
                         'u': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Naagarabhaavi-in-Bangalore'},
                  'mbp': {'v': 9136,
                          'sqyd': 82227,
                          'p': 'Q3 2026',
                          'u': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Naagarabhaavi-in-Bangalore'},
                  'listings': []},
 'Vijayanagar': {'zone': 'West',
                 'mb': {'v': 8921,
                        'p': 'Jul-Sep 2025 (older version of page)',
                        'u': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Vijayanagar-in-Bangalore'},
                 'sy': {'v': 10850, 'chg': 0.2, 'u': 'https://www.squareyards.com/property-rates/vijayanagar-bangalore'},
                 'mbp': {'v': 13267,
                         'sqyd': 119404,
                         'p': 'Jul-Sep 2025 (older version of page)',
                         'u': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Vijayanagar-in-Bangalore'},
                 'listings': []},
 'RT Nagar': {'zone': 'North',
              'mb': {'v': 6334, 'p': 'Q3 2026', 'u': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-RT-Nagar-in-Bangalore'},
              'sy': {'v': 14900, 'chg': -4.8, 'u': 'https://www.squareyards.com/property-rates/rt-nagar-bangalore'},
              'mbp': {'v': 3379,
                      'sqyd': 30410,
                      'p': 'Q3 2026',
                      'u': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-RT-Nagar-in-Bangalore'},
              'listings': [{'url': 'https://www.squareyards.com/resale-1300-sq-ft-plot-in-rt-nagar/10625124',
                            'psf': 6923,
                            'plot_sqft': 1300,
                            'locality': 'Rt Nagar, Central Bangalore, Rt Nagar'},
                           {'url': 'https://www.squareyards.com/resale-1500-sq-ft-plot-in-rt-nagar/10631158',
                            'psf': 3000,
                            'plot_sqft': 1500,
                            'locality': 'Rt Nagar, Central Bangalore, Rt Nagar'},
                           {'url': 'https://www.squareyards.com/resale-2000-sq-ft-plot-in-rt-nagar/9893822',
                            'psf': 23000,
                            'plot_sqft': 2000,
                            'locality': 'Rt Nagar'},
                           {'url': 'https://www.squareyards.com/resale-4000-sq-ft-plot-in-rt-nagar/10631458',
                            'psf': 30000,
                            'plot_sqft': 4000,
                            'locality': 'Rt Nagar, Central Bangalore, Rt Nagar'}]},
 'Bannerghatta Road': {'zone': 'South',
                       'mb': {'v': 9825,
                              'p': 'Q3 2026',
                              'u': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Bannerghatta-Main-Road-in-Bangalore'},
                       'sy': {'v': 12450, 'chg': -3.2, 'u': 'https://www.squareyards.com/property-rates/bannerghatta-road-bangalore'},
                       'mbp': {'v': 4466,
                               'sqyd': 40193,
                               'p': 'Q3 2026',
                               'u': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Bannerghatta-Main-Road-in-Bangalore'},
                       'listings': [{'url': 'https://www.squareyards.com/resale-1200-sq-ft-plot-in-bannerghatta-road/10306050',
                                     'psf': 1598,
                                     'plot_sqft': 1200,
                                     'locality': 'Bannerghatta Road'}]},
 'Begur': {'zone': 'South',
           'mb': {'v': 10146, 'p': 'Q3 2026', 'u': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Begur-in-Bangalore'},
           'sy': {'v': 9550, 'chg': 0.4, 'u': 'https://www.squareyards.com/property-rates/begur-bangalore'},
           'mbp': {'v': 7366,
                   'sqyd': 66297,
                   'p': 'Q3 2026',
                   'u': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Begur-in-Bangalore'},
           'listings': [{'url': 'https://www.squareyards.com/resale-1260-sq-ft-plot-in-begur/9382504',
                         'psf': 7714,
                         'plot_sqft': 1260,
                         'locality': 'Green Valley 6, Begur'},
                        {'url': 'https://www.squareyards.com/resale-1260-sq-ft-plot-in-begur/9481467',
                         'psf': 7714,
                         'plot_sqft': 1260,
                         'locality': 'Green Valley 10, Begur'}]},
 'Singasandra': {'zone': 'South',
                 'mb': {'v': 11053,
                        'p': 'Q3 2026',
                        'u': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Singasandra-in-Bangalore'},
                 'sy': {'v': 11850, 'chg': -1.1, 'u': 'https://www.squareyards.com/property-rates/singasandra-bangalore'},
                 'mbp': {'v': 12503,
                         'sqyd': 112525,
                         'p': 'Q3 2026',
                         'u': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Singasandra-in-Bangalore'},
                 'listings': []},
 'RR Nagar': {'zone': 'West',
              'mb': {'v': 8538,
                     'p': 'Q3 2026',
                     'u': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Rajarajeshwari-Nagar-in-Bangalore'},
              'mbp': {'v': 11693,
                      'sqyd': 105239,
                      'p': 'Q3 2026',
                      'u': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Rajarajeshwari-Nagar-in-Bangalore'},
              'listings': []},
 'Puttenahalli': {'zone': 'South', 'listings': []}}

# Areas with no portal page of their own are estimated from the parent locality (disclosed in the app).
PROXY_PARENT = {'Puttenahalli': 'JP Nagar'}

# Past 12 months, zone average asking price (Square Yards zone figures as reported by mypropertypoint.com, 23 Oct 2026)
ZONE_YOY = {"Central": 5.8, "East": -1.3, "South": 3.3, "North": 2.3, "West": -1.0}
ZONE_YOY_URL = "https://mypropertypoint.com/blog/property-rates-in-bangalore-per-sq-ft-by-area-october-2026"

import statistics as _st


def _clamp(x, lo, hi):
    return max(lo, min(hi, x))


def apartment_view(area):
    d = MARKET.get(area, {})
    proxy = None
    if not (d.get('mb') or d.get('sy')) and area in PROXY_PARENT:
        proxy = PROXY_PARENT[area]
        d = MARKET.get(proxy, {})
    srcs = []
    if d.get('mb'):
        srcs.append({'source': 'MagicBricks, multistorey apartment average', 'value': d['mb']['v'], 'period': d['mb'].get('p') or '', 'url': d['mb']['u']})
    if d.get('sy'):
        srcs.append({'source': 'Square Yards, apartment average', 'value': d['sy']['v'], 'period': 'Nov 2026', 'url': d['sy']['u']})
    vals = [x['value'] for x in srcs]
    if not vals:
        return {'low': None, 'high': None, 'mid': None, 'est': None, 'confidence': 'none', 'method': 'none', 'spread_percent': None, 'note': 'No portal figure found for this area.', 'sources': []}
    low, high = min(vals), max(vals)
    est = int(round(sum(vals) / len(vals), -1))
    spread = round((high - low) / low * 100) if len(vals) == 2 else None
    if proxy:
        conf, method = 'low', 'proxy'
        note = 'No portal page exists for ' + area + '. This is the figure for ' + proxy + ', the locality it sits in, so it is a stand-in, not a measurement.'
    elif len(vals) == 1:
        conf, method = 'low', 'one portal'
        note = 'Estimate = the one portal figure found (' + srcs[0]['source'].split(',')[0] + '). Only one source, so treat it as indicative.'
    elif spread < 20:
        conf, method = 'high', 'two portals'
        note = 'Estimate = midpoint of two portals that agree within ' + str(spread) + ' percent.'
    elif spread < 60:
        conf, method = 'medium', 'two portals'
        note = 'Estimate = midpoint of two portals ' + str(spread) + ' percent apart. The real figure for a given flat can sit anywhere in the range.'
    else:
        conf, method = 'low', 'two portals'
        note = 'Estimate = midpoint of two portals ' + str(spread) + ' percent apart. They disagree a lot (asking averages follow whatever is listed), so use the range, not the midpoint.'
    return {'low': low, 'high': high, 'mid': est, 'est': est, 'confidence': conf, 'method': method, 'spread_percent': spread, 'proxy_of': proxy, 'note': note, 'sources': srcs}


# Sanity flag (my threshold, NOT validated): a sole MagicBricks plot average below this share of the area's own apartment rate
# looks inconsistent with it. Its cause (listing mix, unit, scope) cannot be checked from the page, so the observed figure is
# shown unchanged and a modelled estimate is offered next to it, clearly labelled.
PLOT_FLAG_VS_APT = 0.4


def _plot_obs(area):
    d = MARKET.get(area, {})
    ls = d.get('listings', [])
    obs = {}
    if len(ls) >= 3:
        vals = sorted(l['psf'] for l in ls)
        obs['sy_median'] = int(round(_st.median(vals), -2))
        obs['sy_low'], obs['sy_high'] = vals[0], vals[-1]
    if d.get('mbp'):
        obs['mb'] = d['mbp']['v']
    return obs


def _plot_direct(area):
    """(est, low, high, obs) from observed sources only, or None."""
    obs = _plot_obs(area)
    vals = [v for k, v in (('mb', obs.get('mb')), ('sy', obs.get('sy_median'))) if v]
    if not vals:
        return None
    lo, hi = min(vals), max(vals)
    est = int(round(sum(vals) / len(vals), -2))
    if len(vals) == 1 and 'sy_median' in obs:
        lo, hi = obs['sy_low'], obs['sy_high']
    return {'est': est, 'low': int(lo), 'high': int(hi), 'obs': obs, 'n_src': len(vals)}


def _plot_flagged(area):
    d = _plot_direct(area)
    apt = apartment_view(area)['est']
    if not d or not apt:
        return False
    return d['n_src'] == 1 and 'mb' in d['obs'] and 'sy_median' not in d['obs'] and d['obs']['mb'] < PLOT_FLAG_VS_APT * apt


def plot_view(area):
    d = MARKET.get(area, {})
    ls = d.get('listings', [])
    obs = _plot_obs(area)
    srcs = []
    if d.get('mbp'):
        srcs.append({'source': 'MagicBricks, residential plot average (card label Sq-Yrd: ' + format(d['mbp']['sqyd'], ',') + ' per sq yd, divided by 9)', 'value': d['mbp']['v'], 'period': d['mbp'].get('p') or '', 'url': d['mbp']['u']})
    base = {'n': len(ls), 'listings': ls, 'sources': srcs, 'observed': obs}
    direct = _plot_direct(area)
    if direct and not _plot_flagged(area):
        if direct['n_src'] == 2:
            ratio = max(obs['mb'], obs['sy_median']) / min(obs['mb'], obs['sy_median'])
            conf = 'medium' if ratio < 1.6 else 'low'
            note = 'Two sources: MagicBricks locality plot average ' + format(obs['mb'], ',') + ' and the median of ' + str(len(ls)) + ' Square Yards listings ' + format(obs['sy_median'], ',') + ' per sqft, ' + format(ratio, '.1f') + 'x apart. The estimate is just their midpoint. Nothing I checked says which is closer to the truth, so rely on the range.'
        elif 'sy_median' in obs:
            conf = 'low'
            note = 'Square Yards listings only (' + str(len(ls)) + ' listings, median ' + format(obs['sy_median'], ',') + '). Range shown is lowest to highest listing. Single source.'
        else:
            conf = 'low'
            note = 'MagicBricks locality plot average only. Single source, sample size and micro-area scope are not stated on the page.'
        base.update({'shown': True, 'est': direct['est'], 'low': direct['low'], 'high': direct['high'], 'confidence': conf, 'method': 'direct', 'note': note})
        return base
    # modelled paths
    zone = d.get('zone')
    apt = apartment_view(area)['est']
    parent = PROXY_PARENT.get(area)
    flagged_txt = ''
    if direct and _plot_flagged(area):
        flagged_txt = 'The only portal figure (MagicBricks ' + format(obs['mb'], ',') + '/sqft) is ' + str(int(100 * obs['mb'] / apt)) + '% of this area\'s apartment estimate. It is shown as observed, but looks inconsistent with it (cause cannot be checked), so a modelled estimate is given instead. '
    if parent and _plot_direct(parent) and not _plot_flagged(parent):
        p = _plot_direct(parent)
        base.update({'shown': True, 'est': p['est'], 'low': p['low'], 'high': p['high'], 'confidence': 'low', 'method': 'proxy',
                     'note': 'No portal plot figure for ' + area + '. This is the figure for ' + parent + ', the locality it sits in. A stand-in, not a measurement.'})
        return base
    ratios = []
    for a2, d2 in MARKET.items():
        if a2 == area or d2.get('zone') != zone or a2 in PROXY_PARENT:
            continue
        dd = _plot_direct(a2)
        a2v = apartment_view(a2)['est']
        if dd and a2v and not _plot_flagged(a2):
            ratios.append(dd['est'] / a2v)
    if apt and len(ratios) >= 2:
        r = _st.median(ratios)
        base.update({'shown': True, 'est': int(round(apt * r, -2)), 'low': int(round(apt * min(ratios), -2)), 'high': int(round(apt * max(ratios), -2)), 'confidence': 'low', 'method': 'modelled',
                     'note': flagged_txt + ('No plot data found for this area. ' if not flagged_txt else '') + 'MODELLED, not observed: apartment estimate times the median plot-to-apartment price ratio (' + format(r, '.2f') + ') of ' + str(len(ratios)) + ' ' + zone + ' zone areas that have plot data. Range = lowest and highest ratio in the zone. Those ratios come from the same unreconciled sources, so treat this as a rough placeholder.'})
        return base
    base.update({'shown': False, 'est': None, 'low': None, 'high': None, 'confidence': 'none', 'method': 'none', 'note': 'No plot data and no basis for an estimate.'})
    return base


BASE_PRICES = {a: (apartment_view(a)['mid'] or 0) for a in MARKET}


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

# Fixed green cover estimates per area (source unverified)
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
    if news_items or 'news' not in cache_data[area_name]:
        cache_data[area_name]['news'] = {'time': now, 'data': news_items}
    else:
        return cache_data[area_name]['news'].get('data', [])
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
                    'score': post_data.get('score', 0),
                    'fetched': now,
                    'created': post_data.get('created_utc')
                })
    except Exception as e:
        print(f"Error fetching reddit for {area_name}: {e}")
        
    if area_name not in cache_data:
        cache_data[area_name] = {}
    if posts or 'social' not in cache_data[area_name]:
        cache_data[area_name]['social'] = {'time': now, 'data': posts}
    else:
        return cache_data[area_name]['social'].get('data', [])
    save_cache()
    return posts

import email.utils as _eu

POS_TERMS = {'metro': 1.0, 'inaugurat': 1.0, 'tech park': 1.0, 'flyover': 0.5, 'new road': 0.5, 'upgrade': 1.0, 'green': 0.5, 'redevelop': 0.5, 'growth': 1.0, 'rise in': 0.5, 'boom': 1.0, 'clean': 0.5, 'safe': 0.5, 'airport': 0.5, 'lake revival': 1.0, 'rejuvenat': 1.0, 'connectivity': 0.5, 'best': 0.5}
NEG_TERMS = {'flood': 1.5, 'waterlog': 1.5, 'water logging': 1.5, 'crime': 1.0, 'murder': 1.0, 'robbery': 1.0, 'pothole': 0.75, 'protest': 0.5, 'delay': 0.75, 'traffic jam': 1.0, 'gridlock': 1.0, 'accident': 0.75, 'killed': 0.75, 'fire': 0.75, 'collapse': 1.5, 'scam': 1.0, 'water shortage': 1.5, 'tanker': 1.0, 'power cut': 0.75, 'demolition': 0.75, 'encroachment': 0.5, 'garbage': 0.75, 'sewage': 1.0, 'stink': 0.75, 'slump': 1.0, 'worst': 0.75}
AREA_TERMS = {'Malleswaram': ['malleswaram', 'malleshwaram'], 'Nagarabhaavi': ['nagarbhavi', 'nagarabhavi', 'nagarabhaavi'], 'RR Nagar': ['rr nagar', 'rajarajeshwari', 'rajarajeshwari nagar'], 'JP Nagar': ['jp nagar', 'j p nagar'], 'BTM Layout': ['btm'], 'HSR Layout': ['hsr'], 'KR Puram': ['kr puram', 'k r puram', 'krishnarajapura'], 'MG Road': ['mg road', 'mahatma gandhi road'], 'RT Nagar': ['rt nagar', 'r t nagar'], 'Bannerghatta Road': ['bannerghatta'], 'Sarjapur Road': ['sarjapur'], 'Electronic City': ['electronic city']}
MIN_FRESH_ITEMS = 3
FRESH_DAYS = 90


def _age_days(date_str):
    try:
        t = _eu.parsedate_to_datetime(date_str).timestamp()
        return (time.time() - t) / 86400.0
    except Exception:
        return None


def sentiment_signal(area, news_items, social_items):
    """Keyword-lexicon sentiment of recent, area-specific headlines. A missing signal is reported as missing, never as neutral."""
    terms = AREA_TERMS.get(area, [area.lower()])
    used, stale, offtopic = [], 0, 0
    for it in news_items:
        title = (it.get('title') or '')
        low = title.lower()
        if not any(t in low for t in terms):
            offtopic += 1
            continue
        age = _age_days(it.get('date') or '')
        if age is None or age > FRESH_DAYS:
            stale += 1
            continue
        used.append(('news', title, low))
    for it in social_items:
        title = (it.get('title') or '')
        low = title.lower()
        if not any(t in low for t in terms):
            offtopic += 1
            continue
        created = it.get('created')
        if not created or (time.time() - created) / 86400.0 > FRESH_DAYS:
            stale += 1
            continue
        used.append(('social', title, low))
    uniq, toks = [], []
    for k, t, low in used:
        core = low.rsplit(' - ', 1)[0]
        tk = set(w for w in re.findall(r'[a-z0-9]+', core) if len(w) > 3)
        if any(len(tk & o) / max(1, len(tk | o)) >= 0.4 for o in toks):
            continue  # same story as one already counted
        toks.append(tk)
        uniq.append((k, t, low))
    all_scores = []
    for k, t, low in uniq:
        sc = sum(w for term, w in POS_TERMS.items() if term in low) - sum(w for term, w in NEG_TERMS.items() if term in low)
        all_scores.append(_clamp(sc, -2.0, 2.0))
    scored = [(u, sc) for u, sc in zip(uniq, all_scores) if sc != 0]
    scores = [sc for u, sc in scored]
    uniq = [u for u, sc in scored]
    n = len(uniq)
    base = {'n_used': n, 'n_stale': stale, 'n_offtopic': offtopic, 'n_candidates': len(used), 'n_distinct_stories': len(toks), 'min_needed': MIN_FRESH_ITEMS, 'fresh_days': FRESH_DAYS,
            'items': [{'source': k, 'title': t} for k, t, low in uniq][:6]}
    if n < MIN_FRESH_ITEMS:
        base.update({'status': 'insufficient', 'net': None, 'tilt_percent': 0.0,
                     'note': 'Not enough usable signal (' + str(n) + ' distinct recent stories naming the area with a positive or negative keyword, ' + str(MIN_FRESH_ITEMS) + ' needed, newer than ' + str(FRESH_DAYS) + ' days; ' + str(len(toks)) + ' distinct stories found in total). Sentiment adds nothing to this outlook. This is missing data, not a neutral reading.'})
        return base
    net = _clamp(sum(scores) / n / 2.0, -1.0, 1.0)
    tilt = round(_clamp(net * 1.5, -1.0, 1.0), 2)
    base.update({'status': 'ok', 'net': round(net, 2), 'tilt_percent': tilt,
                 'note': str(n) + ' distinct recent stories naming the area and containing a keyword, scored. Net sentiment ' + format(net, '+.2f') + ' (scale -1 to +1), adjusting the outlook by ' + format(tilt, '+.2f') + ' points at most +/-1. Keyword scoring misses sarcasm and context, so the weight is small.'})
    return base


def outlook(area, sent):
    """Indicative 12-month outlook. Formula, not a validated forecast: no backtest has been run."""
    apt, plot = apartment_view(area), plot_view(area)
    d = MARKET.get(area, {})
    zone = d.get('zone', 'South')
    zy = ZONE_YOY.get(zone, 0.0)
    base = round(zy, 2)
    live = calculate_liveability_score(area, 0)['score']
    live_tilt = round((live - 6.0) * 0.35, 2)
    sent_tilt = sent.get('tilt_percent', 0.0)
    g = round(base + live_tilt + sent_tilt, 2)
    spread = apt.get('spread_percent') or 0
    half = _clamp(3.0 + 0.1 * spread + (2.0 if apt.get('method') in ('one portal', 'proxy') else 0.0), 3.0, 12.0)
    def proj(est, extra):
        if not est:
            return None
        h = half * extra
        return {'now': est, 'projected': int(round(est * (1 + g / 100), -1)), 'low': int(round(est * (1 + (g - h) / 100), -1)), 'high': int(round(est * (1 + (g + h) / 100), -1)), 'half_width': round(h, 1)}
    conf = 'low' if (apt.get('confidence') in ('low', 'none') or sent.get('status') != 'ok') else 'medium'
    return {
        'change_percent': g,
        'apartment': proj(apt.get('est'), 1.0),
        'plot': proj(plot.get('est'), 1.6),
        'components': {
            'zone_trend': {'value': zy, 'note': zone + ' zone, last 12 months'},
            'baseline': {'value': base, 'note': 'zone trend only. Area-level change figures were dropped because their period is unclear (one portal page labels the same number both annual and quarterly)'},
            'liveability': {'value': live_tilt, 'score': live, 'note': 'liveability score ' + str(live) + ' vs a neutral 6.0, 0.35 points per score point. The score is built from FIXED ratings typed into the code (water, flood risk, canopy and a 3-tier amenities list), not live measurements'},
            'sentiment': {'value': sent_tilt, 'status': sent.get('status')},
        },
        'confidence': conf,
        'disclaimer': 'Indicative scenario from a fixed formula (zone past trend + liveability + news/social tilt). It has not been backtested, so there is no measured accuracy. The band is a sensitivity range based on my judgement of source disagreement. It is not a statistical prediction interval and has not been calibrated.',
    }


def analyze_sentiment_and_predict(area, news_items, social_items):
    d = MARKET.get(area, {})
    sent = sentiment_signal(area, news_items, social_items)
    ol = outlook(area, sent)
    zone = d.get('zone', 'South')
    return {
        'apartment': apartment_view(area),
        'plot': plot_view(area),
        'zone': zone,
        'zone_trend_percent': ZONE_YOY.get(zone, 0.0),
        'zone_trend_note': zone + ' Bengaluru zone average over the last 12 months to Sep 2026, Square Yards figure as reported by mypropertypoint.com. It describes the whole zone, not this area.',
        'zone_trend_url': ZONE_YOY_URL,
        'change_percent': ol['change_percent'],
        'outlook': ol,
        'sentiment': sent,
        'data_date': PRICE_DATA_DATE,
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
            try:
                with open('boundary_provenance.json', 'r') as pf:
                    provenance = json.load(pf)
            except Exception:
                provenance = {}
            for area in AREAS:
                if area not in data:
                    data[area] = {'properties': {}}  # no outline (e.g. Electronic City): keep its fixed properties for the heatmaps
            for area, geo in data.items():
                if geo:
                    if 'properties' not in geo:
                        geo['properties'] = {}
                    geo['properties']['outline'] = provenance.get(area, {'outline_source': 'unknown', 'approximate': True, 'wards': []})
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

@app.route('/api/summary')
def get_summary():
    """One compact row per area, used by Compare and Find my area."""
    rows = []
    for area in AREAS:
        water = WATER_AVAILABILITY.get(area, "Low (Tanker Dependent)")
        topo = ELEVATION_INFO.get(area, "Moderate")
        gc = GREEN_COVER_DATA.get(area, {"mature_trees": 5000, "canopy_percent": 10})
        live = calculate_liveability_score(area, 0)
        lat, lon = COORDS.get(area, (None, None))
        rows.append({
            'area': area,
            'lat': lat, 'lon': lon,
            'price_sqft': apartment_view(area)['mid'],
            'apt_est': apartment_view(area)['est'],
            'apt_conf': apartment_view(area)['confidence'],
            'apt_method': apartment_view(area)['method'],
            'outlook_percent': outlook(area, {'tilt_percent': 0.0, 'status': 'not_loaded'})['change_percent'],
            'apt_low': apartment_view(area)['low'],
            'apt_high': apartment_view(area)['high'],
            'plot': {k: v for k, v in plot_view(area).items() if k != 'listings'},
            'liveability': live['score'],
            'water': water,
            'water_level': 2 if "High" in water and "Medium" not in water else (1 if ("Medium" in water or "High" in water) else 0),
            'canopy_percent': gc['canopy_percent'],
            'mature_trees': gc.get('mature_trees'),
            'terrain': topo,
            'flood_risk': "Low" if "Low Flood Risk" in topo else ("Moderate" if "Moderate Flood Risk" in topo else "High"),
            'amenities_rating': live.get('amenities_rating'),
        })
    return jsonify(rows)


@app.route('/api/methodology')
def get_methodology():
    """Plain description of what each number is and how fresh it is."""
    newest = None
    oldest = None
    for entry in cache_data.values():
        for kind in ('news', 'social'):
            t = (entry.get(kind) or {}).get('time')
            if t:
                newest = t if newest is None else max(newest, t)
                oldest = t if oldest is None else min(oldest, t)
    def iso(t):
        return time.strftime('%d %b %Y', time.gmtime(t)) if t else None
    return jsonify({
        'news_cache_newest': iso(newest),
        'news_cache_note': 'Dates come from this server cache.',
        'news_cache_oldest': iso(oldest),
        'metrics': [
            {'name': 'Apartment price per sqft (estimate)', 'kind': 'sourced estimate',
             'how': 'Two public asking-price series per area: MagicBricks locality "Multistorey Apartment (Average Price per sq ft)", Q3 2026, pages updated Oct 2026 (Marathahalli and Vijayanagar pages showed Jul-Sep 2025 data when read, so those two MagicBricks figures are older), and the Square Yards locality apartment average, pages dated Nov 2026. The estimate is the midpoint of the two, always shown next to the full range and a confidence label: high if the portals agree within 20 percent, medium within 60, low if further apart or if only one portal has the area. Portals disagree because asking averages follow whatever is listed that quarter, so the midpoint is a summary, not a measured price. Nagarabhaavi and RR Nagar have only a MagicBricks figure. Puttenahalli has no portal page and uses its parent locality JP Nagar, labelled as a stand-in. All are asking prices, not registered sale prices.'},
            {'name': 'Plot price per sqft (estimate)', 'kind': 'sourced or modelled estimate',
             'how': 'Observed sources: (1) MagicBricks locality page, card "Residential Plot (Average Price Rs/Sq-Yrd)", Q3 2026 (Marathahalli and Vijayanagar pages showed Jul-Sep 2025). The figure is divided by 9 to get per sqft. The unit label is the card label; one page summary sentence (Indiranagar) prints the same number as per sqft, so the unit rests on the card label and on plausibility. The pages do not state the sample size or micro-area scope. (2) The median of audited Square Yards resale plot listings where 3 or more passed (rules: plain Plot type, city Bangalore, locality matches as a whole name, price/area/total reconcile, sqft, 10,000 sqft or less, no duplicates, micro-area verifiable from the title; nothing removed for price). The two sources can be several times apart and I found no evidence about which is closer, so with both the estimate is only their midpoint and the range between them is the real information. With one source the estimate is that source. Where a sole MagicBricks figure is below 40 percent of the area apartment rate (a threshold I chose, not validated) it is shown as observed but flagged, and a MODELLED estimate is offered: apartment estimate times the median plot-to-apartment ratio of same-zone areas with plot data. MG Road, Bellandur, Yeshwanthpur and Basavanagudi are modelled this way; Puttenahalli borrows JP Nagar. Modelled values are placeholders, not measurements. Listing dates are not shown on the pages.'},
            {'name': 'Recorded sale prices', 'kind': 'not available',
             'how': 'No recorded-sale dataset (for example Karnataka registration data) was verified for this update, so the app shows none. Everything above is asking prices.'},
            {'name': '12-month outlook', 'kind': 'indicative formula',
             'how': 'Outlook % = zone trend + liveability tilt + sentiment tilt. Zone trend: last-12-month change of the zone average asking price, Square Yards zone figures as reported by mypropertypoint.com on 23 Oct 2026 (that article says "+5.8% in a year" for Central and lists the others without a period; I did not open the Square Yards zone page itself, so the period for the other zones is assumed). Area-level change percentages from Square Yards area pages are NOT used because their period is unclear: the same page labels one number both annual and QoQ. Liveability tilt = (liveability score - 6) x 0.35 points. The liveability score rests on fixed ratings typed into the code for water, flood risk, canopy and a 3-tier amenities list (not measured counts), so this input is an assumption. Sentiment tilt: see next item. The projected price is the estimate times (1 + outlook). The low-high figures are a sensitivity band whose width grows with source disagreement and single-source data; it is my judgement, not a calibrated or statistical prediction interval. No backtest has been run, so no accuracy is claimed. Compare and Find show the baseline outlook without live sentiment; the area panel adds sentiment when enough fresh items exist.'},
            {'name': 'News and social sentiment', 'kind': 'live signal, often missing',
             'how': 'Google News RSS headlines and r/bangalore search results for the area. An item counts only if its title names the area and it is under 90 days old by its own timestamp (news pubDate, reddit created time). Items without a timestamp are dropped. De-duplicated, then scored with a keyword list (metro, flood, water logging, crime and similar, each weighted). At least 3 usable items are needed. Below that the status is insufficient and sentiment adds exactly 0: no data, not a neutral reading. With enough items the tilt is net sentiment x 1.5 points, capped at +/-1. Keyword scoring misses context and sarcasm, so the weight is small. The reddit feed may be blocked from the server, in which case only news is used. Past cached posts without a creation time are treated as stale.'},
            {'name': 'Kaveri water supply', 'kind': 'fixed',
             'how': 'A fixed rating per area typed into the code, which mentions BWSSB Cauvery stages. The source is not cited in the app and has not been verified. Not a live supply reading.'},
            {'name': 'Green canopy', 'kind': 'fixed',
             'how': 'Fixed tree-count and canopy percentage per area. The code labels them BBMP Tree Census figures, but that attribution is unverified. Not recalculated from satellite data.'},
            {'name': 'Terrain and flood risk', 'kind': 'fixed',
             'how': 'A fixed description of elevation and flood exposure per area. No source is cited in the app.'},
            {'name': 'Liveability score', 'kind': 'mixed',
             'how': 'Starts at 5, then adds or subtracts points for water (up to 1.5), flood risk (1.5), green canopy (1.5), amenities (1.5) and the news signal (up to 1). All of the first four are FIXED assumptions typed into the code, not measurements: water, flood and canopy are per-area ratings with no verified source, and amenities is a hard-coded 3-tier list of areas (central areas 1.5, a middle group 1.0, everything else 0.5) with no counts of schools, hospitals or parks behind it. Only the news signal is live, and only when enough fresh headlines exist. Compare and Find use the score without the news signal.'},
            {'name': 'Area outlines on the map', 'kind': 'derived',
             'how': 'Each outline is built by merging the official Greater Bengaluru Authority ward polygons (369 wards, 2025, published on OpenCity) that match the area. Wards were chosen by name match, OpenStreetMap place points inside the ward, and the area pin. Hover an area to see its wards. These are ward-based approximations, not official locality limits. HSR Layout uses its OpenStreetMap suburb outline. Electronic City is outside the ward map, so it is a pin only.'},
        ]
    })


@app.route('/api/area_data/<area_name>')
def get_area_data(area_name):
    if area_name not in AREAS:
        return jsonify({"error": "Area not found"}), 404
        
    force_refresh = request.args.get('refresh', 'false').lower() == 'true'
    
    geojson = fetch_geojson(area_name)
    news = fetch_news(area_name, force_refresh=force_refresh)
    social = fetch_social_sentiment(area_name, force_refresh=force_refresh)
        
    prediction = analyze_sentiment_and_predict(area_name, news, social)
    
    # Calculate Liveability Index (monthly/weekly sentiment cache bound)
    liveability = calculate_liveability_score(area_name, (prediction['sentiment']['net'] or 0) * 7 if prediction['sentiment']['status'] == 'ok' else 0)
    
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
        'liveability': liveability,
        'headlines_fetched': (lambda t: time.strftime('%d %b %Y', time.gmtime(t)) if t else None)(cache_data.get(area_name, {}).get('news', {}).get('time'))
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
    prediction = analyze_sentiment_and_predict(nearest, news, social)
    liveability = calculate_liveability_score(nearest, (prediction['sentiment']['net'] or 0) * 7 if prediction['sentiment']['status'] == 'ok' else 0)

    apt = prediction['apartment']; pl = prediction['plot']; ol = prediction['outlook']
    summary = f"<b>{nearest}</b> (nearest listed area).<br>"
    if apt['est'] is None:
        summary += "Apartments: no portal figure found.<br>"
    else:
        summary += f"Apartments: about ₹{apt['est']:,}/sqft asking (portal range ₹{apt['low']:,} to ₹{apt['high']:,}, {apt['confidence']} confidence).<br>"
    if pl['est']:
        summary += f"Plots: about ₹{pl['est']:,}/sqft asking (range ₹{pl['low']:,} to ₹{pl['high']:,}, {pl['confidence']} confidence, {pl['method']}).<br>"
    summary += f"12-month outlook: <b>{ol['change_percent']:+.1f}%</b> indicative (formula, not validated, {ol['confidence']} confidence).<br>"
    summary += f"Liveability: <b>{liveability['score']}/10</b>."

    return jsonify({
        'nearest_area': nearest,
        'summary': summary
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
