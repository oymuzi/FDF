// FDF Dashboard - Modern Design
const CONFIG = {
    githubUsername: 'oymuzi',
    repoName: 'fdf',
    branch: 'main'
};

const BASE_URL = `https://raw.githubusercontent.com/${CONFIG.githubUsername}/${CONFIG.repoName}/${CONFIG.branch}/data/`;

let mzData = [];
let wjData = [];
let mainChart = null;

// Init
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 FDF Dashboard');
    console.log('📦', BASE_URL);
    loadData();
});

// Load CSV
async function loadCSV(filename) {
    const url = BASE_URL + filename;
    try {
        const res = await fetch(url);
        if (!res.ok) throw new Error(res.status);
        const csv = await res.text();

        return new Promise((resolve, reject) => {
            Papa.parse(csv, {
                header: true,
                dynamicTyping: true,
                skipEmptyLines: true,
                complete: r => resolve(r.data),
                error: reject
            });
        });
    } catch (err) {
        console.error(`❌ ${filename}:`, err);
        throw err;
    }
}

// Load all data
async function loadData() {
    try {
        const [mz, wj] = await Promise.all([
            loadCSV('mz_history.csv'),
            loadCSV('wj_history.csv')
        ]);

        mzData = cleanData(mz);
        wjData = cleanData(wj);

        updateStats();
        createChart();

        console.log('✅ Loaded');
    } catch (err) {
        console.error('❌ Error:', err);
        showError('Failed to load data');
    }
}

// Clean data
function cleanData(data) {
    if (!data) return [];
    return data
        .filter(r => r['时间'] && r['总价值'])
        .map(r => ({
            ...r,
            时间: new Date(r['时间']),
            总价值: parseFloat(r['总价值'])
        }))
        .sort((a, b) => a.时间 - b.时间);
}

// Update stats
function updateStats() {
    if (!mzData.length || !wjData.length) return;

    const mz = mzData[mzData.length - 1];
    const wj = wjData[wjData.length - 1];

    // MZ
    document.getElementById('mzValue').textContent = `$${formatNumber(mz.总价值)}`;
    const mzChangeVal = ((mz.总价值 - (mzData[mzData.length-2]?.总价值||mz.总价值)) / (mzData[mzData.length-2]?.总价值||1) * 100).toFixed(2);
    updateStatChange('mzChange', mzChangeVal);

    // WJ
    document.getElementById('wjValue').textContent = `$${formatNumber(wj.总价值)}`;
    const wjChangeVal = ((wj.总价值 - (wjData[wjData.length-2]?.总价值||wj.总价值)) / (wjData[wjData.length-2]?.总价值||1) * 100).toFixed(2);
    updateStatChange('wjChange', wjChangeVal);

    // Time
    document.getElementById('updateTime').textContent = `Updated: ${formatTime(mz.时间)}`;
}

function updateStatChange(id, val) {
    const el = document.getElementById(id);
    const num = parseFloat(val);
    el.textContent = `${num > 0 ? '+' : ''}${val}%`;
    el.className = `stat-change ${num >= 0 ? 'positive' : 'negative'}`;
}

// Create chart
function createChart() {
    const ctx = document.getElementById('mainChart')?.getContext('2d');
    if (!ctx) return;

    const labels = mzData.map(d => formatTime(d.时间));

    mainChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels,
            datasets: [
                {
                    label: 'MZ',
                    data: mzData.map(d => d.总价值),
                    borderColor: '#6366f1',
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 6,
                    pointHoverBackgroundColor: '#6366f1'
                },
                {
                    label: 'George',
                    data: wjData.map(d => d.总价值),
                    borderColor: '#8b5cf6',
                    backgroundColor: 'rgba(139, 92, 246, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 6,
                    pointHoverBackgroundColor: '#8b5cf6'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(15, 23, 42, 0.95)',
                    titleColor: '#f1f5f9',
                    bodyColor: '#f1f5f9',
                    borderColor: '#334155',
                    borderWidth: 1,
                    padding: 12,
                    cornerRadius: 8,
                    callbacks: {
                        label: ctx => `${ctx.dataset.label}: $${ctx.parsed.y.toFixed(2)}`
                    }
                }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: {
                        color: '#64748b',
                        maxTicksLimit: 8
                    }
                },
                y: {
                    grid: { color: '#334155' },
                    ticks: {
                        color: '#64748b',
                        callback: v => `$${v.toFixed(0)}`
                    }
                }
            }
        }
    });
}

// Refresh
async function refreshData() {
    console.log('🔄 Refreshing...');
    const btn = document.querySelector('.refresh-btn');
    if (btn) btn.style.transform = 'rotate(360deg)';
    setTimeout(() => btn && (btn.style.transform = ''), 500);

    await loadData();
}

// Helpers
function formatNumber(n) {
    return n ? n.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2}) : '--';
}

function formatTime(d) {
    if (!d) return '--';
    const date = new Date(d);
    return `${String(date.getMonth()+1).padStart(2,'0')}-${String(date.getDate()).padStart(2,'0')} ${String(date.getHours()).padStart(2,'0')}:${String(date.getMinutes()).padStart(2,'0')}`;
}

function showError(msg) {
    const div = document.createElement('div');
    div.style.cssText = `position:fixed;top:20px;left:50%;transform:translateX(-50%);background:#ef4444;color:#fff;padding:1rem 2rem;border-radius:8px;z-index:9999;font-weight:500;`;
    div.textContent = msg;
    document.body.appendChild(div);
    setTimeout(() => div.remove(), 5000);
}

console.log('⚠️  Check CONFIG in js/app.js');
