// =============================================
// VN30 Stock Scorer — App Logic (Connected to API)
// =============================================

const API_BASE = "/api";

// ---- State ----
let allData = [];
let filteredData = [];
let currentSort = { key: 'total_score', dir: -1 }; // -1 = desc
let isRefreshing = false;
let currentCategory = 'vn30'; // Mặc định là VN30
let historyChart = null; // Biến lưu đồ thị

function toNumber(value, fallback = 0) {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : fallback;
}

function normalizeScoreRow(row) {
    const normalized = { ...row };
    normalized.total_score = toNumber(normalized.total_score);
    normalized.mcdx_score = toNumber(normalized.mcdx_score);
    normalized.rrg_score = toNumber(
        normalized.rrg_score,
        normalized.total_score - normalized.mcdx_score
    );
    normalized.extra_score = toNumber(
        normalized.extra_score,
        Math.max(normalized.total_score - normalized.mcdx_score - normalized.rrg_score, 0)
    );
    normalized.score_max = Math.max(
        toNumber(normalized.score_max, 2.0),
        normalized.total_score,
        0.01
    );
    return normalized;
}

// ---- Init ----
document.addEventListener('DOMContentLoaded', () => {
    fetchScores();
    
    // Only show refresh controls and poll status if running on localhost
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        checkStatus();
        setInterval(checkStatus, 3000);
    } else {
        // Hide local-only UI elements on Vercel
        const refreshBtn = document.getElementById('btnRefresh');
        if (refreshBtn) refreshBtn.style.display = 'none';
        const statusDot = document.getElementById('statusDot');
        if (statusDot) statusDot.style.visibility = 'hidden';
    }
});

// ---- Tab Switching ----
function switchTab(category) {
    currentCategory = category;
    
    // Update UI active state
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
        // So sánh chính xác hoặc dùng class
    });
    // Set active cho nút vừa bấm
    event.currentTarget.classList.add('active');
    
    // Ẩn/Hiện các section
    const importSection = document.getElementById('importSection');
    const historySection = document.getElementById('historySection');
    const mainTableContainer = document.querySelector('.table-section');
    const statsRow = document.querySelector('.stats-row');

    if (category === 'custom') {
        importSection.style.display = 'block';
        historySection.style.display = 'none';
        mainTableContainer.style.display = 'block';
        statsRow.style.display = 'flex';
    } else if (category === 'history') {
        importSection.style.display = 'none';
        historySection.style.display = 'block';
        mainTableContainer.style.display = 'none';
        statsRow.style.display = 'none';
    } else {
        importSection.style.display = 'none';
        historySection.style.display = 'none';
        mainTableContainer.style.display = 'block';
        statsRow.style.display = 'flex';
    }

    // Reset filter và load data mới (nếu không phải history)
    if (category !== 'history') {
        document.getElementById('searchInput').value = '';
        document.getElementById('filterQuadrant').value = '';
        fetchScores();
    }
}

// ---- History Logic ----
async function loadHistory() {
    const symbol = document.getElementById('historySymbol').value.trim().toUpperCase();
    if (!symbol) return alert("Vui lòng nhập mã cổ phiếu!");

    try {
        const response = await fetch(`${API_BASE}/history?symbol=${symbol}`);
        const data = await response.json();
        
        // Chỉ lấy 10 ngày gần nhất và đảo ngược để vẽ từ trái sang phải
        const historyData = data.slice(0, 10).reverse();
        
        renderHistoryTable(historyData);
        renderHistoryChart(historyData, symbol);
    } catch (error) {
        console.error("Error loading history:", error);
        alert("Không thể tải dữ liệu lịch sử!");
    }
}

function renderHistoryTable(data) {
    const tbody = document.getElementById('historyTableBody');
    if (!data || data.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; padding:20px;">Không có dữ liệu lịch sử cho mã này.</td></tr>`;
        return;
    }

    tbody.innerHTML = data.slice().reverse().map(d => {
        const row = normalizeScoreRow(d);
        const rrgScore = row.rrg_score.toFixed(2);
        return `<tr>
            <td>${row.updated_date}</td>
            <td style="color:var(--accent-blue); font-weight:600;">${row.mcdx_score.toFixed(2)}</td>
            <td style="color:var(--accent-green); font-weight:600;">${rrgScore}</td>
            <td style="font-weight:800;">${row.total_score.toFixed(2)}</td>
            <td>${row.rrg_quadrant}</td>
        </tr>`;
    }).join('');
}

