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
    "Bannerghatta Road": [12.8966, 77.5975],
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
    "Bannerghatta Road": "medium", "Begur": "low", "Singasandra": "low", "RR Nagar": "medium", "Puttenahalli": "medium",
    "Whitefield": "low", "Bellandur": "low", "Sarjapur Road": "low", "KR Puram": "low", "Hebbal": "low"
};

// --- INITIALIZE MAP & VARIABLES ---
let activeAreaName = null;
let currentGeoJsonLayer = null;
let baseTileLayer = null;
(function(){const s=document.createElement('style');s.textContent='.osm-dark-tiles{filter:invert(1) hue-rotate(180deg) brightness(0.95) contrast(0.9);}';document.head.appendChild(s);})();
let topoLayer = null;
let waterGeoJsonLayerGroup = null;
let greenGeoJsonLayerGroup = null;

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
    
    // CARTO basemaps now require an API key, and Esri's keyless legacy
    // canvas services are deprecated, so use the standard OpenStreetMap tiles
    // (allowed with visible attribution) and darken them with a CSS filter in dark mode.
    baseTileLayer = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 19,
        className: currentTheme === 'dark' ? 'osm-dark-tiles' : ''
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

// Update Topographic Opacity Slider
function updateTopoOpacity(val) {
    document.getElementById('opacity-val').innerText = val + '%';
    if (topoLayer) {
        topoLayer.setOpacity(parseFloat(val) / 100);
    }
}

// 2. Verified BWSSB Kaveri Water Supply (Contiguous GeoJSON Overlay!)
// 2. Verified BWSSB Kaveri Water Supply (Continuous City-Wide Heatmap Overlay!)
let waterCoverHeatLayer = null;
let waterLegendControl = null;

function addWaterLegend() {
    if (waterLegendControl) return;
    waterLegendControl = L.control({ position: 'bottomleft' });
    waterLegendControl.onAdd = function(map) {
        const div = L.DomUtil.create('div', 'map-legend glass-panel');
        div.innerHTML = `
            <div class="legend-header">
                <span class="legend-title">Water Security index</span>
            </div>
            <div class="legend-scale">
                <div class="scale-bar" style="background: linear-gradient(to right, #dc2626, #f59e0b, #2563eb) !important;"></div>
                <div class="scale-labels">
                    <span>Low (Red)</span>
                    <span>Medium</span>
                    <span>High (Blue)</span>
                </div>
            </div>
            <div class="legend-meta">Estimated supply (fixed values, unverified source)</div>
        `;
        return div;
    };
    waterLegendControl.addTo(map);
}

function removeWaterLegend() {
    if (waterLegendControl) {
        map.removeControl(waterLegendControl);
        waterLegendControl = null;
    }
}

