// --- CONSTANTS & CONFIGURATIONS ---
const BENGALURU_COORDS = [12.9716, 77.5946];

const AREA_COORDS = {
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
    "Bannerghatta Road / Arekere": [12.8966, 77.5975],
    "Begur": [12.8806, 77.6244],
    "Singasandra": [12.8860, 77.6540],
    "RR Nagar": [12.9248, 77.5200],
    "Puttenahalli": [12.8997, 77.5818]
};

const WATER_LEVELS = {
    "Jayanagar": "high", "Basavanagudi": "high", "MG Road": "high", "Malleswaram": "high", "RT Nagar": "high", "JP Nagar": "high",
    "Rajajinagar": "medium", "Indiranagar": "medium", "Koramangala": "medium", "Yelahanka": "medium", "Banashankari": "high",
    "HSR Layout": "medium", "BTM Layout": "medium", "Electronic City": "medium", "Marathahalli": "medium", "Yeshwanthpur": "medium",
    "Kalyan Nagar": "medium", "Kammanahalli": "medium", "Nagarabhaavi": "medium", "Vijayanagar": "medium",
    "Bannerghatta Road / Arekere": "medium", "Begur": "low", "Singasandra": "low", "RR Nagar": "medium", "Puttenahalli": "medium",
    "Whitefield": "low", "Bellandur": "low", "Sarjapur Road": "low", "KR Puram": "low", "Hebbal": "low"
};

// --- NAMMA METRO DATA TRACKS & STATIONS ---
const METRO_STATIONS = [
    { name: "Majestic (Interchange)", coord: [12.9756, 77.5728], line: "Purple & Green Line Interchange" },
    { name: "Indiranagar", coord: [12.9783, 77.6408], line: "Purple Line" },
    { name: "MG Road", coord: [12.9718, 77.6010], line: "Purple Line" },
    { name: "Vijayanagar", coord: [12.9696, 77.5360], line: "Purple Line" },
    { name: "Whitefield (Kadugodi)", coord: [12.9698, 77.7499], line: "Purple Line" },
    { name: "KR Puram", coord: [13.0084, 77.7001], line: "Purple Line" },
    { name: "Mysore Road", coord: [12.9535, 77.5250], line: "Purple Line" },
    { name: "RR Nagar (Jnanabharathi)", coord: [12.9248, 77.5200], line: "Purple Line" },
    { name: "Jayanagar", coord: [12.9250, 77.5938], line: "Green Line" },
    { name: "JP Nagar", coord: [12.9063, 77.5857], line: "Green Line" },
    { name: "Banashankari", coord: [12.9254, 77.5467], line: "Green Line" },
    { name: "Yeshwanthpur", coord: [13.0285, 77.5409], line: "Green Line" },
    { name: "Malleswaram (Sampige Road)", coord: [13.0011, 77.5630], line: "Green Line" },
    { name: "BTM Layout", coord: [12.9165, 77.6101], line: "Yellow Line" },
    { name: "Silk Board", coord: [12.9174, 77.6225], line: "Yellow Line" },
    { name: "HSR Layout", coord: [12.9116, 77.6388], line: "Yellow Line" },
    { name: "Electronic City", coord: [12.8399, 77.6770], line: "Yellow Line" }
];

const PURPLE_LINE_PATH = [
    [12.9698, 77.7499], // Whitefield
    [13.0084, 77.7001], // KR Puram
    [12.9569, 77.7011], // Marathahalli
    [12.9783, 77.6408], // Indiranagar
    [12.9760, 77.6264], // Halasuru
    [12.9718, 77.6010], // MG Road
    [12.9756, 77.5728], // Majestic
    [12.9733, 77.5640], // City Railway
    [12.9696, 77.5360], // Vijayanagar
    [12.9535, 77.5250], // Mysore Road
    [12.9248, 77.5200], // RR Nagar
    [12.9015, 77.4725]  // Challaghatta
];

const GREEN_LINE_PATH = [
    [13.0285, 77.5409], // Yeshwanthpur
    [13.0011, 77.5630], // Malleswaram
    [12.9756, 77.5728], // Majestic
    [12.9600, 77.5740], // KR Market
    [12.9505, 77.5730], // National College
    [12.9406, 77.5738], // Lalbagh / Basavanagudi
    [12.9250, 77.5938], // Jayanagar
    [12.9063, 77.5857], // JP Nagar
    [12.9254, 77.5467], // Banashankari
    [12.8735, 77.5735], // Konanakunte Cross
    [12.8600, 77.5520]  // Silk Institute
];

