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
    "RT Nagar": [13.0184, 77.5934]
};

const WATER_LEVELS = {
    "Jayanagar": "high", "Basavanagudi": "high", "MG Road": "high", "Malleswaram": "high", "RT Nagar": "high", "JP Nagar": "high",
    "Rajajinagar": "medium", "Indiranagar": "medium", "Koramangala": "medium", "Yelahanka": "medium", "Banashankari": "high",
    "HSR Layout": "medium", "BTM Layout": "medium", "Electronic City": "medium", "Marathahalli": "medium", "Yeshwanthpur": "medium",
    "Kalyan Nagar": "medium", "Kammanahalli": "medium", "Nagarabhaavi": "medium", "Vijayanagar": "medium",
    "Whitefield": "low", "Bellandur": "low", "Sarjapur Road": "low", "KR Puram": "low", "Hebbal": "low"
};

// --- INITIALIZE MAP & VARIABLES ---
let activeAreaName = null;
let currentGeoJsonLayer = null;
let baseTileLayer = null;
let topoLayer = null;
let waterLayerGroup = null;

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

// --- COLLAPSIBLE SIDEBAR MANAGER ---
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const expandBtn = document.getElementById('expand-sidebar-btn');
    
    if (sidebar.classList.contains('collapsed')) {
        sidebar.classList.remove('collapsed');
        expandBtn.classList.add('hidden');
    } else {
        sidebar.classList.add('collapsed');
        expandBtn.classList.remove('hidden');
    }
    
    // Smoothly invalidate Leaflet map size after transitions (400ms) 
    // so map tiles auto-realign correctly without distortion.
    setTimeout(() => {
        map.invalidateSize({ animate: true });
    }, 420);
}

// --- MAP OVERLAYS CONTROLS ---

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

function toggleWaterLayer(checked) {
    if (checked) {
        if (!waterLayerGroup) {
            waterLayerGroup = L.layerGroup();
            Object.entries(AREA_COORDS).forEach(([area, latlng]) => {
                const status = WATER_LEVELS[area];
                let color = '#ef4444'; // Red (low / tanker)
                let label = 'Low (Tanker Dependent)';
                if (status === 'high') {
                    color = '#10b981'; // Green
                    label = 'High (Cauvery Connected)';
                } else if (status === 'medium') {
                    color = '#f59e0b'; // Orange/Yellow
                    label = 'Medium (Cauvery Connected)';
                }
                
                const circle = L.circle(latlng, {
                    color: color,
                    fillColor: color,
                    fillOpacity: 0.3,
                    radius: 1200,
                    weight: 1.5
                }).bindPopup(`
                    <div style="font-family:'Outfit',sans-serif;padding:3px;">
                        <b style="font-size:0.95rem;color:#111;">${area}</b><br>
                        <span style="color:${color};font-weight:700;">${label}</span>
                    </div>
                `);
                
                waterLayerGroup.addLayer(circle);
            });
        }
        waterLayerGroup.addTo(map);
    } else {
        if (waterLayerGroup) {
            map.removeLayer(waterLayerGroup);
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
    
    waterBadge.innerText = data.water_availability;
    elevBadge.innerText = data.elevation_info;
    
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