async function toggleWaterLayer(checked) {
    if (checked) {
        if (!waterCoverHeatLayer) {
            try {
                // If not warmed up yet, pre-populate
                if (fetchedZonesData.length === 0) {
                    const response = await fetch('/api/all_geojsons');
                    const geojsons = await response.json();
                    Object.entries(geojsons).forEach(([areaName, geojson]) => {
                        if (!geojson) return;
                        const canopy = (geojson.properties && geojson.properties.canopy_percent) || 10;
                        const elevation = (geojson.properties && geojson.properties.elevation_info) || "Moderate Slope";
                        const water = (geojson.properties && geojson.properties.water_availability) || "Low (Tanker Dependent)";
                        const waterLevel = (geojson.properties && geojson.properties.water_level) || "low";
                        const coords = AREA_COORDS[areaName];
                        if (coords) {
                            fetchedZonesData.push({
                                lat: coords[0],
                                lon: coords[1],
                                canopy: canopy,
                                elevation: elevation,
                                water: water,
                                waterLevel: waterLevel
                            });
                        }
                    });
                }
                
                // Centered near MG Road
                const center = AREA_COORDS["MG Road"] || [12.9718, 77.6010];
                
                // Generate a grid of points across Bengaluru using IDW interpolation within a 25km radius circular boundary
                const points = [];
                const minLat = 12.74; // grid bounding box for 25km scanning
                const maxLat = 13.20;
                const minLon = 77.36;
                const maxLon = 77.84;
                const step = 0.005; // Grid resolution step
                
                for (let lat = minLat; lat <= maxLat; lat += step) {
                    for (let lon = minLon; lon <= maxLon; lon += step) {
                        const dx = (lon - center[1]) * 108.0;
                        const dy = (lat - center[0]) * 111.0;
                        const distKm = Math.sqrt(dx * dx + dy * dy);
                        
                        if (distKm <= 25.0) {
                            let totalWeight = 0;
                            let weightedWater = 0;
                            
                            // Map water level to numeric score: high=100, medium=60, low=20
                            const distances = fetchedZonesData.map(z => {
                                const dist = Math.sqrt((lat - z.lat) ** 2 + (lon - z.lon) ** 2);
                                let score = 20;
                                if (z.waterLevel === "high") score = 100;
                                else if (z.waterLevel === "medium") score = 60;
                                return { zone: z, dist: dist, score: score };
                            });
                            
                            distances.sort((a, b) => a.dist - b.dist);
                            const nearest = distances.slice(0, 3);
                            
                            let exactMatch = false;
                            for (let i = 0; i < nearest.length; i++) {
                                if (nearest[i].dist < 0.001) {
                                    points.push([lat, lon, nearest[i].score / 100]);
                                    exactMatch = true;
                                    break;
                                }
                                const weight = 1 / (nearest[i].dist ** 2);
                                totalWeight += weight;
                                weightedWater += nearest[i].score * weight;
                            }
                            
                            if (!exactMatch && totalWeight > 0) {
                                const interpolatedScore = weightedWater / totalWeight;
                                if (interpolatedScore > 10) {
                                    points.push([lat, lon, interpolatedScore / 100]);
                                }
                            }
                        }
                    }
                }
                
                // Create a highly contrasting Red-to-Blue continuous heatmap (Extremely subtle, clean, premium opacities)
                waterCoverHeatLayer = L.heatLayer(points, {
                    radius: 35,
                    blur: 25,
                    maxZoom: 15,
                    max: 4.5, // Calibrated max density to prevent saturation and separate high vs low beautifully!
                    gradient: {
                        0.0: 'rgba(220, 38, 38, 0.01)',     // Subtle low-opacity base glow
                        0.25: 'rgba(220, 38, 38, 0.18)',    // Crimson Red (Low/Tanker dependent) - reduced opacity
                        0.55: 'rgba(245, 158, 11, 0.10)',   // Amber Yellow midtone (high-contrast boundary)
                        0.8: 'rgba(59, 130, 246, 0.22)',    // Clear Ocean Blue (High stage 3/4)
                        1.0: 'rgba(37, 99, 235, 0.28)'      // Sapphire Blue (Stage 1/2) - elegant overlay
                    }
                });
            } catch (err) {
                console.error("Failed to generate city-wide water security heatmap:", err);
            }
        }
        if (waterCoverHeatLayer) {
            waterCoverHeatLayer.addTo(map);
            addWaterLegend();
            updateHeatmapVisualsForZoom(); // Immediately calibrate for current zoom!
        }
    } else {
        if (waterCoverHeatLayer) {
            map.removeLayer(waterCoverHeatLayer);
        }
        removeWaterLegend();
        const floatTooltip = document.getElementById('canopy-floating-tooltip');
        if (floatTooltip) floatTooltip.style.display = 'none';
    }
}

// 3. Green canopy (estimate) NDVI Heatmap (Continuous City-Wide Heatmap Overlay!)
let greenCoverHeatLayer = null;
let greenLegendControl = null;
let fetchedZonesData = [];

function addGreenLegend() {
    if (greenLegendControl) return;
    greenLegendControl = L.control({ position: 'bottomleft' });
    greenLegendControl.onAdd = function(map) {
        const div = L.DomUtil.create('div', 'map-legend glass-panel');
        div.innerHTML = `
            <div class="legend-header">
                <span class="legend-title">Green Canopy Density</span>
            </div>
            <div class="legend-scale">
                <div class="scale-bar"></div>
                <div class="scale-labels">
                    <span>Low (Red)</span>
                    <span>Medium</span>
                    <span>High (Green)</span>
                </div>
            </div>
            <div class="legend-meta">Estimated canopy (fixed values, unverified source)</div>
        `;
        return div;
    };
    greenLegendControl.addTo(map);
}

function removeGreenLegend() {
    if (greenLegendControl) {
        map.removeControl(greenLegendControl);
        greenLegendControl = null;
    }
}

