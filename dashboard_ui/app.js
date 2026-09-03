const API_BASE = "http://localhost:8001/api/v1";

const UI = {
    stats: {
        total: document.getElementById('stat-total'),
        critical: document.getElementById('stat-critical'),
        ips: document.getElementById('stat-ips'),
        throughput: document.getElementById('stat-throughput')
    },
    table: document.getElementById('alerts-table'),
    drawer: {
        panel: document.getElementById('side-drawer'),
        backdrop: document.getElementById('drawer-backdrop'),
        id: document.getElementById('drawer-id'),
        target: document.getElementById('drawer-target'),
        threat: document.getElementById('drawer-threat'),
        conf: document.getElementById('drawer-conf'),
        sbytes: document.getElementById('feat-sbytes'),
        dbytes: document.getElementById('feat-dbytes'),
        proto: document.getElementById('feat-proto')
    }
};

function getSeverityStyle(severity) {
    if (severity === 'Critical') return 'bg-red-500/10 text-red-400 border-red-500/20';
    if (severity === 'High') return 'bg-amber-500/10 text-amber-400 border-amber-500/20';
    return 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20';
}

async function fetchStats() {
    try {
        const res = await fetch(`${API_BASE}/stats`);
        const data = await res.json();
        if(UI.stats.total) UI.stats.total.innerText = data.total_events;
        if(UI.stats.critical) UI.stats.critical.innerText = data.critical_threats;
        if(UI.stats.ips) UI.stats.ips.innerText = data.suspicious_ips;
        if(UI.stats.throughput) UI.stats.throughput.innerHTML = `${data.throughput_gbps}<span class="text-lg font-mono text-muted ml-1">Gbps</span>`;
    } catch (e) {}
}

async function fetchAlerts() {
    try {
        const res = await fetch(`${API_BASE}/alerts?limit=7`);
        const alerts = await res.json();
        
        if(!UI.table) return;
        UI.table.innerHTML = "";
        
        alerts.forEach(alert => {
            const timeStr = new Date(alert.timestamp * 1000).toLocaleTimeString();
            const sevStyle = getSeverityStyle(alert.severity);
            
            const tr = document.createElement('tr');
            tr.className = "hover:bg-card-hover/80 transition-colors group";
            tr.innerHTML = `
                <td class="py-4 px-6"><input type="checkbox" class="rounded border-border bg-card-bg text-brand"></td>
                <td class="py-4 px-6 font-mono text-muted whitespace-nowrap">${timeStr}</td>
                <td class="py-4 px-6 whitespace-nowrap">
                    <span class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-medium border ${sevStyle}">
                        ${alert.severity}
                    </span>
                </td>
                <td class="py-4 px-6">
                    <div class="font-medium text-on-surface">${alert.attack_category}</div>
                    <div class="text-[11px] text-muted">UNSW-NB15 Match</div>
                </td>
                <td class="py-4 px-6 font-mono whitespace-nowrap text-brand">${alert.srcip}</td>
                <td class="py-4 px-6 font-mono whitespace-nowrap text-on-surface">${alert.dstip}</td>
                <td class="py-4 px-6 text-right whitespace-nowrap">
                    <button onclick="openDrawerDetails('${alert.event_id}')" class="px-2.5 py-1 rounded bg-accent-red/20 text-accent-red hover:bg-accent-red hover:text-white transition-all text-xs font-medium">Inspect</button>
                </td>
            `;
            UI.table.appendChild(tr);
        });
    } catch (e) {}
}

async function openDrawerDetails(eventId) {
    try {
        const res = await fetch(`${API_BASE}/alerts/${eventId}`);
        const alert = await res.json();
        
        if(UI.drawer.id) UI.drawer.id.innerText = `#${alert.event_id.split('-')[0].toUpperCase()}`;
        if(UI.drawer.target) UI.drawer.target.innerText = alert.dstip;
        if(UI.drawer.threat) UI.drawer.threat.innerText = alert.srcip;
        if(UI.drawer.conf) UI.drawer.conf.innerText = `${(alert.anomaly_score * 100).toFixed(1)}% Match`;
        
        if(alert.raw_features) {
            if(UI.drawer.sbytes) UI.drawer.sbytes.innerText = alert.raw_features.sbytes || 'N/A';
            if(UI.drawer.dbytes) UI.drawer.dbytes.innerText = alert.raw_features.dbytes || 'N/A';
            if(UI.drawer.proto) UI.drawer.proto.innerText = alert.raw_features.proto || 'N/A';
        }
        
        UI.drawer.panel.classList.remove('translate-x-full');
        UI.drawer.backdrop.classList.remove('hidden');
    } catch (e) {}
}

function closeDrawer() {
    UI.drawer.panel.classList.add('translate-x-full');
    UI.drawer.backdrop.classList.add('hidden');
}

// Navigation Tabs Logic (Simple mock for now)
document.querySelectorAll('nav a').forEach(link => {
    link.addEventListener('click', (e) => {
        if(e.target.innerText !== 'Live Monitoring') {
            alert(`${e.target.innerText} module is initializing. Awaiting ML pipeline integration.`);
        }
    });
});

setInterval(() => {
    fetchStats();
    fetchAlerts();
}, 2500);

fetchStats();
fetchAlerts();