const YELLOW_LINE_PATH = [
    [12.9215, 77.5830], // RV Road
    [12.9165, 77.6101], // BTM Layout
    [12.9174, 77.6225], // Silk Board
    [12.9116, 77.6388], // HSR Layout
    [12.8860, 77.6540], // Singasandra
    [12.8399, 77.6770], // Electronic City
    [12.8160, 77.6930]  // Bommasandra
];

// --- INITIALIZE MAP & VARIABLES ---
let activeAreaName = null;
let currentGeoJsonLayer = null;
let baseTileLayer = null;
let topoLayer = null;
let waterGeoJsonLayerGroup = null;
let metroLayerGroup = null;

const map = L.map('map', {
    zoomControl: false 
}).setView(BENGALURU_COORDS, 12);

L.control.zoom({ position: 'bottomright' }).addTo(map);

// --- THEME STATE MANAGER ---
let currentTheme = localStorage.getItem('theme') || 'dark';
document.documentElement.setAttribute('data-theme', currentTheme);

function updateThemeUI() {
    const sun = document.querySelector('.sun-icon');
    const moon = document.querySelector('.moon-icon');
    if (sun && moon) {
        if (currentTheme === 'dark') {
            sun.classList.remove('hidden');
            moon.classList.add('hidden');
        } else {
            sun.classList.add('hidden');
            moon.classList.remove('hidden');
        }
    }
}

function updateMapTileLayer() {
    if (baseTileLayer) {
        map.removeLayer(baseTileLayer);
    }
    
    // Choose beautiful tiles depending on light/dark themes
    const url = currentTheme === 'dark' 
        ? 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
        : 'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png';
        
    baseTileLayer = L.tileLayer(url, {
        attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
        subdomains: 'abcd',
        maxZoom: 20
    }).addTo(map);
}

function toggleTheme() {
    currentTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', currentTheme);
    localStorage.setItem('theme', currentTheme);
    updateThemeUI();
    updateMapTileLayer();
}

// Initial Tile setup
updateMapTileLayer();
updateThemeUI();

// --- COLLAPSIBLE SIDEBAR MANAGER (FIXED BOTTOM SHEET & 100vh RESIZING FOR MOBILE) ---
function toggleSidebar() {
    const container = document.querySelector('.app-container');
    const expandBtn = document.getElementById('expand-sidebar-btn');
    
    if (container.classList.contains('sidebar-collapsed')) {
        container.classList.remove('sidebar-collapsed');
        expandBtn.classList.add('hidden');
    } else {
        container.classList.add('sidebar-collapsed');
        expandBtn.classList.remove('hidden');
    }
    
    // Smoothly invalidate Leaflet map size after height transition (400ms) 
    // so map tiles auto-realign correctly without distortion.
    setTimeout(() => {
        map.invalidateSize({ animate: true });
    }, 420);
}

// --- MAP OVERLAYS CONTROLS ---

// 1. Topographic Elevation Overlay
function toggleTopoLayer(checked) {
    const sliderContainer = document.getElementById('opacity-slider-container');
    if (checked) {
        sliderContainer.classList.remove('disabled');
        if (!topoLayer) {
            topoLayer = L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
                maxZoom: 17,
                attribution: 'Map data: &copy; OpenStreetMap contributors, SRTM | Map style: &copy; OpenTopoMap (CC-BY-SA)',
                opacity: parseFloat(document.getElementById('topo-opacity').value) / 100
            });
        }
        topoLayer.addTo(map);
    } else {
        sliderContainer.classList.add('disabled');
        if (topoLayer) {
            map.removeLayer(topoLayer);
        }
    }
}

function updateTopoOpacity(val) {
    document.getElementById('opacity-val').innerText = val + '%';
    if (topoLayer) {
        topoLayer.setOpacity(parseFloat(val) / 100);
    }
}