async function toggleGreenCoverLayer(checked) {
    if (checked) {
        if (!greenCoverHeatLayer) {
            try {
                // If not warmed up yet, pre-populate from cash
                if (fetchedZonesData.length === 0) {
                    const response = await fetch('/api/all_geojsons');
                    const geojsons = await response.json();
                    Object.entries(geojsons).forEach(([areaName, geojson]) => {
                        if (!geojson) return;
                        const canopy = (geojson.properties && geojson.properties.canopy_percent) || 10;
                        const elevation = (geojson.properties && geojson.properties.elevation_info) || "Moderate Slope";
                        const water = (geojson.properties && geojson.properties.water_availability) || "Low (Tanker Dependent)";
                        const waterLevel = (geojson.properties && geojson.properties.water_level) || "low";
                        const coords = AREA_COORDS[areaName];
                        if (coords) {
                            fetchedZonesData.push({
                                lat: coords[0],
                                lon: coords[1],
                                canopy: canopy,
                                elevation: elevation,
                                water: water,
                                waterLevel: waterLevel
                            });
                        }
                    });
                }
                
                // Centered near MG Road coordinates
                const center = AREA_COORDS["MG Road"] || [12.9718, 77.6010];
                
                // Generate a dense grid of points across Bengaluru using IDW interpolation within an 18km radius circular boundary
                const points = [];
                const minLat = 12.80; // Highly optimized bounding box centered around MG Road for 18km scanning
                const maxLat = 13.14;
                const minLon = 77.42;
                const maxLon = 77.78;
                const step = 0.005; // Grid resolution step
                
                for (let lat = minLat; lat <= maxLat; lat += step) {
                    for (let lon = minLon; lon <= maxLon; lon += step) {
                        // Calculate Euclidean distance in kilometers
                        const dx = (lon - center[1]) * 108.0;
                        const dy = (lat - center[0]) * 111.0;
                        const distKm = Math.sqrt(dx * dx + dy * dy);
                        
                        if (distKm <= 18.0) {
                            let totalWeight = 0;
                            let weightedCanopy = 0;
                            
                            const distances = fetchedZonesData.map(z => {
                                const dist = Math.sqrt((lat - z.lat) ** 2 + (lon - z.lon) ** 2);
                                return { zone: z, dist: dist };
                            });
                            
                            distances.sort((a, b) => a.dist - b.dist);
                            const nearest = distances.slice(0, 3);
                            
                            let exactMatch = false;
                            for (let i = 0; i < nearest.length; i++) {
                                if (nearest[i].dist < 0.001) {
                                    points.push([lat, lon, nearest[i].zone.canopy / 50]);
                                    exactMatch = true;
                                    break;
                                }
                                const weight = 1 / (nearest[i].dist ** 2);
                                totalWeight += weight;
                                weightedCanopy += nearest[i].zone.canopy * weight;
                            }
                            
                            if (!exactMatch && totalWeight > 0) {
                                const interpolatedCanopy = weightedCanopy / totalWeight;
                                if (interpolatedCanopy > 1) {
                                    points.push([lat, lon, interpolatedCanopy / 50]);
                                }
                            }
                        }
                    }
                }
                
                // Create an extremely vibrant continuous RYG continuous heatmap (Increased opacity & high-contrast saturations)
                greenCoverHeatLayer = L.heatLayer(points, {
                    radius: 35,
                    blur: 25,
                    maxZoom: 15,
                    max: 3.2, // Calibrated max density to map canopy % exactly to 0.0 - 1.0 gradient stops
                    gradient: {
                        0.0: 'rgba(220, 38, 38, 0.0)',     // Completely transparent at 0%
                        0.15: 'rgba(220, 38, 38, 0.05)',   // Almost transparent warning edge (7.5% cover)
                        0.20: 'rgba(220, 38, 38, 0.15)',   // Light Red warning (10% cover) - prevents red globs!
                        0.24: 'rgba(245, 158, 11, 0.80)',  // Saturated Amber/Yellow (12% cover)
                        0.40: 'rgba(16, 185, 129, 0.90)',  // Emerald Green starts exactly at 20% cover! (Green begins at 20% cover)
                        0.60: 'rgba(5, 150, 105, 0.95)',   // Solid Green at exactly 30% cover
                        1.0: 'rgba(2, 44, 34, 1.0)'        // Deep Heritage Forest Green for high canopy (50%+)
                    }
                });
            } catch (err) {
                console.error("Failed to generate city-wide green cover heatmap:", err);
            }
        }
        if (greenCoverHeatLayer) {
            greenCoverHeatLayer.addTo(map);
            addGreenLegend();
            updateHeatmapVisualsForZoom(); // Immediately calibrate for current zoom!
        }
    } else {
        if (greenCoverHeatLayer) {
            map.removeLayer(greenCoverHeatLayer);
        }
        removeGreenLegend();
        const floatTooltip = document.getElementById('canopy-floating-tooltip');
        if (floatTooltip) floatTooltip.style.display = 'none';
    }
}

