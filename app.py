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

PRICE_DATA_DATE = "25 Nov 2026"
# Per area: the two portal apartment figures exactly as read from each page (asking prices), and the
# plot listings that passed the checks described in the About page. Nothing here is averaged.
PRICE_DATA = {'Jayanagar': {'zone': 'South',
               'mb': {'value': 14028,
                      'period': 'Q3 2026',
                      'page_updated': 'Oct-2026',
                      'url': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Jayanagar-in-Bangalore'},
               'sy': {'value': 19850,
                      'page_date': 'Nov 2026',
                      'url': 'https://www.squareyards.com/property-rates/jayanagar-bangalore',
                      'headline_all_types': 18900},
               'land_listings': [{'url': 'https://www.squareyards.com/resale-1200-sq-ft-plot-in-jayanagar/10624955',
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
                'mb': {'value': 9486,
                       'period': 'Q3 2026',
                       'page_updated': 'Oct-2026',
                       'url': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-HSR-Layout-in-Bangalore'},
                'sy': {'value': 17638,
                       'page_date': 'Nov 2026',
                       'url': 'https://www.squareyards.com/property-rates/hsr-layout-bangalore',
                       'headline_all_types': 17638},
                'land_listings': [{'url': 'https://www.squareyards.com/resale-1200-sq-ft-plot-in-hsr-layout/10664851',
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
                'mb': {'value': 10550,
                       'period': 'Q3 2026',
                       'page_updated': 'Oct-2026',
                       'url': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Btm-Layout-in-Bangalore'},
                'sy': {'value': 14150,
                       'page_date': 'Nov 2026',
                       'url': 'https://www.squareyards.com/property-rates/btm-layout-bangalore',
                       'headline_all_types': 13850},
                'land_listings': [{'url': 'https://www.squareyards.com/resale-1200-sq-ft-plot-in-btm-layout/9318622',
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
             'mb': {'value': 16222,
                    'period': 'Q3 2026',
                    'page_updated': 'Oct-2026',
                    'url': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Mahatma-Gandhi-Road-in-Bangalore'},
             'sy': {'value': 20100,
                    'page_date': 'Nov 2026',
                    'url': 'https://www.squareyards.com/property-rates/mg-road-bangalore',
                    'headline_all_types': 20100},
             'land_listings': []},
 'Rajajinagar': {'zone': 'West',
                 'mb': {'value': 23414,
                        'period': 'Q3 2026',
                        'page_updated': 'Oct-2026',
                        'url': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Rajajinagar-in-Bangalore'},
                 'sy': {'value': 13714,
                        'page_date': 'Nov 2026',
                        'url': 'https://www.squareyards.com/property-rates/rajajinagar-bangalore',
                        'headline_all_types': 13714},
                 'land_listings': []},
 'Indiranagar': {'zone': 'Central',
                 'mb': {'value': 18753,
                        'period': 'Q3 2026',
                        'page_updated': 'Oct-2026',
                        'url': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Indiranagar-in-Bangalore'},
                 'sy': {'value': 18750,
                        'page_date': 'Nov 2026',
                        'url': 'https://www.squareyards.com/property-rates/indiranagar-bangalore',
                        'headline_all_types': 18750},
                 'land_listings': [{'url': 'https://www.squareyards.com/resale-8000-sq-ft-plot-in-indiranagar/10469142',
                                    'psf': 62500,
                                    'plot_sqft': 8000,
                                    'locality': 'Indiranagar, Central Bangalore, Indiranagar'}]},
 'Koramangala': {'zone': 'South',
                 'mb': {'value': 15253,
                        'period': 'Q3 2026',
                        'page_updated': 'Oct-2026',
                        'url': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Koramangala-in-Bangalore'},
                 'sy': {'value': 18750,
                        'page_date': 'Nov 2026',
                        'url': 'https://www.squareyards.com/property-rates/koramangala-bangalore',
                        'headline_all_types': 18750},
                 'land_listings': [{'url': 'https://www.squareyards.com/resale-1800-sq-ft-plot-in-koramangala/10786732',
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
                'mb': {'value': 13394,
                       'period': 'Q3 2026',
                       'page_updated': 'Oct-2026',
                       'url': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Whitefield-in-Bangalore'},
                'sy': {'value': 14500,
                       'page_date': 'Nov 2026',
                       'url': 'https://www.squareyards.com/property-rates/whitefield-bangalore',
                       'headline_all_types': 14500},
                'land_listings': [{'url': 'https://www.squareyards.com/resale-1500-sq-ft-plot-in-whitefield/10346998',
                                   'psf': 2699,
                                   'plot_sqft': 1500,
                                   'locality': 'Whitefield'}]},
 'Electronic City': {'zone': 'South',
                     'mb': {'value': 8732,
                            'period': 'Q3 2026',
                            'page_updated': 'Oct-2026',
                            'url': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Electronic-City-in-Bangalore'},
                     'sy': {'value': 9350,
                            'page_date': 'Nov 2026',
                            'url': 'https://www.squareyards.com/property-rates/electronic-city-bangalore',
                            'headline_all_types': 9300},
                     'land_listings': [{'url': 'https://www.squareyards.com/resale-1200-sq-ft-plot-in-electronic-city-phase-i/9723984',
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
 'Malleshwaram': {'zone': 'Central',
                  'mb': {'value': 15218,
                         'period': 'Q3 2026',
                         'page_updated': 'Oct-2026',
                         'url': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Malleshwaram-in-Bangalore'},
                  'land_listings': [{'url': 'https://www.squareyards.com/resale-3420-sq-ft-plot-in-abhishek-apartments-malleshwaram/10429331',
                                     'psf': 30994,
                                     'plot_sqft': 3420,
                                     'locality': 'Abhishek Apartments Malleshwaram, Malleswaram'}]},
 'Yelahanka': {'zone': 'North',
               'mb': {'value': 10164,
                      'period': 'Q3 2026',
                      'page_updated': 'Oct-2026',
                      'url': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Yelahanka-in-Bangalore'},
               'sy': {'value': 10100,
                      'page_date': 'Nov 2026',
                      'url': 'https://www.squareyards.com/property-rates/yelahanka-bangalore',
                      'headline_all_types': 10100},
               'land_listings': [{'url': 'https://www.squareyards.com/resale-1200-sq-ft-plot-in-yelahanka/10326754',
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
                  'mb': {'value': 11120,
                         'period': 'Q3 2026',
                         'page_updated': 'Oct-2026',
                         'url': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Banashankari-in-Bangalore'},
                  'sy': {'value': 13500,
                         'page_date': 'Nov 2026',
                         'url': 'https://www.squareyards.com/property-rates/banashankari-bangalore',
                         'headline_all_types': 13450},
                  'land_listings': [{'url': 'https://www.squareyards.com/resale-1200-sq-ft-plot-in-banashankari-6th-stage/9800531',
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
               'mb': {'value': 15521,
                      'period': 'Q3 2026',
                      'page_updated': 'Oct-2026',
                      'url': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Bellandur-in-Bangalore'},
               'sy': {'value': 16050,
                      'page_date': 'Nov 2026',
                      'url': 'https://www.squareyards.com/property-rates/bellandur-bangalore',
                      'headline_all_types': 16050},
               'land_listings': []},
 'Marathahalli': {'zone': 'East',
                  'mb': {'value': 8192,
                         'period': 'Q3 2026',
                         'page_updated': 'Oct-2026',
                         'url': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Marathahalli-in-Bangalore'},
                  'sy': {'value': 17050,
                         'page_date': 'Nov 2026',
                         'url': 'https://www.squareyards.com/property-rates/marathahalli-bangalore',
                         'headline_all_types': 15300},
                  'land_listings': []},
 'Hebbal': {'zone': 'North',
            'mb': {'value': 16103,
                   'period': 'Q3 2026',
                   'page_updated': 'Oct-2026',
                   'url': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Hebbal-in-Bangalore'},
            'sy': {'value': 17350,
                   'page_date': 'Nov 2026',
                   'url': 'https://www.squareyards.com/property-rates/hebbal-bangalore',
                   'headline_all_types': 17100},
            'land_listings': [{'url': 'https://www.squareyards.com/resale-1200-sq-ft-plot-in-hebbal/10608342',
                               'psf': 7500,
                               'plot_sqft': 1200,
                               'locality': 'Hebbal, Central Bangalore, Hebbal'},
                              {'url': 'https://www.squareyards.com/resale-1200-sq-ft-plot-in-hebbal/9464516',
                               'psf': 3938,
                               'plot_sqft': 1200,
                               'locality': 'Ready For Construction, Hebbal'},
                              {'url': 'https://www.squareyards.com/resale-1200-sq-ft-plot-in-hebbal/9834193',
                               'psf': 25000,
                               'plot_sqft': 1200,
                               'locality': 'Hebbal'},
                              {'url': 'https://www.squareyards.com/resale-1300-sq-ft-plot-in-hebbal/10667910',
                               'psf': 8462,
                               'plot_sqft': 1300,
                               'locality': 'Hebbal'},
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
              'mb': {'value': 9919,
                     'period': 'Q3 2026',
                     'page_updated': 'Oct-2026',
                     'url': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Jp-Nagar-in-Bangalore'},
              'sy': {'value': 11900,
                     'page_date': 'Nov 2026',
                     'url': 'https://www.squareyards.com/property-rates/jp-nagar-bangalore',
                     'headline_all_types': 11350},
              'land_listings': [{'url': 'https://www.squareyards.com/resale-1200-sq-ft-plot-in-jp-nagar/10525866',
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
                  'mb': {'value': 14913,
                         'period': 'Q3 2026',
                         'page_updated': 'Oct-2026',
                         'url': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Basavanagudi-in-Bangalore'},
                  'sy': {'value': 16100,
                         'page_date': 'Nov 2026',
                         'url': 'https://www.squareyards.com/property-rates/basavanagudi-bangalore',
                         'headline_all_types': 16500},
                  'land_listings': [{'url': 'https://www.squareyards.com/resale-1201-sq-ft-plot-in-basavanagudi/10391588',
                                     'psf': 3250,
                                     'plot_sqft': 1201,
                                     'locality': 'Basavanagudi'},
                                    {'url': 'https://www.squareyards.com/resale-2400-sq-ft-plot-in-basavanagudi/10796240',
                                     'psf': 42000,
                                     'plot_sqft': 2400,
                                     'locality': 'Basavanagudi, Basavanagudi'}]},
 'Sarjapur Road': {'zone': 'East',
                   'mb': {'value': 11978,
                          'period': 'Q3 2026',
                          'page_updated': 'Oct-2026',
                          'url': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Sarjapur-Road-in-Bangalore'},
                   'sy': {'value': 12200,
                          'page_date': 'Nov 2026',
                          'url': 'https://www.squareyards.com/property-rates/sarjapur-road-bangalore',
                          'headline_all_types': 12250},
                   'land_listings': [{'url': 'https://www.squareyards.com/resale-1499-sq-ft-plot-in-sarjapur-road/9548179',
                                      'psf': 4536,
                                      'plot_sqft': 1499,
                                      'locality': 'Sarjapur Road'}]},
 'KR Puram': {'zone': 'East',
              'mb': {'value': 10543,
                     'period': 'Q3 2026',
                     'page_updated': 'Oct-2026',
                     'url': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Kr-Puram-in-Bangalore'},
              'sy': {'value': 11500,
                     'page_date': 'Nov 2026',
                     'url': 'https://www.squareyards.com/property-rates/kr-puram-bangalore',
                     'headline_all_types': 11450},
              'land_listings': [{'url': 'https://www.squareyards.com/resale-1200-sq-ft-plot-in-kr-puram/9704509',
                                 'psf': 1132,
                                 'plot_sqft': 1200,
                                 'locality': 'Villa Plots Are Available, Kr Puram'},
                                {'url': 'https://www.squareyards.com/resale-1200-sq-ft-plot-in-kr-puram/9705010',
                                 'psf': 2083,
                                 'plot_sqft': 1200,
                                 'locality': 'Maa Plots, Kr Puram'}]},
 'Yeshwanthpur': {'zone': 'North',
                  'mb': {'value': 12908,
                         'period': 'Q3 2026',
                         'page_updated': 'Oct-2026',
                         'url': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Yeswanthpur-in-Bangalore'},
                  'sy': {'value': 12200,
                         'page_date': 'Nov 2026',
                         'url': 'https://www.squareyards.com/property-rates/yeshwanthpur-bangalore',
                         'headline_all_types': 12900},
                  'land_listings': [{'url': 'https://www.squareyards.com/resale-1500-sq-ft-plot-in-yeshwanthpur/10642017',
                                     'psf': 4500,
                                     'plot_sqft': 1500,
                                     'locality': 'Yeshwanthpur'}]},
 'Kalyan Nagar': {'zone': 'North',
                  'mb': {'value': 9255,
                         'period': 'Q3 2026',
                         'page_updated': 'Oct-2026',
                         'url': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Kalyan-Nagar-in-Bangalore'},
                  'sy': {'value': 7900,
                         'page_date': 'Nov 2026',
                         'url': 'https://www.squareyards.com/property-rates/kalyan-nagar-bangalore',
                         'headline_all_types': 7900},
                  'land_listings': [{'url': 'https://www.squareyards.com/resale-2000-sq-ft-plot-in-kalyan-nagar/10637229',
                                     'psf': 18000,
                                     'plot_sqft': 2000,
                                     'locality': 'Kalyan Nagar, Central Bangalore, Kalyan Nagar'}]},
 'Kammanahalli': {'zone': 'North',
                  'mb': {'value': 17122,
                         'period': 'Q3 2026',
                         'page_updated': 'Oct-2026',
                         'url': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Kammanahalli-in-Bangalore'},
                  'sy': {'value': 19550,
                         'page_date': 'Nov 2026',
                         'url': 'https://www.squareyards.com/property-rates/kammanahalli-bangalore',
                         'headline_all_types': 19250},
                  'land_listings': [{'url': 'https://www.squareyards.com/resale-1300-sq-ft-plot-in-kammanahalli/10637114',
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
 'Nagarbhavi': {'zone': 'West',
                'mb': {'value': 7022,
                       'period': 'Q3 2026',
                       'page_updated': 'Oct-2026',
                       'url': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Naagarabhaavi-in-Bangalore'},
                'land_listings': []},
 'Vijayanagar': {'zone': 'West',
                 'sy': {'value': 10850,
                        'page_date': 'Oct 2026',
                        'url': 'https://www.squareyards.com/property-rates/vijayanagar-bangalore',
                        'headline_all_types': 10850},
                 'land_listings': []},
 'RT Nagar': {'zone': 'North',
              'mb': {'value': 6334,
                     'period': 'Q3 2026',
                     'page_updated': 'Oct-2026',
                     'url': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-RT-Nagar-in-Bangalore'},
              'sy': {'value': 14900,
                     'page_date': 'Nov 2026',
                     'url': 'https://www.squareyards.com/property-rates/rt-nagar-bangalore',
                     'headline_all_types': 15650},
              'land_listings': [{'url': 'https://www.squareyards.com/resale-1300-sq-ft-plot-in-rt-nagar/10625124',
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
                       'mb': {'value': 9825,
                              'period': 'Q3 2026',
                              'page_updated': 'Oct-2026',
                              'url': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Bannerghatta-Main-Road-in-Bangalore'},
                       'sy': {'value': 12450,
                              'page_date': 'Nov 2026',
                              'url': 'https://www.squareyards.com/property-rates/bannerghatta-road-bangalore',
                              'headline_all_types': 12450},
                       'land_listings': [{'url': 'https://www.squareyards.com/resale-1200-sq-ft-plot-in-bannerghatta-road/10306050',
                                          'psf': 1598,
                                          'plot_sqft': 1200,
                                          'locality': 'Bannerghatta Road'}]},
 'Begur': {'zone': 'South',
           'mb': {'value': 10146,
                  'period': 'Q3 2026',
                  'page_updated': 'Oct-2026',
                  'url': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Begur-in-Bangalore'},
           'sy': {'value': 9550,
                  'page_date': 'Nov 2026',
                  'url': 'https://www.squareyards.com/property-rates/begur-bangalore',
                  'headline_all_types': 9550},
           'land_listings': [{'url': 'https://www.squareyards.com/resale-1260-sq-ft-plot-in-begur/9382504',
                              'psf': 7714,
                              'plot_sqft': 1260,
                              'locality': 'Green Valley 6, Begur'},
                             {'url': 'https://www.squareyards.com/resale-1260-sq-ft-plot-in-begur/9481467',
                              'psf': 7714,
                              'plot_sqft': 1260,
                              'locality': 'Green Valley 10, Begur'}]},
 'Singasandra': {'zone': 'South',
                 'mb': {'value': 11053,
                        'period': 'Q3 2026',
                        'page_updated': 'Oct-2026',
                        'url': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Singasandra-in-Bangalore'},
                 'sy': {'value': 11850,
                        'page_date': 'Nov 2026',
                        'url': 'https://www.squareyards.com/property-rates/singasandra-bangalore',
                        'headline_all_types': 12000},
                 'land_listings': []},
 'RR Nagar': {'zone': 'West',
              'mb': {'value': 8538,
                     'period': 'Q3 2026',
                     'page_updated': 'Oct-2026',
                     'url': 'https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Rajarajeshwari-Nagar-in-Bangalore'},
              'land_listings': []},
 'Puttenahalli': {'zone': 'South', 'land_listings': []}}

# Zone trends: Square Yards zone averages, year on year to Sep 2026, as reported by mypropertypoint.com (23 Oct 2026)
ZONE_YOY = {"Central": 5.8, "East": -1.3, "South": 3.3, "North": 2.3, "West": -1.0}
ZONE_YOY_URL = "https://mypropertypoint.com/blog/property-rates-in-bangalore-per-sq-ft-by-area-october-2026"


def apartment_view(area):
    d = PRICE_DATA.get(area, {})
    srcs = []
    for key, label, period in (('mb', 'MagicBricks, multistorey apartment average', 'Q3 2026'), ('sy', 'Square Yards, apartment average', 'Nov 2026')):
        if d.get(key):
            srcs.append({'source': label, 'value': d[key]['value'], 'period': period, 'url': d[key]['url']})
    vals = [x['value'] for x in srcs]
    if not vals:
        return {'low': None, 'high': None, 'mid': None, 'note': 'No portal figure found for this area.', 'sources': []}
    low, high = min(vals), max(vals)
    if len(vals) == 1:
        note = 'One portal only (' + srcs[0]['source'].split(',')[0] + '). Treat as indicative.'
    else:
        gap = round((high - low) / low * 100)
        if gap >= 20:
            note = 'Two portals, ' + str(gap) + ' percent apart. Both are asking prices and portal averages follow whatever is listed that quarter. No single figure is shown.'
        else:
            note = 'Two portals agree within ' + str(gap) + ' percent.'
    return {'low': low, 'high': high, 'mid': int(round((low + high) / 2)), 'note': note, 'sources': srcs}


def plot_view(area):
    ls = PRICE_DATA.get(area, {}).get('land_listings', [])
    n = len(ls)
    if n < 5:
        return {'n': n, 'shown': False, 'note': 'Only ' + str(n) + ' usable listing(s) found. Not enough to show a range.', 'listings': ls}
    vals = [l['psf'] for l in ls]
    lo, hi = min(vals), max(vals)
    note = str(n) + ' Square Yards resale plot listings, asking price per sqft. This is the range seen, not an average.'
    if hi / lo > 3:
        note += ' The spread is very wide, so no typical value can be read from it.'
    return {'n': n, 'shown': True, 'low': lo, 'high': hi, 'note': note, 'listings': ls}


BASE_PRICES = {a: (apartment_view(a)['mid'] or 0) for a in PRICE_DATA}


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

def analyze_sentiment_and_predict(area, news_items, social_items):
    """Sourced apartment and plot figures, plus the zone trend. Headlines only feed the small liveability signal."""
    d = PRICE_DATA.get(area, {})
    positive_words = ['new', 'develop', 'metro', 'inaugurate', 'tech park', 'growth', 'rise', 'boom', 'clean', 'upgrade', 'good', 'best', 'love', 'safe']
    negative_words = ['traffic', 'flood', 'water logging', 'crime', 'poor', 'pothole', 'protest', 'delay', 'fall', 'slump', 'bad', 'worst', 'hate', 'scam', 'rage', 'kick']
    score = 0
    texts = [i['title'].lower() for i in news_items] + [i['title'].lower() for i in social_items]
    for t in texts:
        for w in positive_words:
            if w in t:
                score += 1
        for w in negative_words:
            if w in t:
                score -= 1
    headline_percent = max(-20.0, min(20.0, score * 1.5))
    zone = d.get('zone', 'South')
    yoy = ZONE_YOY.get(zone, 0.0)
    return {
        'apartment': apartment_view(area),
        'plot': plot_view(area),
        'zone': zone,
        'zone_trend_percent': yoy,
        'zone_trend_note': zone + ' Bengaluru zone average over the last 12 months to Sep 2026, Square Yards figure as reported by mypropertypoint.com. It describes the whole zone, not this area, and is not a forecast for the next 12 months. No area-level trend is shown because none was found with a source.',
        'zone_trend_url': ZONE_YOY_URL,
        'change_percent': yoy,
        'headline_percent': round(headline_percent, 2),
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
            {'name': 'Apartment price per sqft', 'kind': 'sourced',
             'how': 'Shown as the two portal figures, not averaged. MagicBricks: locality "Multistorey Apartment (Average Price per sq ft)", Q3 2026, pages updated Oct 2026. Square Yards: locality apartment average, pages dated Nov 2026 (the all-property headline is not used). Both are asking prices from live listings, so they follow the listing mix. They can differ by 80 percent or more for the same area (HSR Layout, Marathahalli, Rajajinagar), and a published review of the same data names that mix as the likely cause (mypropertypoint.com, 23 Oct 2026). Nothing here says which portal is right, so the range is shown and each source is linked in the area panel. Some areas have only one portal figure and Puttenahalli has none. Compare sorts on the middle of the two figures and Find matches on the lower one, because those need one number.'},
            {'name': 'Plot price per sqft', 'kind': 'sourced',
             'how': 'Range of asking prices across Square Yards resale plot listings found in Nov 2026, with listing links in the area panel. A listing counts only if its price, plot area and total price reconcile, it is in sqft, the plot is 10,000 sqft or less, the listing page says Property Type Plot (industrial and semi-commercial plots are dropped), the page City is Bangalore, the locality name matches the area as a whole name (for example Doddakammanahalli is not Kammanahalli), the micro-area is verifiable from the listing title (listings titled only with a seller or project code are dropped), and it is not a duplicate. Nothing is removed for its price. Where fewer than 5 listings pass, the range is withheld and only the individual listings are shown. A range is shown only when 5 or more listings pass; otherwise the app says there are too few. It is a range, not an average, and the spread within an area is often very wide. Listing dates were not shown on the pages, so freshness is unknown.'},
            {'name': 'Recorded sale prices', 'kind': 'not available',
             'how': 'No recorded-sale dataset was verified for this update, so the app shows none. Everything above is asking prices.'},
            {'name': 'Past zone trend (no forecast)', 'kind': 'trend',
             'how': 'Last-12-month change in the zone average asking price (Central +5.8%, South +3.3%, North +2.3%, East -1.3%, West -1.0%, to Sep 2026), Square Yards figures as reported by mypropertypoint.com. It is a zone-level past figure, not a forecast, and not specific to the area. Forecasts are withheld because the evidence is not enough to support one.'},
            {'name': 'Kaveri water supply', 'kind': 'fixed',
             'how': 'A fixed rating per area typed into the code, which mentions BWSSB Cauvery stages. The source is not cited in the app and has not been verified. Not a live supply reading.'},
            {'name': 'Green canopy', 'kind': 'fixed',
             'how': 'Fixed tree-count and canopy percentage per area. The code labels them BBMP Tree Census figures, but that attribution is unverified. Not recalculated from satellite data.'},
            {'name': 'Terrain and flood risk', 'kind': 'fixed',
             'how': 'A fixed description of elevation and flood exposure per area. No source is cited in the app.'},
            {'name': 'Liveability score', 'kind': 'mixed',
             'how': 'Starts at 5, then adds or subtracts points for water, flood risk, green canopy and amenities (up to 1.5 each), plus up to 1 for the news heuristic. Compare and Find my area use the score without the news signal so it stays stable.'},
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
    liveability = calculate_liveability_score(area_name, prediction['headline_percent'])
    
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
    liveability = calculate_liveability_score(nearest, prediction['headline_percent'])

    # Format currency for summary
    apt = prediction['apartment']; pl = prediction['plot']
    summary = f"<b>{nearest}</b> (nearest listed area).<br>"
    if apt['low'] is None:
        summary += "Apartments: no portal figure found.<br>"
    elif apt['low'] == apt['high']:
        summary += f"Apartments: ₹{apt['low']:,}/sqft asking, one portal only.<br>"
    else:
        summary += f"Apartments: ₹{apt['low']:,} to ₹{apt['high']:,}/sqft asking (two portals disagree).<br>"
    if pl['shown']:
        summary += f"Plots: ₹{pl['low']:,} to ₹{pl['high']:,}/sqft asking across {pl['n']} listings, not an average.<br>"
    else:
        summary += "Plots: too few usable listings to show a range.<br>"
    summary += f"Zone trend, last 12 months: <b>{prediction['zone_trend_percent']:+.1f}%</b> ({prediction['zone']} zone, not specific to this area, not a forecast).<br>"
    summary += f"Liveability: <b>{liveability['score']}/10</b>. Built from fixed water, canopy and terrain ratings plus the headline signal."

    return jsonify({
        'nearest_area': nearest,
        'summary': summary
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
