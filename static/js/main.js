const formatCurrency = (num) => {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        maximumFractionDigits: 0
    }).format(num);
};

const BENGALURU_COORDS = [12.9716, 77.5946];
const map = L.map('map', {
    zoomControl: false 
}).setView(BENGALURU_COORDS, 12);

L.control.zoom({ position: 'bottomright' }).addTo(map);

L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
    subdomains: 'abcd',
    maxZoom: 20
}).addTo(map);

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
        
        popup.setContent(`<div style="font-family:\'Outfit\',sans-serif;font-size:0.95rem;line-height:1.4;color:#333;padding:5px;">${data.summary}</div>`);
        
        // Also load the area data and highlight
        const buttons = document.querySelectorAll('.area-btn');
        let matchedBtn = null;
        buttons.forEach(btn => {
            if(btn.innerText === data.nearest_area) matchedBtn = btn;
        });
        if(matchedBtn) loadAreaData(data.nearest_area, matchedBtn);
        
    } catch (err) {
        popup.setContent('<div style="color:red;font-family:\'Outfit\',sans-serif;">Error analyzing location.</div>');
    }
});

let currentGeoJsonLayer = null;

async function initializeApp() {
    try {
        const response = await fetch('/api/areas');
        const areas = await response.json();
        
        const areasList = document.getElementById('areas-list');
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

async function loadAreaData(area, buttonElement) {
    document.querySelectorAll('.area-btn').forEach(btn => btn.classList.remove('active'));
    buttonElement.classList.add('active');
    
    document.getElementById('info-panel').classList.add('hidden');
    document.getElementById('loading-state').classList.remove('hidden');

    try {
        const response = await fetch(`/api/area_data/${encodeURIComponent(area)}`);
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

function switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    
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
