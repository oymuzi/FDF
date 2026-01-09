// FDF Dashboard - Modern Design
const CONFIG = {
    githubUsername: 'oymuzi',
    repoName: 'fdf',
    branch: 'main'
};

// 添加时间戳避免缓存
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

// Set time range
function setTimeRange(value) {
    // Update button states
    const buttons = document.querySelectorAll('#timeRangeControl .segment-btn');
    buttons.forEach(btn => {
        if (btn.dataset.value === value) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
    updateChart();
}

// Set account filter
function setAccountFilter(value) {
    // Update button states
    const buttons = document.querySelectorAll('#accountFilterControl .segment-btn');
    buttons.forEach(btn => {
        if (btn.dataset.value === value) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
    updateChart();
}

// Load CSV
async function loadCSV(filename) {
    // 添加时间戳参数避免缓存
    const url = BASE_URL + filename + '?t=' + Date.now();
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

    // 获取北京时间昨天最后一次的数据（00:00之前最后一条）
    const mzYesterday = getYesterdayLastValue(mzData);
    const wjYesterday = getYesterdayLastValue(wjData);

    // MZ
    document.getElementById('mzValue').textContent = `$${formatNumber(mz.总价值)}`;
    const mzChangeVal = mzYesterday
        ? ((mz.总价值 - mzYesterday.总价值) / mzYesterday.总价值 * 100).toFixed(2)
        : '0.00';
    updateStatChange('mzChange', mzChangeVal);

    // WJ
    document.getElementById('wjValue').textContent = `$${formatNumber(wj.总价值)}`;
    const wjChangeVal = wjYesterday
        ? ((wj.总价值 - wjYesterday.总价值) / wjYesterday.总价值 * 100).toFixed(2)
        : '0.00';
    updateStatChange('wjChange', wjChangeVal);

    // Time
    document.getElementById('updateTime').textContent = `Updated: ${formatTime(mz.时间)}`;
}

// 获取昨天最后一次的值（北京时间00:00之前）
function getYesterdayLastValue(data) {
    if (!data || data.length === 0) return null;

    const lastEntry = data[data.length - 1];
    const lastTime = new Date(lastEntry.时间);

    // 获取今天00:00（使用UTC+8北京时间）
    const todayDate = new Date(lastTime);
    todayDate.setHours(0, 0, 0, 0);

    // 从后往前找，找到今天00:00之前的最后一条数据
    for (let i = data.length - 1; i >= 0; i--) {
        const entryTime = new Date(data[i].时间);
        if (entryTime < todayDate) {
            return data[i];
        }
    }

    // 如果找不到昨天的数据，返回倒数第二条（前一次记录）
    if (data.length >= 2) {
        return data[data.length - 2];
    }

    return null;
}

function updateStatChange(id, val) {
    const el = document.getElementById(id);
    const num = parseFloat(val);
    const icon = num > 0 ? '↑' : num < 0 ? '↓' : '→';
    el.textContent = `${icon} ${Math.abs(num)}%`;
    el.className = `stat-change ${num > 0 ? 'positive' : num < 0 ? 'negative' : 'neutral'}`;
}

// Filter data by time range
function filterDataByTimeRange(data, range) {
    if (!data || data.length === 0) return data;

    const now = new Date();
    let startTime;

    switch (range) {
        case 'D':  // 近24小时
            startTime = new Date(now.getTime() - 24 * 60 * 60 * 1000);
            break;
        case 'W':  // 近一周
            startTime = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
            break;
        case 'All':  // 所有
        default:
            return data;
    }

    return data.filter(d => d.时间 >= startTime);
}

// Filter data by account
function filterDataByAccount(mzData, wjData, account) {
    switch (account) {
        case 'MZ':
            return { mzData, wjData: [] };
        case 'GEORGE':
            return { mzData: [], wjData };
        case 'All':
        default:
            return { mzData, wjData };
    }
}

// Create chart
function createChart() {
    const ctx = document.getElementById('mainChart')?.getContext('2d');
    if (!ctx) return;

    // 从激活的按钮获取当前值
    const timeRangeBtn = document.querySelector('#timeRangeControl .segment-btn.active');
    const accountFilterBtn = document.querySelector('#accountFilterControl .segment-btn.active');
    const timeRange = timeRangeBtn?.dataset.value || 'W';
    const accountFilter = accountFilterBtn?.dataset.value || 'All';

    // 过滤时间范围
    let filteredMz = filterDataByTimeRange(mzData, timeRange);
    let filteredWj = filterDataByTimeRange(wjData, timeRange);

    // 过滤账号
    const filtered = filterDataByAccount(filteredMz, filteredWj, accountFilter);
    filteredMz = filtered.mzData;
    filteredWj = filtered.wjData;

    // 对齐两个数据集，使用共同的时间范围
    const mzStartTime = filteredMz[0]?.时间.getTime();
    const mzEndTime = filteredMz[filteredMz.length - 1]?.时间.getTime();
    const wjStartTime = filteredWj[0]?.时间.getTime();
    const wjEndTime = filteredWj[filteredWj.length - 1]?.时间.getTime();

    // 如果某个数据集为空，使用另一个数据集的时间范围
    let alignedStart, alignedEnd;
    if (filteredMz.length === 0) {
        alignedStart = wjStartTime;
        alignedEnd = wjEndTime;
    } else if (filteredWj.length === 0) {
        alignedStart = mzStartTime;
        alignedEnd = mzEndTime;
    } else {
        alignedStart = Math.max(mzStartTime, wjStartTime);
        alignedEnd = Math.min(mzEndTime, wjEndTime);
    }

    // 过滤数据，确保在共同时间范围内
    const alignedMz = filteredMz.filter(d => d.时间.getTime() >= alignedStart && d.时间.getTime() <= alignedEnd);
    const alignedWj = filteredWj.filter(d => d.时间.getTime() >= alignedStart && d.时间.getTime() <= alignedEnd);

    // 使用两个数据集的时间并集作为标签（按时间排序）
    const allTimes = new Set();
    alignedMz.forEach(d => allTimes.add(d.时间.getTime()));
    alignedWj.forEach(d => allTimes.add(d.时间.getTime()));

    const sortedTimes = Array.from(allTimes).sort((a, b) => a - b);
    const labels = sortedTimes.map(t => formatTime(new Date(t)));

    // 创建时间到数据的映射
    const mzMap = new Map(alignedMz.map(d => [d.时间.getTime(), d.总价值]));
    const wjMap = new Map(alignedWj.map(d => [d.时间.getTime(), d.总价值]));

    // 生成对齐的数据数组
    const mzAlignedData = sortedTimes.map(t => mzMap.get(t) || null);
    const wjAlignedData = sortedTimes.map(t => wjMap.get(t) || null);

    // 创建datasets
    const datasets = [];
    if (filteredMz.length > 0) {
        datasets.push({
            label: 'MZ',
            data: mzAlignedData,
            borderColor: '#6366f1',
            backgroundColor: 'rgba(99, 102, 241, 0.1)',
            borderWidth: 3,
            fill: true,
            tension: 0.4,
            pointRadius: 0,
            pointHoverRadius: 6,
            pointHoverBackgroundColor: '#6366f1',
            spanGaps: true
        });
    }
    if (filteredWj.length > 0) {
        datasets.push({
            label: 'George',
            data: wjAlignedData,
            borderColor: '#8b5cf6',
            backgroundColor: 'rgba(139, 92, 246, 0.1)',
            borderWidth: 3,
            fill: true,
            tension: 0.4,
            pointRadius: 0,
            pointHoverRadius: 6,
            pointHoverBackgroundColor: '#8b5cf6',
            spanGaps: true
        });
    }

    mainChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels,
            datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: false,
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
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function(context) {
                            const datasetLabel = context.dataset.label || '';
                            let value = context.parsed.y;

                            // 如果当前值为null，向前查找最近的一个非null值
                            if (value === null || value === undefined) {
                                const dataIndex = context.dataIndex;
                                const datasetData = context.dataset.data;

                                // 向前查找最近的有效值
                                for (let i = dataIndex; i >= 0; i--) {
                                    if (datasetData[i] !== null && datasetData[i] !== undefined) {
                                        value = datasetData[i];
                                        break;
                                    }
                                }
                            }

                            if (value === null || value === undefined) {
                                return `${datasetLabel}: 暂无数据`;
                            }

                            return `${datasetLabel}: $${value.toFixed(2)}`;
                        }
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

// Update chart
function updateChart() {
    if (mainChart) {
        mainChart.destroy();
    }
    createChart();
}

// FUN Balance
let funData = null;
let currentFunPerson = 'mz';

// Load FUN balance data
async function loadFunBalance() {
    try {
        const url = BASE_URL + 'fun_balance.json?t=' + Date.now();
        const res = await fetch(url);
        if (!res.ok) throw new Error(res.status);
        funData = await res.json();
        updateFunDisplay();
    } catch (err) {
        console.log('FUN余额数据加载失败:', err);
    }
}

// Update FUN display in header
function updateFunDisplay() {
    if (!funData) return;

    const mzTotal = funData.mz.total;
    const georgeTotal = funData.george.total;

    // 如果两人都为0，隐藏显示
    if (mzTotal === 0 && georgeTotal === 0) {
        document.getElementById('funDisplay').style.display = 'none';
        return;
    }

    // 显示FUN区域
    const display = document.getElementById('funDisplay');
    display.style.display = 'flex';

    // 更新数值
    document.getElementById('mzFun').textContent = mzTotal.toFixed(18);
    document.getElementById('georgeFun').textContent = georgeTotal.toFixed(18);

    // 添加点击事件
    display.onclick = openFunModal;
}

// Open FUN modal
function openFunModal() {
    const modal = document.getElementById('funModal');
    modal.style.display = 'flex';
    renderFunDetails();
}

// Close FUN modal
function closeFunModal() {
    const modal = document.getElementById('funModal');
    modal.style.display = 'none';
}

// Switch FUN tab
function switchFunTab(person) {
    currentFunPerson = person;

    // 更新tab状态
    document.querySelectorAll('.fun-tab').forEach(tab => {
        if (tab.dataset.person === person) {
            tab.classList.add('active');
        } else {
            tab.classList.remove('active');
        }
    });

    renderFunDetails();
}

// Render FUN details
function renderFunDetails() {
    if (!funData) return;

    const person = currentFunPerson;
    const data = funData[person];

    // 更新总计
    document.getElementById('funSummary').textContent = '总计: ' + data.total.toFixed(18) + ' $FUN';

    // 渲染地址列表
    const listEl = document.getElementById('funAddressList');
    const addresses = data.addresses;

    if (Object.keys(addresses).length === 0) {
        listEl.innerHTML = '<div style="text-align: center; color: var(--text-muted); padding: 2rem;">暂无余额</div>';
        return;
    }

    const sortedAddrs = Object.entries(addresses).sort((a, b) => b[1] - a[1]);

    listEl.innerHTML = sortedAddrs.map(([addr, bal]) => `
        <div class="fun-address-item">
            <div class="fun-addr">${addr}</div>
            <div class="fun-addr-bal">${bal.toFixed(18)} $FUN</div>
        </div>
    `).join('');
}

// 点击模态框外部关闭
window.onclick = function(event) {
    const modal = document.getElementById('funModal');
    if (event.target === modal) {
        closeFunModal();
    }
}

// 在loadData中调用loadFunBalance
const originalLoadData = loadData;
loadData = async function() {
    await originalLoadData();
    await loadFunBalance();
};

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
