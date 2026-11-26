// Namma Estates: area outlines with hover, Compare, Find my area, About data.
// Runs after main.js. Uses the global `map` and `loadAreaData` from main.js.

(function () {
    const state = {
        summary: [],
        byName: {},
        zoneLayers: {},
        view: 'explore',
        compare: ['', '', ''],
        find: { price: 30000, live: 0, water: 0, green: 0, flood: false },
        matches: null,          // Set of matching area names while Find is active
        hovered: null,
        selected: null
    };

    const COMPARE_COLORS = ['#3b82f6', '#f59e0b', '#a855f7'];
    const inr = n => '₹' + Number(n).toLocaleString('en-IN');
    const esc = s => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
    const waterLabel = v => ['Low (tanker dependent)', 'Medium', 'High'][v];

    // ---------- Zone outlines ----------
    function accent() {
        return getComputedStyle(document.documentElement).getPropertyValue('--accent-primary').trim() || '#3b82f6';
    }

    function baseStyle(area) {
        const a = accent();
        const ci = state.compare.indexOf(area);
        if (state.view === 'compare' && ci >= 0) {
            return { color: COMPARE_COLORS[ci], weight: 3, opacity: 1, fillColor: COMPARE_COLORS[ci], fillOpacity: 0.3 };
        }
        if (state.view === 'find' && state.matches) {
            return state.matches.has(area)
                ? { color: '#10b981', weight: 2.5, opacity: 1, fillColor: '#10b981', fillOpacity: 0.3 }
                : { color: '#64748b', weight: 1, opacity: 0.35, fillColor: '#64748b', fillOpacity: 0.03 };
        }
        // Explore: no outlines by default. Only the hovered or selected area shows.
        if (state.view === 'explore' && state.selected === area) {
            return { color: a, weight: 3, opacity: 1, fillColor: a, fillOpacity: 0.3 };
        }
        return { color: a, weight: 0, opacity: 0, fillColor: a, fillOpacity: 0.001 };
    }

    function hoverStyle(area) {
        const s = baseStyle(area);
        return { color: s.color, weight: 3, opacity: 1, fillColor: s.fillColor, fillOpacity: 0.38 };
    }

    function refreshZoneStyles() {
        Object.entries(state.zoneLayers).forEach(([area, layer]) => {
            layer.setStyle(state.hovered === area ? hoverStyle(area) : baseStyle(area));
        });
    }

    function tipHtml(area) {
        const s = state.byName[area];
        if (!s) return `<strong>${esc(area)}</strong>`;
        return `<div class="zone-tip-name">${esc(area)}</div>` +
            `<div class="zone-tip-row"><span>Apartment asking</span><b>${s.apt_est === null ? 'no figure' : '~' + inr(s.apt_est)}/sqft</b></div>` +
            `<div class="zone-tip-row"><span>Liveability</span><b>${s.liveability}/10</b></div>` +
            `<div class="${s.outline && s.outline.approximate ? 'zone-tip-warn' : 'zone-tip-ok'}">${s.outline && s.outline.approximate ? 'Ward-based approximation (' + (s.outline.wards || []).length + (((s.outline.wards || []).length === 1) ? ' ward)' : ' wards)') : 'OpenStreetMap suburb outline'}</div>` +
            `<div class="zone-tip-hint">Click for details</div>`;
    }

    function buildZones(geojsons) {
        if (!map.getPane('zones')) {
            map.createPane('zones');
            map.getPane('zones').style.zIndex = 450;
        }
        Object.entries(geojsons).forEach(([area, gj]) => {
            if (!gj || !gj.type) return;
            const layer = L.geoJSON(gj, {
                pane: 'zones',
                style: () => baseStyle(area),
                // Each area is a real polygon, so hovering follows the actual outline
                smoothFactor: 0.6
            }).addTo(map);
            layer.bindTooltip(() => tipHtml(area), { sticky: true, direction: 'top', className: 'zone-tip', opacity: 1 });
            layer.on('mouseover', () => {
                state.hovered = area;
                layer.setStyle(hoverStyle(area));
                layer.bringToFront();
            });
            layer.on('mouseout', () => {
                state.hovered = null;
                layer.setStyle(baseStyle(area));
            });
            layer.on('click', () => selectArea(area));
            if (state.byName[area]) state.byName[area].outline = (gj.properties || {}).outline;
            state.zoneLayers[area] = layer;
        });
    }

    function outlineNote(area) {
        const s = state.byName[area] || {};
        const o = s.outline;
        if (!o) return 'No outline on the map: this area is outside the ward map, so it is shown as a pin only.';
        if (!o.approximate) return 'Outline: OpenStreetMap suburb boundary.';
        return 'Outline is a ward-based approximation, not an official locality limit. Wards: ' + (o.wards || []).join(', ') + '.';
    }
    function showOutlineNote(area) {
        const title = document.getElementById('info-title');
        if (!title) return;
        let n = document.getElementById('outline-note');
        if (!n) { n = document.createElement('p'); n.id = 'outline-note'; n.className = 'outline-note'; title.insertAdjacentElement('afterend', n); }
        n.textContent = outlineNote(area);
    }
    if (typeof window.loadAreaData === 'function') {
        const origLoad = window.loadAreaData;
        window.loadAreaData = async function (area) {
            state.selected = area; refreshZoneStyles();
            const r = await origLoad.apply(this, arguments);
            showOutlineNote(area);
            return r;
        };
    }

    function selectArea(area) {
        const btn = Array.from(document.querySelectorAll('.area-btn')).find(b => b.innerText === area);
        if (!btn) return;
        setView('explore');
        loadAreaData(area, btn);
    }
    window.selectAreaByName = selectArea;

    // ---------- View switching ----------
    window.setView = function (view) {
        state.view = view;
        if (typeof map !== 'undefined' && map.closePopup) map.closePopup();
        document.querySelectorAll('.mode-btn').forEach(b => b.classList.toggle('active', b.dataset.view === view));
        document.querySelectorAll('.view').forEach(v => v.classList.toggle('hidden', v.id !== 'view-' + view));
        if (view === 'find') runFind(); else state.matches = null;
        if (view === 'compare') renderCompare();
        if (view === 'about') renderAbout();
        refreshZoneStyles();
        // Heatmap/legend controls live in Explore only; keep the layers as the user left them.
    };

    // ---------- Compare ----------
    function initCompare() {
        const wrap = document.getElementById('compare-pickers');
        wrap.innerHTML = '';
        for (let i = 0; i < 3; i++) {
            const sel = document.createElement('select');
            sel.className = 'compare-select';
            sel.style.borderLeftColor = COMPARE_COLORS[i];
            sel.innerHTML = '<option value="">' + (i < 2 ? 'Choose area ' + (i + 1) : 'Add a third (optional)') + '</option>' +
                state.summary.map(s => `<option value="${esc(s.area)}">${esc(s.area)}</option>`).join('');
            sel.onchange = () => { state.compare[i] = sel.value; renderCompare(); refreshZoneStyles(); fitCompare(); };
            wrap.appendChild(sel);
        }
    }

    function fitCompare() {
        const layers = state.compare.filter(Boolean).map(a => state.zoneLayers[a]).filter(Boolean);
        if (!layers.length) return;
        const b = L.featureGroup(layers).getBounds();
        if (b.isValid()) map.flyToBounds(b, { padding: [60, 60], maxZoom: 14, duration: 0.8 });
    }

    function renderCompare() {
        const chosen = state.compare.map((a, i) => ({ a, i })).filter(x => x.a && state.byName[x.a]);
        const wrap = document.getElementById('compare-table-wrap');
        if (chosen.length < 2) {
            wrap.innerHTML = '<div class="empty-note">Choose at least two areas to see them side by side.</div>';
            return;
        }
        const rows = [
            { label: 'Apartment asking price per sqft (estimate, portal range)', get: s => s.apt_est, show: s => s.apt_est === null ? 'no figure found' : '~' + inr(s.apt_est) + ' (' + (s.apt_low === s.apt_high ? 'one source' : inr(s.apt_low) + ' to ' + inr(s.apt_high)) + ', ' + s.apt_conf + ' confidence)', best: null },
            { label: '12-month outlook, baseline (past 12-month change + liveability, excludes live news sentiment; the area panel adds it when enough fresh items exist)', get: s => s.outlook_percent, show: s => (s.outlook_percent > 0 ? '+' : '') + s.outlook_percent + '%', best: 'max' },
            { label: 'Plot asking price per sqft (estimate, range)', get: s => null, show: s => s.plot && s.plot.est ? '~' + inr(s.plot.est) + ' (' + (s.plot.low === s.plot.high ? 'single source' : inr(s.plot.low) + ' to ' + inr(s.plot.high)) + ', ' + s.plot.confidence + ' confidence, ' + s.plot.method + ')' : 'no estimate', best: null },
            { label: 'Liveability', get: s => s.liveability, show: s => s.liveability + ' / 10', best: 'max' },
            { label: 'Water supply', get: s => s.water_level, show: s => waterLabel(s.water_level), best: 'max' },
            { label: 'Green canopy', get: s => s.canopy_percent, show: s => s.canopy_percent + '%', best: 'max' },
            { label: 'Flood risk', get: s => ({ Low: 2, Moderate: 1, High: 0 })[s.flood_risk], show: s => s.flood_risk, best: 'max' },
            { label: 'Amenities', get: s => s.amenities_rating, show: s => s.amenities_rating + ' / 10', best: 'max' },
            { label: 'Bus routes within 1.5 km (counts, not timetables)', get: s => s.bus_routes, show: s => s.bus_routes == null ? 'no data' : s.bus_routes + ' routes, ' + s.bus_stops + ' stops', best: 'max' }
        ];
        let html = '<table class="compare-table"><thead><tr><th></th>' +
            chosen.map(c => `<th style="border-bottom-color:${COMPARE_COLORS[c.i]}">${esc(c.a)}</th>`).join('') + '</tr></thead><tbody>';
        rows.forEach(r => {
            const vals = chosen.map(c => r.get(state.byName[c.a]));
            const target = r.best === 'min' ? Math.min(...vals) : Math.max(...vals);
            const tie = !r.best || vals.every(v => v === vals[0]);
            html += `<tr><td class="row-label">${r.label}</td>` + chosen.map((c, idx) => {
                const s = state.byName[c.a];
                const best = !tie && vals[idx] === target;
                return `<td class="${best ? 'best' : ''}">${esc(r.show(s))}</td>`;
            }).join('') + '</tr>';
        });
        html += '</tbody></table>' +
            '<p class="fine-print">Prices are asking-price estimates from public portals with their ranges and confidence. The outlook here is the baseline without live news sentiment; open the area for the full version. Ratings are fixed estimates. See About data.</p>' +
            '<details class="bus-note"><summary>About the bus row</summary><p class="fine-print">Counts of BMTC bus stops and distinct route numbers within 1.5 km of each area centre point (not the outline), from the Bengaluru GTFS feed published by Reclaim City, built by Vonter from BMTC data, licence ODbL. It shows which routes exist, not how often they run: the upstream project warns its timetables and stop timings can be inaccurate, so no frequency or waiting time is claimed. Central areas near big bus hubs count high. Not used in the liveability score or outlook. Full note in About data.</p></details>' +
            '<div class="compare-actions">' + chosen.map(c => `<button class="mini-btn" onclick="selectAreaByName('${esc(c.a).replace(/'/g, "\\'")}')">Open ${esc(c.a)}</button>`).join('') + '</div>';
        wrap.innerHTML = html;
    }

    // ---------- Find my area ----------
    function readFind() {
        state.find.price = Number(document.getElementById('find-price').value);
        state.find.live = Number(document.getElementById('find-live').value);
        state.find.flood = document.getElementById('find-flood').checked;
        document.getElementById('find-price-val').innerText = state.find.price >= 30000 ? 'any' : inr(state.find.price);
        document.getElementById('find-live-val').innerText = state.find.live <= 0 ? 'any' : state.find.live + '+';
    }

    function runFind() {
        readFind();
        const f = state.find;
        const base = s => s.liveability >= f.live && s.water_level >= f.water && s.canopy_percent >= f.green && (!f.flood || s.flood_risk === 'Low');
        const any = f.price >= 30000;
        const ok = state.summary.filter(s => base(s) && (any || (s.apt_high !== null && s.apt_high <= f.price)));
        const partial = any ? [] : state.summary.filter(s => base(s) && s.apt_low !== null && s.apt_low <= f.price && s.apt_high > f.price);
        const byFit = (a, b) => (b.liveability - a.liveability) || ((a.apt_low || 0) - (b.apt_low || 0));
        ok.sort(byFit); partial.sort(byFit);
        state.matches = new Set(ok.concat(partial).map(s => s.area));
        const sum = document.getElementById('find-summary');
        sum.innerText = (ok.length ? `${ok.length} of ${state.summary.length} areas match, both portals within your cap` : 'No area has both portals within your cap.') + (partial.length ? ` ${partial.length} more are only partly within it (listed below).` : '');
        const item = (s, i) =>
            `<button class="find-item" onclick="selectAreaByName('${esc(s.area).replace(/'/g, "\\'")}')">` +
            `<span class="find-rank">${i + 1}</span>` +
            `<span class="find-name">${esc(s.area)}</span>` +
            `<span class="find-meta">${s.apt_est === null ? 'no price' : '~' + inr(s.apt_est) + ' (' + (s.apt_low === s.apt_high ? 'one source' : inr(s.apt_low) + ' to ' + inr(s.apt_high)) + ')'} · ${s.liveability}/10 · ${esc(waterLabel(s.water_level).split(' ')[0])} water</span></button>`;
        const res = document.getElementById('find-results');
        res.innerHTML = ok.map(item).join('') +
            (partial.length ? `<div class="find-partial-head">Partly within your cap: one portal is under it, the other is above it</div>` + partial.map(item).join('') : '');
        refreshZoneStyles();
        if (ok.length || partial.length) {
            const b = L.featureGroup(ok.concat(partial).map(s => state.zoneLayers[s.area]).filter(Boolean)).getBounds();
            if (b.isValid()) map.flyToBounds(b, { padding: [50, 50], maxZoom: 13, duration: 0.8 });
        }
    }

    function initFind() {
        ['find-price', 'find-live'].forEach(id => document.getElementById(id).addEventListener('input', runFind));
        document.getElementById('find-flood').addEventListener('change', runFind);
        const seg = (id, key) => document.querySelectorAll('#' + id + ' button').forEach(b => b.onclick = () => {
            document.querySelectorAll('#' + id + ' button').forEach(x => x.classList.remove('active'));
            b.classList.add('active');
            state.find[key] = Number(b.dataset.v);
            runFind();
        });
        seg('find-water', 'water');
        seg('find-green', 'green');
    }

    // ---------- About data ----------
    async function renderAbout() {
        const el = document.getElementById('about-content');
        if (el.dataset.loaded) return;
        try {
            const m = await (await fetch('/api/methodology')).json();
            const tag = { fixed: 'Fixed estimate', heuristic: 'News heuristic', mixed: 'Mixed', derived: 'Derived', sourced: 'Public data', trend: 'Trend', 'not available': 'Not available' };
            let html = '<p class="view-hint">Prices are asking prices from public portals (Nov 2026), shown as the portal figures rather than one average. Water, canopy, terrain and flood ratings are still fixed estimates typed into the app without cited sources. Here is which is which.</p>';
            m.metrics.forEach(x => {
                html += `<div class="about-item"><div class="about-head"><span>${esc(x.name)}</span><span class="tag tag-${x.kind}">${tag[x.kind]}</span></div><p>${esc(x.how)}</p></div>`;
            });
            const when = m.news_cache_newest ? (m.news_cache_oldest === m.news_cache_newest ? m.news_cache_newest : `${m.news_cache_oldest} to ${m.news_cache_newest}`) : 'not loaded yet';
            const aps = state.summary.filter(x => x.outline && x.outline.approximate && (x.outline.wards || []).length);
            html += '<details class="about-item"><summary>Wards in each area outline</summary>' + aps.map(x => `<p class="fine-print"><b>${esc(x.area)}</b>: ${esc(x.outline.wards.join(', '))}</p>`).join('') + '</details>';
            html += `<p class="fine-print">Headlines are cached per area for up to 7 days. Latest cached fetch times on this server: ${esc(when)}. Use the refresh button on an area to fetch fresh headlines.</p>`;
            html += '<p class="fine-print">Area outlines: Greater Bengaluru Authority 2025 ward boundaries via OpenCity (licence listed as Public Domain), grouped into areas by this app, plus the OpenStreetMap suburb outline for HSR Layout (ODbL). Wards were matched using OpenStreetMap place names. Electronic City has no outline. Base map: OpenStreetMap contributors. This is a research tool, not financial advice.</p>';
            el.innerHTML = html;
            el.dataset.loaded = '1';
        } catch (e) {
            el.innerHTML = '<div class="empty-note">Could not load the data notes. Try again.</div>';
        }
    }

    // ---------- Boot ----------
    async function boot() {
        try {
            const [sum, geo] = await Promise.all([
                fetch('/api/summary').then(r => r.json()),
                fetch('/api/all_geojsons').then(r => r.json())
            ]);
            state.summary = sum;
            sum.forEach(s => { state.byName[s.area] = s; });
            map.attributionControl.addAttribution('Wards: GBA via OpenCity; HSR outline: OpenStreetMap contributors');
            buildZones(geo);
            initCompare();
            initFind();
            renderCompare();
        } catch (e) {
            console.error('Feature init failed', e);
        }
    }

    // Recolour outlines when the theme flips
    const origToggle = window.toggleTheme;
    window.toggleTheme = function () { origToggle(); refreshZoneStyles(); };

    document.addEventListener('DOMContentLoaded', boot);
    if (document.readyState !== 'loading') boot();
})();