function renderHistoryChart(data, symbol) {
    const ctx = document.getElementById('historyChart').getContext('2d');
    
    const labels = data.map(d => d.updated_date.slice(5)); // Lấy MM-DD
    const mcdxScores = data.map(d => d.mcdx_score);
    const rrgScores = data.map(d => normalizeScoreRow(d).rrg_score);
    const totalScores = data.map(d => d.total_score);
    const yMax = Math.max(2.1, ...data.map(d => normalizeScoreRow(d).score_max + 0.1));

    if (historyChart) {
        historyChart.destroy();
    }

    historyChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Tổng điểm',
                    data: totalScores,
                    borderColor: '#fbbf24',
                    backgroundColor: 'rgba(245, 158, 11, 0.1)',
                    borderWidth: 3,
                    tension: 0.3,
                    fill: true
                },
                {
                    label: 'MCDX Score',
                    data: mcdxScores,
                    borderColor: '#3b82f6',
                    borderWidth: 2,
                    tension: 0.3,
                    pointStyle: 'circle'
                },
                {
                    label: 'RRG Score',
                    data: rrgScores,
                    borderColor: '#10b981',
                    borderWidth: 2,
                    tension: 0.3,
                    pointStyle: 'rectRot'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { labels: { color: '#94a3b8', font: { size: 12 } } },
                title: { display: true, text: `Biến động 10 ngày của ${symbol}`, color: '#f8fafc', font: { size: 16 } }
            },
            scales: {
                y: {
                    min: 0,
                    max: yMax,
                    ticks: { color: '#64748b' },
                    grid: { color: 'rgba(255,255,255,0.05)' }
                },
                x: {
                    ticks: { color: '#64748b' },
                    grid: { display: false }
                }
            }
        }
    });
}

// ---- API Calls ----
async function fetchScores() {
    try {
        // Try local API first
        const response = await fetch(`${API_BASE}/scores?category=${currentCategory}`);
        if (!response.ok) throw new Error("Local API failed");
        const data = await response.json();
        processData(data);
    } catch (error) {
        console.log(`Local API not available, falling back to data_${currentCategory}.json...`);
        try {
            // Fallback to static JSON file
            const filename = currentCategory === 'vn30' ? 'data_vn30.json' : 
                            currentCategory === 'vn100' ? 'data_vn100.json' : 
                            currentCategory === 'custom' ? 'data_custom.json' : 'data.json';
            const response = await fetch(filename);
            if (!response.ok) throw new Error(`${filename} not found`);
            const data = await response.json();
            processData(data);
        } catch (err) {
            console.error("Could not fetch data from any source:", err);
            processData([]);
        }
    }
}

function processData(data) {
    allData = (data || []).map(normalizeScoreRow);
    filteredData = [...allData];
    
    updateStats();
    sortAndRender();
    
    if (allData.length > 0 && allData[0].updated_at) {
        const lastUpdate = new Date(allData[0].updated_at);
        document.getElementById('updateText').textContent = `Cập nhật: ${lastUpdate.toLocaleDateString('vi-VN')} ${lastUpdate.toLocaleTimeString('vi-VN', {hour:'2-digit', minute:'2-digit'})}`;
    } else {
        document.getElementById('updateText').textContent = `Chưa có dữ liệu`;
    }
}

async function checkStatus() {
    try {
        const response = await fetch(`${API_BASE}/status?category=${currentCategory}`);
        const status = await response.json();
        
        const btn = document.getElementById('btnRefresh');
        const dot = document.getElementById('statusDot');
        const prog = document.getElementById('progressContainer');
        const bar = document.getElementById('progressBar');
        const lbl = document.getElementById('progressLabel');
        
        if (status.is_running) {
            isRefreshing = true;
            btn.disabled = true;
            btn.classList.add('loading');
            dot.classList.add('running');
            prog.classList.add('visible');
            
            lbl.textContent = `Đang cập nhật toàn bộ tiêu chí (${currentCategory.toUpperCase()})...`;
            bar.style.width = '100%'; 
        } else {
            if (isRefreshing) {
                // Was refreshing, now stopped -> fetch new data
                fetchScores();
                isRefreshing = false;
            }
            btn.disabled = false;
            btn.classList.remove('loading');
            dot.classList.remove('running');
            prog.classList.remove('visible');
        }
    } catch (error) {
        console.error("Error checking status:", error);
    }
}