// --- INTERACTIVE MAP CLICK TO SEARCH ---
map.on('click', async function(e) {
    const lat = e.latlng.lat;
    const lon = e.latlng.lng;
    
    const popup = L.popup({ maxWidth: 260, maxHeight: 190, autoPan: true, autoPanPadding: [12, 12] })
        .setLatLng(e.latlng)
        .setContent('<div class="spinner" style="width:20px;height:20px;margin:10px auto;"></div><div style="text-align:center;color:#333;">Analyzing zone...</div>')
        .openOn(map);
        
    try {
        const response = await fetch(`/api/nearest?lat=${lat}&lon=${lon}`);
        const data = await response.json();
        if (data.error) throw new Error(data.error);
        
        popup.setContent(`<div style="font-family:'Outfit',sans-serif;font-size:0.85rem;line-height:1.35;color:#333;padding:2px 4px;">${data.summary}</div>`);
        
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

// --- INTERACTIVE MAP MOUSEMOVE HOVER TOOLTIP FOR GREEN COVER & TOPOGRAPHY ---
map.on('mousemove', function(e) {
    let floatTooltip = document.getElementById('canopy-floating-tooltip');
    if (!floatTooltip) {
        floatTooltip = document.createElement('div');
        floatTooltip.id = 'canopy-floating-tooltip';
        floatTooltip.className = 'canopy-tooltip';
        floatTooltip.style.position = 'absolute';
        floatTooltip.style.pointerEvents = 'none';
        floatTooltip.style.zIndex = '9999';
        floatTooltip.style.display = 'none';
        document.body.appendChild(floatTooltip);
    }

    const topoEnabled = document.getElementById('topo-layer-toggle').checked;
    const greenEnabled = document.getElementById('green-layer-toggle').checked;
    const waterEnabled = document.getElementById('water-layer-toggle').checked;

    if ((greenEnabled || topoEnabled || waterEnabled) && fetchedZonesData.length > 0) {
        const lat = e.latlng.lat;
        const lon = e.latlng.lng;
        
        // Find the nearest zone from fetchedZonesData
        let nearestZone = null;
        let minDist = Infinity;
        
        fetchedZonesData.forEach(z => {
            const dist = Math.sqrt((lat - z.lat) ** 2 + (lon - z.lon) ** 2);
            if (dist < minDist) {
                minDist = dist;
                nearestZone = z;
            }
        });
        
        const center = AREA_COORDS["MG Road"] || [12.9718, 77.6010];
        const dx = (lon - center[1]) * 108.0;
        const dy = (lat - center[0]) * 111.0;
        const distKm = Math.sqrt(dx * dx + dy * dy);
        
        let tooltipHtml = "";
        
        // 1. Topography Layer hover tooltip (within local neighborhood bounds)
        if (topoEnabled && nearestZone && minDist < 0.08) {
            let zoneName = "Nearby Zone";
            Object.entries(AREA_COORDS).forEach(([name, coords]) => {
                if (coords[0] === nearestZone.lat && coords[1] === nearestZone.lon) {
                    zoneName = name;
                }
            });
            tooltipHtml += `<div style="margin-bottom:2px;">📍 <b>${zoneName}</b></div>`;
            tooltipHtml += `<div>⛰️ Terrain: <b>${nearestZone.elevation}</b></div>`;
        }
        
        // 2. Green Canopy Layer hover tooltip (within 18km of MG Road)
        if (greenEnabled && distKm <= 18.0) {
            let totalWeight = 0;
            let weightedCanopy = 0;
            
            const distances = fetchedZonesData.map(z => {
                const dist = Math.sqrt((lat - z.lat) ** 2 + (lon - z.lon) ** 2);
                return { zone: z, dist: dist };
            });
            
            distances.sort((a, b) => a.dist - b.dist);
            const nearest = distances.slice(0, 3);
            
            let exactMatch = false;
            let canopyVal = 0;
            
            for (let i = 0; i < nearest.length; i++) {
                if (nearest[i].dist < 0.001) {
                    canopyVal = nearest[i].zone.canopy;
                    exactMatch = true;
                    break;
                }
                const weight = 1 / (nearest[i].dist ** 2);
                totalWeight += weight;
                weightedCanopy += nearest[i].zone.canopy * weight;
            }
            
            if (!exactMatch && totalWeight > 0) {
                canopyVal = Math.round(weightedCanopy / totalWeight);
            }
            
            if (canopyVal > 0) {
                if (tooltipHtml) tooltipHtml += `<hr style="margin: 6px 0; border: 0; border-top: 1px solid var(--glass-border);">`;
                tooltipHtml += `<div>🌳 Canopy Cover: <b>${canopyVal}%</b></div>`;
            }
        }

        // 3. Kaveri Water Supply hover tooltip (within local neighborhood bounds)
        if (waterEnabled && nearestZone && minDist < 0.08) {
            if (tooltipHtml) tooltipHtml += `<hr style="margin: 6px 0; border: 0; border-top: 1px solid var(--glass-border);">`;
            let waterColor = "var(--danger)";
            if (nearestZone.waterLevel === "high") waterColor = "var(--success)";
            else if (nearestZone.waterLevel === "medium") waterColor = "var(--warning)";
            
            tooltipHtml += `<div>🚰 Water: <span style="color:${waterColor};font-weight:700;">${nearestZone.water}</span></div>`;
        }
        
        if (tooltipHtml) {
            floatTooltip.innerHTML = tooltipHtml;
            floatTooltip.style.left = (e.originalEvent.pageX + 15) + 'px';
            floatTooltip.style.top = (e.originalEvent.pageY - 15) + 'px';
            floatTooltip.style.display = 'block';
        } else {
            floatTooltip.style.display = 'none';
        }
    } else {
        floatTooltip.style.display = 'none';
    }
});

map.on('mouseout', function() {
    const floatTooltip = document.getElementById('canopy-floating-tooltip');
    if (floatTooltip) floatTooltip.style.display = 'none';
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

        // Warm up and cache GeoJSON properties on startup for instantaneous, zero-lag hover tooltips
        const geoResponse = await fetch('/api/all_geojsons');
        const geojsons = await geoResponse.json();
        fetchedZonesData = [];
        Object.entries(geojsons).forEach(([areaName, geojson]) => {
            if (!geojson) return;
            const canopy = (geojson.properties && geojson.properties.canopy_percent) || 10;
            const elevation = (geojson.properties && geojson.properties.elevation_info) || "Moderate Slope";
            const water = (geojson.properties && geojson.properties.water_availability) || "Low (Tanker Dependent)";
            const waterLevel = (geojson.properties && geojson.properties.water_level) || "low";
            const coords = AREA_COORDS[areaName];
            if (coords) {
                fetchedZonesData.push({
                    lat: coords[0],
                    lon: coords[1],
                    canopy: canopy,
                    elevation: elevation,
                    water: water,
                    waterLevel: waterLevel
                });
            }
        });
    } catch (error) {
        console.error("Failed to fetch areas/geojsons during initialization:", error);
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
    const apt = fin.apartment, plot = fin.plot;
    const fmt = (n) => formatCurrency(n);
    const rng = (lo, hi) => lo === hi ? '' : fmt(lo) + ' to ' + fmt(hi);
    const ol = fin.outlook || {};
    document.getElementById('current-price').innerText = apt.est === null ? 'No figure found' : '~' + fmt(apt.est) + ' / sqft';
    document.getElementById('apt-note').innerText = (apt.est === null ? '' : 'Portal range ' + (rng(apt.low, apt.high) || fmt(apt.low)) + '. Confidence: ' + apt.confidence + '. ') + apt.note;
    const oa = ol.apartment;
    document.getElementById('predicted-price').innerText = oa ? '~' + fmt(oa.projected) + ' / sqft' : '--';
    document.getElementById('zone-note').innerText = oa ? 'Apartments in 12 months, ' + (ol.change_percent > 0 ? '+' : '') + ol.change_percent + '%, sensitivity band ' + fmt(oa.low) + ' to ' + fmt(oa.high) + ' (judgement, not a statistical interval). Confidence: ' + ol.confidence + '. A formula scenario, not a validated forecast.' : '';
    const od = document.getElementById('outlook-detail');
    od.innerHTML = '';
    if (ol.components) {
        const c = ol.components, s = fin.sentiment || {};
        const mkp = (t) => { const p = document.createElement('p'); p.textContent = t; od.appendChild(p); };
        mkp('Outlook ' + (ol.change_percent > 0 ? '+' : '') + ol.change_percent + '% = zone trend ' + c.baseline.value + '% (' + c.baseline.note + ') + liveability ' + c.liveability.value + ' (' + c.liveability.note + ') + sentiment ' + c.sentiment.value + '.');
        mkp('News and social sentiment: ' + (s.status === 'ok' ? 'used. ' : 'NOT used. ') + (s.note || ''));
        if (ol.plot) mkp('Plots in 12 months: ~' + fmt(ol.plot.projected) + ' / sqft, sensitivity band ' + fmt(ol.plot.low) + ' to ' + fmt(ol.plot.high) + ' (wider, plot data is thinner).');
        mkp(ol.disclaimer);
    }
    // Update overview Highlights (Liveability & Green Cover)
    if (data.liveability) {
        const scoreEl = document.getElementById('overview-liveability');
        scoreEl.innerText = data.liveability.score + ' / 10';
        if (data.liveability.score >= 8.0) {
            scoreEl.style.color = 'var(--success)';
        } else if (data.liveability.score >= 5.0) {
            scoreEl.style.color = 'var(--warning)';
        } else {
            scoreEl.style.color = 'var(--danger)';
        }
    }
    if (data.green_cover) {
        const greenEl = document.getElementById('overview-green');
        greenEl.innerText = data.green_cover.canopy_percent + '%';
        if (data.green_cover.canopy_percent >= 30) {
            greenEl.style.color = 'var(--success)';
        } else if (data.green_cover.canopy_percent >= 15) {
            greenEl.style.color = 'var(--warning)';
        } else {
            greenEl.style.color = 'var(--danger)';
        }
    }
    
    const landEl = document.getElementById('land-price');
    const landNote = document.getElementById('land-note');
    landEl.innerText = plot.est ? '~' + fmt(plot.est) + ' / sqft' : 'No estimate';
    landNote.innerText = (plot.est ? 'Range ' + (rng(plot.low, plot.high) || 'n/a (single source)') + '. Confidence: ' + plot.confidence + '. ' : '') + plot.note;
    const srcBox = document.getElementById('price-sources');
    srcBox.innerHTML = '';
    const mk = (tag, text, parent, href) => { const e = document.createElement(tag); e.textContent = text; if (href) { e.href = href; e.target = '_blank'; e.rel = 'noopener'; } parent.appendChild(e); return e; };
    mk('h4', 'Sources, asking prices, ' + fin.data_date, srcBox);
    (plot.sources || []).forEach(s => { const p = mk('p', '', srcBox); mk('a', s.source + ', ' + s.period + ': ' + fmt(s.value) + ' / sqft', p, s.url); });
    apt.sources.forEach(s => { const p = mk('p', '', srcBox); mk('a', s.source + ', ' + s.period + ': ' + fmt(s.value) + ' / sqft', p, s.url); });
    if (plot.listings && plot.listings.length) {
        const det = mk('details', '', srcBox); mk('summary', plot.listings.length + ' plot listings checked', det);
        plot.listings.forEach(l => { const p = mk('p', '', det); mk('a', fmt(l.psf) + ' / sqft, ' + l.plot_sqft + ' sqft, ' + (l.locality || ''), p, l.url); });
    }
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
    
    document.getElementById('reasoning-text').innerText = 'All prices are asking prices from public portals read on ' + fin.data_date + ', not recorded sale prices. Estimates always come with their source range and confidence. Where a figure is modelled or borrowed from a nearby area the note says so. See About data for the full method.' + (data.headlines_fetched ? ' Headlines cached ' + data.headlines_fetched + ' (used in the outlook only when enough recent headlines about this area exist).' : '');
    
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

    // Liveability Tab
    const liveabilityTab = document.getElementById('tab-liveability');
    if (liveabilityTab && data.liveability && data.amenities) {
        const liv = data.liveability;
        const amen = data.amenities;
        
        // Circular dial SVG progress
        const strokeDashOffset = 251.2 - (251.2 * liv.score) / 10;
        
        // Determine color based on score
        let scoreColor = 'var(--danger)';
        if (liv.score >= 8.0) scoreColor = 'var(--success)';
        else if (liv.score >= 5.0) scoreColor = 'var(--warning)';
        
        liveabilityTab.innerHTML = `
            <div class="liveability-scorecard">
                <div class="circular-progress-container">
                    <svg class="progress-ring" width="100" height="100">
                        <circle class="progress-ring__background" stroke="rgba(255,255,255,0.07)" stroke-width="8" fill="transparent" r="40" cx="50" cy="50"/>
                        <circle class="progress-ring__circle" stroke="${scoreColor}" stroke-width="8" fill="transparent" r="40" cx="50" cy="50"
                                style="stroke-dasharray: 251.2; stroke-dashoffset: ${strokeDashOffset}; transition: stroke-dashoffset 0.5s ease-in-out;"/>
                    </svg>
                    <div class="progress-text">
                        <span class="score-num">${liv.score}</span>
                        <span class="score-max">/10</span>
                    </div>
                </div>
                <div class="scorecard-header">
                    <h3>Liveability Rating</h3>
                    <p>Determined by environmental and infrastructural viability indices</p>
                </div>
            </div>
            
            <div class="factors-breakdown">
                <h4>Category Viability Indices</h4>
                
                <div class="factor-row">
                    <div class="factor-info">
                        <span class="factor-name">🚰 Water Security</span>
                        <span class="factor-score">${liv.water_rating}/10</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${liv.water_rating * 10}%; background: ${liv.water_rating >= 8 ? 'var(--success)' : (liv.water_rating >= 6 ? 'var(--warning)' : 'var(--danger)')}"></div>
                    </div>
                </div>
                
                <div class="factor-row">
                    <div class="factor-info">
                        <span class="factor-name">🌳 Green Cover Canopy</span>
                        <span class="factor-score">${liv.green_rating}/10</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${liv.green_rating * 10}%; background: ${liv.green_rating >= 8 ? 'var(--success)' : (liv.green_rating >= 6 ? 'var(--warning)' : 'var(--danger)')}"></div>
                    </div>
                </div>
                
                <div class="factor-row">
                    <div class="factor-info">
                        <span class="factor-name">⛰️ Terrain Safety & Drainage</span>
                        <span class="factor-score">${liv.topo_rating}/10</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${liv.topo_rating * 10}%; background: ${liv.topo_rating >= 8 ? 'var(--success)' : (liv.topo_rating >= 6 ? 'var(--warning)' : 'var(--danger)')}"></div>
                    </div>
                </div>
                
                <div class="factor-row">
                    <div class="factor-info">
                        <span class="factor-name">🏫 Public Infrastructure</span>
                        <span class="factor-score">${liv.amenities_rating}/10</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${liv.amenities_rating * 10}%; background: ${liv.amenities_rating >= 8 ? 'var(--success)' : (liv.amenities_rating >= 6 ? 'var(--warning)' : 'var(--danger)')}"></div>
                    </div>
                </div>
                
                <div class="factor-row">
                    <div class="factor-info">
                        <span class="factor-name">📊 Public Vibe (Sentiment)</span>
                        <span class="factor-score">${liv.sentiment_rating}/10</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${liv.sentiment_rating * 10}%; background: ${liv.sentiment_rating >= 8 ? 'var(--success)' : (liv.sentiment_rating >= 6 ? 'var(--warning)' : 'var(--danger)')}"></div>
                    </div>
                </div>
            </div>
            
            <div class="amenities-grid-section">
                <h4>Premium Public Infrastructure</h4>
                <div class="amenities-list-vertical">
                    <div class="amenity-item">
                        <div class="amenity-icon">🎓</div>
                        <div class="amenity-details">
                            <div class="amenity-type">Schools & Institutions</div>
                            <div class="amenity-names">${amen.schools || 'Local networks'}</div>
                        </div>
                    </div>
                    <div class="amenity-item">
                        <div class="amenity-icon">🌲</div>
                        <div class="amenity-details">
                            <div class="amenity-type">Parks & Recreation</div>
                            <div class="amenity-names">${amen.parks || 'Local neighborhood spaces'}</div>
                        </div>
                    </div>
                    <div class="amenity-item">
                        <div class="amenity-icon">🏥</div>
                        <div class="amenity-details">
                            <div class="amenity-type">Hospitals & Medical Care</div>
                            <div class="amenity-names">${amen.hospitals || 'Nearby clinics'}</div>
                        </div>
                    </div>
                    <div class="amenity-item">
                        <div class="amenity-icon">🛍️</div>
                        <div class="amenity-details">
                            <div class="amenity-type">Shopping & Recreation</div>
                            <div class="amenity-names">${amen.shopping || 'Local retail grids'}</div>
                        </div>
                    </div>
                </div>
            </div>
        `;
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
            interactive: false,
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

// --- HEATMAP DYNAMIC ZOOM OPTIMIZATION ---
function updateHeatmapVisualsForZoom() {
    const zoom = map.getZoom();
    
    // Scale Green Canopy Heatmap values dynamically
    if (greenCoverHeatLayer && map.hasLayer(greenCoverHeatLayer)) {
        let radius = 35;
        let blur = 25;
        let alphaMult = 1.0;
        
        // Dynamically double radius and blur with each zoom level to maintain overlap and density!
        if (zoom <= 11) {
            radius = 20;
            blur = 15;
            alphaMult = 0.85;
        } else if (zoom === 12) {
            radius = 35;
            blur = 25;
            alphaMult = 1.00;
        } else if (zoom === 13) {
            radius = 70;
            blur = 50;
            alphaMult = 1.05;
        } else if (zoom === 14) {
            radius = 130;
            blur = 90;
            alphaMult = 1.15; // Slightly increased opacity at zoom 14!
        } else if (zoom >= 15) {
            radius = 220;
            blur = 150;
            alphaMult = 1.30; // Highly opaque at zoom 15+!
        }
        
        greenCoverHeatLayer.setOptions({
            radius: radius,
            blur: blur,
            max: 3.2, // Keep max constant so normalized ratios match gradient stops perfectly!
            gradient: {
                0.0: `rgba(220, 38, 38, 0.0)`,                                   // Fully transparent at 0%
                0.15: `rgba(220, 38, 38, ${Math.min(0.05 * alphaMult, 0.12)})`,  // Subtle warning edge (7.5% cover)
                0.20: `rgba(220, 38, 38, ${Math.min(0.15 * alphaMult, 0.28)})`,  // Low opacity Red (10% cover) - prevents red globs!
                0.24: `rgba(245, 158, 11, ${Math.min(0.80 * alphaMult, 0.98)})`,  // Amber/Yellow transition (12% cover)
                0.40: `rgba(16, 185, 129, ${Math.min(0.90 * alphaMult, 1.0)})`,  // Emerald Green starts exactly at 20% cover!
                0.60: `rgba(5, 150, 105, ${Math.min(0.95 * alphaMult, 1.0)})`,   // Solid Green (30% cover)
                1.0: `rgba(2, 44, 34, ${Math.min(1.0 * alphaMult, 1.0)})`        // Deep Forest Green (50%+)
            }
        });
    }
    
    // Scale Kaveri Water Heatmap values dynamically
    if (waterCoverHeatLayer && map.hasLayer(waterCoverHeatLayer)) {
        let radius = 35;
        let blur = 25;
        let alphaMult = 1.0;
        
        if (zoom <= 11) {
            radius = 20;
            blur = 15;
            alphaMult = 0.80;
        } else if (zoom === 12) {
            radius = 35;
            blur = 25;
            alphaMult = 1.00;
        } else if (zoom === 13) {
            radius = 70;
            blur = 50;
            alphaMult = 1.10;
        } else if (zoom === 14) {
            radius = 130;
            blur = 90;
            alphaMult = 1.25; // Increase opacity on zoom in
        } else if (zoom >= 15) {
            radius = 220;
            blur = 150;
            alphaMult = 1.40; // High opacity overlay
        }
        
        waterCoverHeatLayer.setOptions({
            radius: radius,
            blur: blur,
            max: 4.5,
            gradient: {
                0.0: `rgba(220, 38, 38, ${Math.min(0.01 * alphaMult, 0.05)})`,
                0.25: `rgba(220, 38, 38, ${Math.min(0.18 * alphaMult, 0.35)})`,
                0.55: `rgba(245, 158, 11, ${Math.min(0.10 * alphaMult, 0.25)})`,
                0.8: `rgba(59, 130, 246, ${Math.min(0.22 * alphaMult, 0.50)})`,
                1.0: `rgba(37, 99, 235, ${Math.min(0.28 * alphaMult, 0.65)})`
            }
        });
    }
}

// Hook map zoom end event
map.on('zoomend', updateHeatmapVisualsForZoom);

document.addEventListener('DOMContentLoaded', initializeApp);
