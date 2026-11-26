# Namma Estates

An interactive map of 30 Bengaluru residential localities with asking-price estimates for apartments and plots, a liveability score, and an indicative 12-month price outlook.

Live site: https://namma-estates.onrender.com/
Stack: Python (Flask) backend, Leaflet front end, deployed on Render.

## What the app shows

Four views in the sidebar:

- **Explore**: click an area on the map to open its panel with prices, outlook, liveability, water supply, greenery, flood risk, amenity counts and the headlines behind the sentiment signal.
- **Compare**: up to three areas side by side, best value in each row highlighted.
- **Find my area**: set a max apartment price, minimum liveability, water supply, greenery and low-flood-risk filters. Matching areas light up on the map and the rest fade. Areas where only one of the two portals fits the budget are listed separately as partial matches.
- **About data**: the methodology, fetched live from `/api/methodology`.

The detailed calculation and sources for each area sit behind a collapsed "How this is calculated" dropdown, so the price, confidence and outlook stay visible without scrolling.

## How the numbers are produced

### Apartment price estimate

- Inputs: the MagicBricks locality "Multistorey Apartment (Average Price per sq ft)" and the Square Yards locality apartment average. Both are asking-price series, not registered sales.
- Estimate: midpoint of the two portal figures, always shown with the full range and a confidence label (high if the portals agree within 20%, medium within 60%, low beyond that or when only one portal has the area).
- Nagarabhaavi and RR Nagar have only a MagicBricks figure. Puttenahalli has no portal page and uses JP Nagar as a labelled stand-in.
- Freshness: MagicBricks pages show Q3 2026 and were updated Oct 2026, except the Marathahalli and Vijayanagar pages, which still showed Jul-Sep 2025 data when read. Square Yards pages are dated Nov 2026. Price data date: 25 Nov 2026.

### Plot price estimate

- Inputs: Square Yards asking-price resale plot listings. Each listing passes an audit: plain Plot type, city Bangalore, locality matches as a whole name, price/area/total reconcile, area in sqft, 10,000 sqft or less, no duplicates, micro-area verifiable from the title. Nothing is removed for being cheap or dear.
- 3 or more listings: estimate = median, range = lowest to highest. 1 or 2 listings: shown as a very thin sample. Listings show prices that exist, not what is typical.
- MagicBricks plot averages are displayed for reference only. The card says "per Sq-Yrd" while a summary sentence says "per sqft" for the same number, and nothing found settles the unit, so those figures feed no estimate, ratio or training set.
- Areas with no listings get a MODELLED placeholder: apartment estimate times the median plot-to-apartment ratio of the areas with 3 or more listings, range = middle half of those ratios. Currently 8 areas. Puttenahalli uses JP Nagar (proxy). Modelled and proxy figures are labelled in the UI.
- Current split: 21 direct, 8 modelled, 1 proxy.

### 12-month baseline change

- Where Knight Frank published a micro-market figure (India Real Estate H1 2026 report, table "Residential price movement in select locations", 12-month change to H1 2026), that is used: KR Puram +20%, Yelahanka +18%, Marathahalli +15%, Whitefield +14%, Malleswaram +13%, Hebbal +11%, Electronic City +10%, Yeshwanthpur +9%, Rajajinagar +9%, Bannerghatta Road +7%, Sarjapur Road +3%.
- Everywhere else: the city-wide ANAROCK Q3 2026 figure of +8% in the year (Bengaluru average ₹9,600/sqft). Knight Frank's city figures are +9% (H1 2026) and +11% (Q3 2026, which it says partly reflects dearer stock entering its sample), so city reports differ.
- Assumption: the past 12-month change repeats. That is a scenario, not a measured trend.

### Liveability score (1-10)

Starts at 5, then adds or subtracts:

- Water supply: +1.5 / +0.75 / -1.0. Fixed per-area rating that mentions BWSSB Cauvery stages; the source is not cited and is unverified.
- Flood risk from terrain: +1.5 / +0.5 / -1.5. Fixed rating, no source cited.
- Tree canopy: +1.5 / +0.75 / -0.5. Fixed figures labelled BBMP Tree Census; the attribution is unverified.
- Amenities: +0.5 to +1.5. Measured, see below.
- Sentiment: up to +/-1.0 when enough fresh items exist, see below.

Clamped to 1-10.

### Amenities (measured)

Counts of OpenStreetMap point features within 1.5 km of each area's centre point: schools, colleges and kindergartens; hospitals, clinics and doctors; supermarkets, malls and department stores; bus stops and metro stations. Source: Geofabrik southern-zone extract dated 24 Nov 2026. Converted to a score by percentile rank across the 30 areas on a log scale. Only features mapped as single points are counted, so these are undercounts and uneven by area; parks are excluded from the score for that reason. The centre point is a typed coordinate, not the area outline.

### Bus connectivity (Compare row)

For each area centre point, the number of BMTC bus stops and distinct bus route numbers within 1.5 km, from the Bengaluru bus GTFS feed (valid 9 Nov 2026 to 9 Nov 2027). A route number is the first word of the feed route name, so variants like `104` and `104 KBS-IIHS` count once. Built by `build_bus_connectivity.py` into `bus_connectivity.json`. It counts which stops and routes exist. It makes no timetable, frequency or waiting-time claim: the upstream project warns its source app has inaccurate timetables and stop timings. It is not used in the liveability score or the outlook. Centre points near big bus hubs (for example MG Road) count very high, and a count does not show how useful the routes are. Congestion data from the same publisher is not used (reuse terms unverified).

### News and social sentiment

Google News RSS headlines and r/bangalore search results per area, cached server-side for 7 days. An item counts only if its title names the area and its own timestamp is under 90 days old; untimestamped items are dropped. Items are de-duplicated into distinct stories and scored with a weighted keyword lexicon (metro, flood, water logging, crime and similar). At least 3 usable distinct stories are required; below that the status is "insufficient" and sentiment adds exactly 0: missing data, not a neutral reading. With enough items, tilt = net sentiment x 1.5 points, capped at +/-1. As of 25 Nov 2026, only Hebbal and KR Puram had enough fresh items; this changes as news arrives.

### 12-month outlook

`outlook % = baseline + liveability tilt + sentiment tilt`

- Liveability tilt = (score - 6.0) x 0.35.
- Projected price = estimate x (1 + outlook/100).
- The low-high band is a sensitivity range: half-width = clamp(3 + 0.1 x portal-spread% + 2 for single-source or proxy areas, 3, 12), wider for plots (x1.6). It is a judgement about source disagreement, not a statistical prediction interval. No backtest has been run, so no accuracy is claimed.
- Compare and Find show the baseline outlook without live sentiment; the area panel adds sentiment when enough fresh items exist, so the two can differ for the same area by design.

### Map outlines

Each outline merges the official Greater Bengaluru Authority ward polygons (369 wards, 2025 delimitation, published on OpenCity under "Other (Public Domain)") that match the area. Wards were chosen by name matches, OpenStreetMap place points inside each ward and the area pin (see `build_boundaries.py`, `members.json`, `boundary_provenance.json`). These are ward-based approximations, not official locality limits. HSR Layout uses its OpenStreetMap suburb outline (ODbL). Electronic City is outside the ward map and shows as a pin only. Base map tiles: OpenStreetMap, with OpenTopoMap available as an overlay.

## Data sources and dates