async function startRefresh() {
    console.log(`Refresh clicked for ${currentCategory}`);
    try {
        const response = await fetch(`${API_BASE}/refresh?category=${currentCategory}`, { 
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        const result = await response.json();
        console.log("API Response:", result);
        checkStatus();
    } catch (error) {
        console.error("Error starting refresh:", error);
        alert("Lỗi kết nối tới Backend!");
    }
}

async function saveCustomList() {
    const input = document.getElementById('customSymbolsInput').value;
    if (!input.trim()) return alert("Vui lòng nhập danh sách mã CP!");

    // Parse mã CP (tách theo phẩy hoặc xuống dòng)
    const symbols = input.split(/[\n,]/)
                        .map(s => s.trim().toUpperCase())
                        .filter(s => s.length > 0);

    try {
        const response = await fetch(`${API_BASE}/import`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ symbols })
        });
        const result = await response.json();
        alert(result.message || "Đã lưu danh sách!");
        switchTab('custom'); // Refresh tab custom
    } catch (error) {
        console.error("Error saving custom list:", error);
        alert("Lỗi khi lưu danh sách!");
    }
}

// ---- Stats ----
function updateStats() {
    const counts = { "TĂNG GIÁ": 0, "TÍCH LŨY": 0, "SUY YẾU": 0, "GIẢM GIÁ": 0 };
    allData.forEach(d => { 
        const q = d.rrg_quadrant;
        if (counts[q] !== undefined) counts[q]++; 
    });

    document.getElementById('statTotal').textContent = allData.length;
    document.getElementById('statLeading').textContent = counts["TĂNG GIÁ"];
    document.getElementById('statImproving').textContent = counts["TÍCH LŨY"];
    document.getElementById('statWeakening').textContent = counts["SUY YẾU"];
    document.getElementById('statLagging').textContent = counts["GIẢM GIÁ"];
    
    if (allData.length > 0) {
        const scores = allData.map(d => d.total_score).filter(s => !isNaN(s));
        if (scores.length > 0) {
            const maxScore = Math.max(...scores);
            document.getElementById('statTopScore').textContent = maxScore.toFixed(2);
        } else {
            document.getElementById('statTopScore').textContent = "—";
        }
    } else {
        document.getElementById('statTopScore').textContent = "—";
    }
}

// ---- Sort & Filter (Local) ----
function sortTable(key) {
    if (currentSort.key === key) {
        currentSort.dir *= -1;
    } else {
        currentSort.key = key;
        currentSort.dir = (key === 'symbol') ? 1 : -1;
    }
    sortAndRender();
    updateSortHeaders();
}

function sortAndRender() {
    filteredData.sort((a, b) => {
        const va = a[currentSort.key];
        const vb = b[currentSort.key];
        if (typeof va === 'string') return va.localeCompare(vb) * currentSort.dir;
        return (va - vb) * currentSort.dir;
    });
    renderTable();
}

function updateSortHeaders() {
    document.querySelectorAll('thead th.sortable').forEach(th => {
        th.classList.remove('active-sort');
        const icon = th.querySelector('.sort-icon');
        if (icon) icon.textContent = '↕';
    });
    const ths = document.querySelectorAll('thead th');
    // Map keys to column index mới (Dựa trên index.html mới)
    const keyIdx = { 
        'symbol': 2, 
        'total_score': 3, 
        'mcdx_score': 4, 
        'rrg_score': 5,
        'banker_left': 7, 
        'banker_right': 8, 
        'rs_ratio': 9, 
        'rs_mom': 10, 
        'tail_5d': 11 
    };
    const idx = keyIdx[currentSort.key];
    if (idx) {
        const th = ths[idx-1];
        if (th) {
            th.classList.add('active-sort');
            const icon = th.querySelector('.sort-icon');
            if (icon) icon.textContent = currentSort.dir > 0 ? '↑' : '↓';
        }
    }
}

function filterTable() {
    const search = document.getElementById('searchInput').value.trim().toUpperCase();
    const quadrant = document.getElementById('filterQuadrant').value;
    filteredData = allData.filter(d => {
        const matchSearch = !search || d.symbol.includes(search);
        const matchQuadrant = !quadrant || d.rrg_quadrant === quadrant;
        return matchSearch && matchQuadrant;
    });
    sortAndRender();
}