// 2. Verified BWSSB Kaveri Water Supply (Contiguous GeoJSON Overlay!)
async function toggleWaterLayer(checked) {
    if (checked) {
        if (!waterGeoJsonLayerGroup) {
            waterGeoJsonLayerGroup = L.layerGroup();
            
            try {
                // Fetch the complete procedurial boundaries
                const response = await fetch('/api/all_geojsons');
                const geojsons = await response.json();
                
                Object.entries(geojsons).forEach(([areaName, geojson]) => {
                    const status = WATER_LEVELS[areaName] || "low";
                    let color = '#ef4444'; // Red (low / tanker)
                    let label = 'Low (Tanker Dependent)';
                    if (status === 'high') {
                        color = '#10b981'; // Green
                        label = 'High (Cauvery Connected)';
                    } else if (status === 'medium') {
                        color = '#f59e0b'; // Orange/Yellow
                        label = 'Medium (Cauvery Connected)';
                    }
                    
                    const geoJsonLayer = L.geoJSON(geojson, {
                        style: {
                            color: color,
                            weight: 2,
                            opacity: 0.8,
                            fillColor: color,
                            fillOpacity: 0.3
                        }
                    }).bindPopup(`
                        <div style="font-family:'Outfit',sans-serif;padding:3px;">
                            <b style="font-size:0.95rem;color:#111;">${areaName}</b><br>
                            <span style="color:${color};font-weight:700;">${label}</span>
                        </div>
                    `);
                    
                    waterGeoJsonLayerGroup.addLayer(geoJsonLayer);
                });
            } catch (err) {
                console.error("Failed to draw contiguous Kaveri overlay:", err);
            }
        }
        waterGeoJsonLayerGroup.addTo(map);
    } else {
        if (waterGeoJsonLayerGroup) {
            map.removeLayer(waterGeoJsonLayerGroup);
        }
    }
}

// 3. Namma Metro Network Tracks & Stations
function toggleMetroLayer(checked) {
    if (checked) {
        if (!metroLayerGroup) {
            metroLayerGroup = L.layerGroup();
            
            // Draw Purple Line
            const purpleLine = L.polyline(PURPLE_LINE_PATH, {
                color: '#a855f7',
                weight: 5,
                opacity: 0.85
            }).bindPopup("<b>Namma Metro Purple Line</b> (East-West Corridor)");
            metroLayerGroup.addLayer(purpleLine);
            
            // Draw Green Line
            const greenLine = L.polyline(GREEN_LINE_PATH, {
                color: '#10b981',
                weight: 5,
                opacity: 0.85
            }).bindPopup("<b>Namma Metro Green Line</b> (North-South Corridor)");
            metroLayerGroup.addLayer(greenLine);
            
            // Draw Yellow Line
            const yellowLine = L.polyline(YELLOW_LINE_PATH, {
                color: '#f59e0b',
                weight: 5,
                opacity: 0.85,
                dashArray: '8, 8' // dotted overlay indicating Yellow Line/Silk Board corridor
            }).bindPopup("<b>Namma Metro Yellow Line</b> (Silk Board - Electronic City Corridor)");
            metroLayerGroup.addLayer(yellowLine);
            
            // Add Station Circle Markers
            METRO_STATIONS.forEach(station => {
                const color = station.line.includes("Purple") ? "#a855f7" : "#10b981";
                const marker = L.circleMarker(station.coord, {
                    radius: 6,
                    color: '#ffffff',
                    weight: 1.5,
                    fillColor: color,
                    fillOpacity: 0.95
                }).bindPopup(`
                    <div style="font-family:'Outfit',sans-serif;padding:3px;">
                        <b style="font-size:0.95rem;color:#111;">${station.name} Station</b><br>
                        <span style="color:#666;font-size:0.78rem;">${station.line}</span>
                    </div>
                `);
                metroLayerGroup.addLayer(marker);
            });
        }
        metroLayerGroup.addTo(map);
    } else {
        if (metroLayerGroup) {
            map.removeLayer(metroLayerGroup);
        }
    }
}