| Data | Source | Date | Used for |
| --- | --- | --- | --- |
| Apartment asking averages | [MagicBricks locality pages](https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Btm-Layout-in-Bangalore) (representative page; every area's URL is in `app.py` and in the app's sources dropdown) | Q3 2026 (pages updated Oct 2026; Marathahalli and Vijayanagar Jul-Sep 2025) | Apartment estimate |
| Apartment asking averages | [Square Yards locality pages](https://www.squareyards.com/property-rates/btm-layout-bangalore) (representative page) | Nov 2026 | Apartment estimate |
| Plot asking listings | [Square Yards resale plot listings](https://www.squareyards.com/resale-1200-sq-ft-plot-in-btm-layout/9318622) (representative listing; all listing URLs are in `app.py`) | Read 25 Nov 2026; listing dates not shown on pages | Plot estimate |
| Plot averages (reference only) | [MagicBricks locality pages](https://www.magicbricks.com/Property-Rates-Trends/Multistorey-Apartment-rates-Btm-Layout-in-Bangalore) | Q3 2026 | Shown, not used (unit ambiguous) |
| Micro-market annual change | [Knight Frank India Real Estate H1 2026 (PDF)](https://content.knightfrank.com/research/3116/documents/en/india-real-estate-office-and-residential-market-h1-2026-12927.pdf), table "Residential price movement in select locations" | 12 months to H1 2026 | Outlook baseline (11 areas) |
| City annual change | [ANAROCK Pan-India Residential Market Viewpoints Q3 2026 (PDF)](https://investmentguruindia.com/editorial/uploads/news-pdf/12601e58_Q3_2026_Pan_India_Residential_Market_Viewpoints_9cf1a7e616.pdf), read from a third-party host because the PDF on anarock.com would not load | Q3 2026 | Outlook baseline (19 areas) |
| Ward polygons | [GBA Wards Delimitation 2025, OpenCity](https://data.opencity.in/dataset/gba-wards-delimitation-2025) (369 wards, "Other (Public Domain)" license) | 2025 | Map outlines (28 areas) |
| HSR Layout outline | [OpenStreetMap relation 17168010](https://www.openstreetmap.org/relation/17168010) (suburb boundary, ODbL) | 2026 | Map outline |
| Amenity counts | OpenStreetMap via [Geofabrik southern-zone extract](https://download.geofabrik.de/asia/india/southern-zone.html) | 24 Nov 2026 | Liveability amenities component |
| Bus stops and routes | [Reclaim City India_GTFS, Bengaluru bus feed](https://github.com/reclaimchennai/India_GTFS) (built by [Vonter/bmtc-gtfs](https://github.com/Vonter/bmtc-gtfs) from BMTC data; ODbL, some contents BMTC copyright). Counts in `bus_connectivity.json` are a derived database, shared under ODbL | Feed dated 9 Nov 2026, downloaded 26 Nov 2026 | Compare bus row only |
| News headlines | [Google News RSS](https://news.google.com/rss/search) | live, 7-day cache, 90-day freshness window | Sentiment |
| Social posts | [Reddit r/bangalore search](https://www.reddit.com/r/bangalore/search/) | live, 7-day cache, 90-day freshness window | Sentiment |

All links verified reachable on 25 Nov 2026. Live sentiment coverage noted in this document is a snapshot of that date, not a standing fact.

## Known limitations

- Everything is asking prices. No registered-sale dataset (for example Karnataka registration records) was verified for this update.
- Portal averages disagree because asking averages follow whatever is listed that quarter, so the apartment midpoint is a summary of that disagreement, not a measured price.
- 8 plot estimates are modelled placeholders and 1 is a proxy; all are labelled.
- Water, flood-risk and canopy ratings are fixed values typed into the code with unverified sources.
- Amenity counts undercount (point-mapped features only) and use a typed centre point.
- As of 25 Nov 2026, sentiment was usable in only 2 of 30 areas; coverage shifts with the news cycle.
- The outlook has not been backtested.
- ANAROCK's Q3 2026 report was read from a third-party host because the PDF on anarock.com would not load; the figures match ANAROCK's published numbers.
- Bus counts show which routes exist near a centre point, not service frequency (upstream warns of inaccurate timetables); they are not scored.
- Area outlines are ward-based approximations, not official locality limits; Electronic City has no outline.

## Change log

### 25 Nov 2026: full data coverage, verified baselines and UX

- Replaced the original CARTO tile layer, whose configuration needed an API key that was no longer available, with OpenStreetMap tiles.
- Added area outlines: GBA 2025 ward merges via OpenCity for 28 areas, HSR Layout from its OpenStreetMap suburb boundary, Electronic City as a pin. Hover or tap shows the outline and the wards behind it.
- Added the Compare, Find my area and About data views.
- Extended to full 30-area coverage: apartment, plot and outlook figures for all 30 areas (plots: 21 direct, 8 modelled, 1 proxy).
- Replaced assumed zone-trend periods with verified annual figures: the Knight Frank H1 2026 PDF was checked directly, and ANAROCK Q3 2026 for the city-wide fallback. No assumed periods are compounded into forecasts.
- Demoted MagicBricks plot averages to reference-only after finding the unit label contradicts itself; plot estimates now rest only on audited Square Yards listings.
- Removed the earlier 40%-of-apartment-rate price cutoff and the geometric-mean plot method. No listing is excluded for its price.
- Replaced the hard-coded 3-tier amenity rating with measured OpenStreetMap counts.
- Sentiment now reports "insufficient data" instead of silently reading as neutral, and malformed news feeds (for example RT Nagar) are parsed tolerantly instead of failing.
- Restored the prediction feature with the formula above and a per-component breakdown in the UI.
- Moved the long calculation explanation into a collapsed "How this is calculated" dropdown (CSS v2.3.4).

### May 2026: initial build

- First working app: Leaflet map, liveability scorecard, deterministic weekly predictions, BWSSB Kaveri water layers, Namma Metro overlays (removed the same week), theme toggles, collapsible sidebars.

### Superseded experiments (no longer in the code, kept here for reference)

- Geometric-mean plot estimate over MagicBricks and Square Yards figures with a 40%-of-apartment-rate cutoff: withdrawn. The cutoff was arbitrary and the MagicBricks unit is unresolved.
- Zone trend periods assumed and compounded into 12-month forecasts: replaced by single-period annual changes from primary reports.
- Fixed 3-tier amenity rating: replaced by measured OSM counts.
- Namma Metro map overlays: removed in May 2026.
- Deterministic weekly predictions: replaced by the current 12-month outlook formula.

## Testing and improvement ideas before sharing widely

- Backtest the outlook formula against a year of portal snapshots before calling it a forecast.
- Add a registered-sale source (Karnataka IGR / Kaveri Online) to complement asking prices.
- Resolve the MagicBricks plot unit (Sq-Yrd vs sqft) with the publisher or drop the series entirely.
- Source the water, flood-risk and canopy ratings, or replace them with measured datasets.
- Count area-mapped (polygon) amenity features in OSM, not only points, so parks can return to the score.
- Broaden sentiment sources so more areas clear the 3-story minimum.
- Source an Electronic City boundary; it lies outside the GBA ward map.
- Refresh the Marathahalli and Vijayanagar MagicBricks figures when those pages update past Jul-Sep 2025.

## Repo layout

- `app.py`: Flask backend, market data, estimates, liveability, sentiment, outlook, API endpoints.
- `templates/index.html`: single-page layout and the four views.
- `static/js/main.js`: map, layers, area panel rendering.
- `static/js/features.js`: Compare, Find my area, About data.
- `static/css/style.css`: theme and layout (cache version set in index.html).
- `static_geojsons.json`: built area outlines served to the map.
- `wards_opencity_gba.json`: GBA 2025 ward polygons from OpenCity.
- `members.json`: ward-to-area membership with the evidence for each ward.
- `osm_overrides.json`: HSR Layout OpenStreetMap suburb outline.
- `boundary_provenance.json`: per-area outline source (28 ward merges, HSR from OSM, Electronic City none).
- `build_boundaries.py`, `generate_polygons.py`: boundary build scripts (build needs shapely, not in requirements.txt).
- `bus_connectivity.json`, `build_bus_connectivity.py`: bus stop and route counts per area and the script that builds them from the GTFS feed.
- `sentiment_cache.json`: 7-day server cache of news and social items.
- `requirements.txt`, `Procfile`: Render deployment (gunicorn).

## Running locally

```
pip install -r requirements.txt
python app.py
```

The app serves on http://localhost:5000.