// ---- Render ----
function renderTable() {
    const tbody = document.getElementById('tableBody');

    if (filteredData.length === 0) {
        tbody.innerHTML = `<tr><td colspan="11" style="text-align:center; padding:48px; color:var(--text-muted);">Không có dữ liệu cho nhóm này. Hãy bấm Cập nhật ngay.</td></tr>`;
        document.getElementById('rowCount').textContent = 'Hiển thị 0 mã';
        return;
    }

    tbody.innerHTML = filteredData.map((d, i) => {
        const totalPct = Math.min(100, d.total_score / d.score_max * 100).toFixed(0);
        const totalClass = d.total_score >= 1.5 ? 'high' : d.total_score >= 0.8 ? 'mid' : 'low';
        const rrgScore = d.rrg_score.toFixed(2);

        const rrgClasses = {
            "TĂNG GIÁ": "rrg-leading",
            "TÍCH LŨY": "rrg-improving",
            "SUY YẾU":  "rrg-weakening",
            "GIẢM GIÁ": "rrg-lagging",
        };
        const rrgDots = { "TĂNG GIÁ": "🟢", "TÍCH LŨY": "🔵", "SUY YẾU": "🟠", "GIẢM GIÁ": "🔴" };

        return `<tr>
            <td class="col-rank">${i + 1}</td>
            <td><span class="symbol-badge">${d.symbol}</span></td>
            <td>
                <div class="score-bar-wrap">
                    <div class="score-bar"><div class="score-bar-fill" style="width:${totalPct}%"></div></div>
                    <span class="score-val ${totalClass}">${d.total_score.toFixed(2)}</span>
                </div>
            </td>
            <td><span class="score-val ${d.mcdx_score >= 0.8 ? 'high' : d.mcdx_score >= 0.4 ? 'mid' : 'low'}">${(d.mcdx_score || 0).toFixed(2)}</span></td>
            <td><span class="score-val ${rrgScore >= 0.8 ? 'high' : rrgScore >= 0.4 ? 'mid' : 'low'}">${rrgScore}</span></td>
            <td><span class="rrg-badge ${rrgClasses[d.rrg_quadrant] || ''}">${rrgDots[d.rrg_quadrant] || ''} ${d.rrg_quadrant}</span></td>
            <td><span class="banker-value ${(d.banker_left || 0) >= 16 ? 'hot' : (d.banker_left || 0) >= 8 ? 'warm' : 'cold'}">${(d.banker_left || 0).toFixed(1)}</span></td>
            <td><span class="banker-value ${(d.banker_right || 0) >= 16 ? 'hot' : (d.banker_right || 0) >= 8 ? 'warm' : 'cold'}">${(d.banker_right || 0).toFixed(1)}</span></td>
            <td><span class="num-cell ${d.rs_ratio >= 0 ? 'above100' : 'below100'}">${d.rs_ratio.toFixed(2)}</span></td>
            <td><span class="num-cell ${d.rs_mom >= 0 ? 'above100' : 'below100'}">${d.rs_mom.toFixed(2)}</span></td>
            <td><span class="tail-value ${d.tail_5d >= 4 ? 'active' : ''}">${d.tail_5d.toFixed(2)}</span></td>
        </tr>`;
    }).join('');

    document.getElementById('rowCount').textContent = `Hiển thị ${filteredData.length} mã`;
}

// ---- Export CSV ----
function exportCSV() {
    const headers = ['STT','Mã CP','Tổng điểm','MCDX Score','RRG Score','Điểm thêm','Banker Left','Banker Right','Vùng RRG','RS-Ratio','RS-Mom','Tail 5D'];
    const rows = filteredData.map((d, i) =>
        [i+1, d.symbol, d.total_score.toFixed(2), d.mcdx_score.toFixed(2), d.rrg_score.toFixed(2), d.extra_score.toFixed(2), d.banker_left, d.banker_right, d.rrg_quadrant,
         d.rs_ratio.toFixed(2), d.rs_mom.toFixed(2), d.tail_5d.toFixed(2)].join(',')
    );
    const csv = [headers.join(','), ...rows].join('\n');
    const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8;' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `${currentCategory.toUpperCase()}_Score_${new Date().toISOString().slice(0,10)}.csv`;
    a.click();
}