// --- INTERACTIVE MAP CLICK TO SEARCH ---
map.on('click', async function(e) {
    const lat = e.latlng.lat;
    const lon = e.latlng.lng;
    
    const popup = L.popup()
        .setLatLng(e.latlng)
        .setContent('<div class="spinner" style="width:20px;height:20px;margin:10px auto;"></div><div style="text-align:center;color:#333;">Analyzing zone...</div>')
        .openOn(map);
        
    try {
        const response = await fetch(`/api/nearest?lat=${lat}&lon=${lon}`);
        const data = await response.json();
        if (data.error) throw new Error(data.error);
        
        popup.setContent(`<div style="font-family:'Outfit',sans-serif;font-size:0.95rem;line-height:1.4;color:#333;padding:5px;">${data.summary}</div>`);
        
        // Also load the area data and highlight
        const buttons = document.querySelectorAll('.area-btn');
        let matchedBtn = null;
        buttons.forEach(btn => {
            if(btn.innerText === data.nearest_area) matchedBtn = btn;
        });
        if(matchedBtn) loadAreaData(data.nearest_area, matchedBtn);
        
    } catch (err) {
        popup.setContent('<div style="color:red;font-family:Outfit,sans-serif;">Error analyzing location.</div>');
    }
});

// --- CORE FRONTEND LOGIC ---
const formatCurrency = (num) => {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        maximumFractionDigits: 0
    }).format(num);
};

// Precise Haversine distance calculator
function getDistanceKm(lat1, lon1, lat2, lon2) {
    const R = 6371; // Earth radius in km
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
}

// Find nearest metro station
function findNearestMetro(areaLat, areaLon) {
    let nearest = null;
    let minDistance = Infinity;
    
    METRO_STATIONS.forEach(station => {
        const dist = getDistanceKm(areaLat, areaLon, station.coord[0], station.coord[1]);
        if (dist < minDistance) {
            minDistance = dist;
            nearest = station;
        }
    });
    
    return {
        station: nearest,
        distance: minDistance.toFixed(1)
    };
}

async function initializeApp() {
    try {
        const response = await fetch('/api/areas');
        const areas = await response.json();
        
        const areasList = document.getElementById('areas-list');
        areasList.innerHTML = '';
        areas.forEach(area => {
            const btn = document.createElement('button');
            btn.className = 'area-btn';
            btn.innerText = area;
            btn.onclick = () => loadAreaData(area, btn);
            areasList.appendChild(btn);
        });
    } catch (error) {
        console.error("Failed to fetch areas:", error);
    }
}

async function loadAreaData(area, buttonElement, forceRefresh = false) {
    document.querySelectorAll('.area-btn').forEach(btn => btn.classList.remove('active'));
    buttonElement.classList.add('active');
    
    document.getElementById('info-panel').classList.add('hidden');
    document.getElementById('loading-state').classList.remove('hidden');
    
    activeAreaName = area;

    try {
        const url = `/api/area_data/${encodeURIComponent(area)}${forceRefresh ? '?refresh=true' : ''}`;
        const response = await fetch(url);
        const data = await response.json();
        
        updateSidebar(data);
        updateMap(data);
    } catch (error) {
        console.error("Error loading area data:", error);
        alert("Failed to load data for " + area);
    } finally {
        document.getElementById('loading-state').classList.add('hidden');
        document.getElementById('info-panel').classList.remove('hidden');
    }
}

async function refreshLiveData() {
    if (!activeAreaName) {
        alert("Please select an explore zone first to refresh news sentiments!");
        return;
    }
    
    const refreshBtn = document.getElementById('refresh-feed-btn');
    if (refreshBtn) refreshBtn.classList.add('spinning');
    
    // Find active area button to pass it
    const buttons = document.querySelectorAll('.area-btn');
    let matchedBtn = null;
    buttons.forEach(btn => {
        if(btn.innerText === activeAreaName) matchedBtn = btn;
    });
    
    if (matchedBtn) {
        await loadAreaData(activeAreaName, matchedBtn, true);
    }
    
    if (refreshBtn) refreshBtn.classList.remove('spinning');
}

function switchTab(tabName, event) {
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    if (event) {
        event.currentTarget.classList.add('active');
    }
    
    // Update tab content
    document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
    document.getElementById(`tab-${tabName}`).classList.add('active');
}

function updateSidebar(data) {
    document.getElementById('info-title').innerText = data.area;
    
    const fin = data.financials;
    document.getElementById('current-price').innerText = formatCurrency(fin.current_price_sqft) + ' / sqft';
    document.getElementById('predicted-price').innerText = formatCurrency(fin.predicted_price_sqft) + ' / sqft';
    
    const trendInd = document.getElementById('trend-indicator');
    const trendIcon = document.getElementById('trend-icon');
    const trendPercent = document.getElementById('trend-percent');
    
    trendInd.className = 'trend-indicator'; 
    if (fin.change_percent > 0) {
        trendInd.classList.add('trend-up');
        trendIcon.innerText = '↑';
        trendPercent.innerText = `+${fin.change_percent}%`;
    } else if (fin.change_percent < 0) {
        trendInd.classList.add('trend-down');
        trendIcon.innerText = '↓';
        trendPercent.innerText = `${fin.change_percent}%`;
    } else {
        trendInd.classList.add('trend-stable');
        trendIcon.innerText = '→';
        trendPercent.innerText = `0%`;
    }
    
    document.getElementById('reasoning-text').innerText = fin.reason;
    
    // Update water and elevation badges dynamically
    const waterBadge = document.getElementById('water-status-badge');
    const elevBadge = document.getElementById('elevation-status-badge');
    const metroBadge = document.getElementById('metro-status-badge');
    
    waterBadge.innerText = data.water_availability;
    elevBadge.innerText = data.elevation_info;
    
    // Compute and display nearest Namma Metro station
    const coords = AREA_COORDS[data.area];
    if (coords) {
        const nearestMetro = findNearestMetro(coords[0], coords[1]);
        metroBadge.innerText = `${nearestMetro.station.name} (${nearestMetro.distance} km)`;
    } else {
        metroBadge.innerText = "No station found nearby";
    }
    
    // Dynamically color-code the water badge based on stage
    if (data.water_availability.includes('High')) {
        waterBadge.style.color = 'var(--success)';
    } else if (data.water_availability.includes('Medium')) {
        waterBadge.style.color = 'var(--warning)';
    } else {
        waterBadge.style.color = 'var(--danger)';
    }
    
    // Dynamically color-code the flood risk badge
    if (data.elevation_info.includes('Low Flood Risk')) {
        elevBadge.style.color = 'var(--success)';
    } else if (data.elevation_info.includes('Moderate')) {
        elevBadge.style.color = 'var(--warning)';
    } else {
        elevBadge.style.color = 'var(--danger)';
    }
    
    // News Tab
    const newsList = document.getElementById('news-list');
    newsList.innerHTML = ''; 
    if (data.news && data.news.length > 0) {
        data.news.forEach(item => {
            const li = document.createElement('li');
            li.innerHTML = `
                <a href="${item.link}" target="_blank">${item.title}</a>
                <div class="meta">${item.date}</div>
            `;
            newsList.appendChild(li);
        });
    } else {
        newsList.innerHTML = '<li>No recent credible news found.</li>';
    }

    // Social Tab
    const socialList = document.getElementById('social-list');
    socialList.innerHTML = ''; 
    if (data.social && data.social.length > 0) {
        data.social.forEach(item => {
            const li = document.createElement('li');
            li.innerHTML = `
                <a href="${item.link}" target="_blank">${item.title}</a>
                <div class="meta"><span class="score">↑ ${item.score}</span> Reddit upvotes</div>
            `;
            socialList.appendChild(li);
        });
    } else {
        socialList.innerHTML = '<li>No recent social media chatter found.</li>';
    }
}

function updateMap(data) {
    if (currentGeoJsonLayer) {
        map.removeLayer(currentGeoJsonLayer);
    }

    if (data.geojson) {
        const fin = data.financials;
        let color = '#3b82f6'; 
        if (fin.change_percent > 0) color = '#10b981'; 
        else if (fin.change_percent < 0) color = '#ef4444'; 

        currentGeoJsonLayer = L.geoJSON(data.geojson, {
            style: {
                color: color,
                weight: 3,
                opacity: 0.9,
                fillColor: color,
                fillOpacity: 0.25
            },
            pointToLayer: function (feature, latlng) {
                // If Nominatim only returned a point, draw a nice accurate circle around it
                return L.circle(latlng, {
                    color: color,
                    fillColor: color,
                    fillOpacity: 0.25,
                    radius: 800 // 800m radius
                });
            }
        }).addTo(map);

        // Zoom map to the actual area accurately
        const bounds = currentGeoJsonLayer.getBounds();
        if (bounds.isValid()) {
            map.flyToBounds(bounds, {
                padding: [50, 50],
                maxZoom: 15,
                duration: 1.5
            });
        }
    }
}

document.addEventListener('DOMContentLoaded', initializeApp);
