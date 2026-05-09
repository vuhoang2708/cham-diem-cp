// =============================================
// VN100 Stock Scorer — App Logic (Connected to API)
// =============================================

const API_BASE = "http://localhost:8000/api";

// ---- State ----
let allData = [];
let filteredData = [];
let currentSort = { key: 'total_score', dir: -1 }; // -1 = desc
let isRefreshing = false;

// ---- Init ----
document.addEventListener('DOMContentLoaded', () => {
    fetchScores();
    checkStatus();
    // Poll status every 3 seconds if refreshing
    setInterval(checkStatus, 3000);
});

// ---- API Calls ----
async function fetchScores() {
    try {
        const response = await fetch(`${API_BASE}/scores`);
        if (!response.ok) throw new Error("Failed to fetch scores");
        const data = await response.json();
        
        allData = data;
        filteredData = [...allData];
        
        updateStats();
        sortAndRender();
        
        if (allData.length > 0) {
            const lastUpdate = new Date(allData[0].updated_at);
            document.getElementById('updateText').textContent = `Cập nhật: ${lastUpdate.toLocaleDateString('vi-VN')} ${lastUpdate.toLocaleTimeString('vi-VN', {hour:'2-digit', minute:'2-digit'})}`;
        }
    } catch (error) {
        console.error("Error fetching scores:", error);
    }
}

async function checkStatus() {
    try {
        const response = await fetch(`${API_BASE}/status`);
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
            
            // Note: Currently backend doesn't update progress detail, 
            // but we can show it's running.
            lbl.textContent = `Đang xử lý dữ liệu...`;
            bar.style.width = '50%'; // Indeterminate
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
    try {
        const response = await fetch(`${API_BASE}/refresh`, { method: 'POST' });
        if (response.ok) {
            console.log("Refresh started");
            checkStatus();
        }
    } catch (error) {
        console.error("Error starting refresh:", error);
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
        const maxScore = Math.max(...allData.map(d => d.total_score));
        document.getElementById('statTopScore').textContent = maxScore.toFixed(2);
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
    // This is a bit manual based on DOM order, could be improved
    const ths = document.querySelectorAll('thead th');
    // Map keys to column index (approximate)
    const keyIdx = { 'symbol':1, 'total_score':2, 'mcdx_score':3, 'banker_value':4, 'rs_ratio':6, 'rs_mom':7, 'tail_5d':8 };
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
        tbody.innerHTML = `<tr><td colspan="9" style="text-align:center; padding:48px; color:var(--text-muted);">Không có dữ liệu</td></tr>`;
        document.getElementById('rowCount').textContent = 'Hiển thị 0 mã';
        return;
    }

    tbody.innerHTML = filteredData.map((d, i) => {
        const totalPct = (d.total_score / 2.0 * 100).toFixed(0);
        const totalClass = d.total_score >= 1.5 ? 'high' : d.total_score >= 0.8 ? 'mid' : 'low';
        const bankerClass = d.banker_value >= 16 ? 'hot' : d.banker_value >= 8 ? 'warm' : 'cold';

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
            <td><span class="score-val ${d.mcdx_score >= 0.8 ? 'high' : d.mcdx_score >= 0.4 ? 'mid' : 'low'}">${d.mcdx_score.toFixed(1)}</span></td>
            <td><span class="banker-value ${bankerClass}">${d.banker_value.toFixed(0)}</span></td>
            <td><span class="rrg-badge ${rrgClasses[d.rrg_quadrant] || ''}">${rrgDots[d.rrg_quadrant] || ''} ${d.rrg_quadrant}</span></td>
            <td><span class="num-cell ${d.rs_ratio >= 100 ? 'above100' : 'below100'}">${d.rs_ratio.toFixed(2)}</span></td>
            <td><span class="num-cell ${d.rs_mom >= 100 ? 'above100' : 'below100'}">${d.rs_mom.toFixed(2)}</span></td>
            <td><span class="tail-value ${d.tail_5d >= 4 ? 'active' : ''}">${d.tail_5d.toFixed(2)}</span></td>
        </tr>`;
    }).join('');

    document.getElementById('rowCount').textContent = `Hiển thị ${filteredData.length} mã`;
}

// ---- Export CSV ----
function exportCSV() {
    const headers = ['STT','Mã CP','Tổng điểm','MCDX Score','Banker Value','Vùng RRG','RS-Ratio','RS-Mom','Tail 5D'];
    const rows = filteredData.map((d, i) =>
        [i+1, d.symbol, d.total_score.toFixed(2), d.mcdx_score.toFixed(1), d.banker_value, d.rrg_quadrant,
         d.rs_ratio.toFixed(2), d.rs_mom.toFixed(2), d.tail_5d.toFixed(2)].join(',')
    );
    const csv = [headers.join(','), ...rows].join('\n');
    const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8;' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `VN100_Score_${new Date().toISOString().slice(0,10)}.csv`;
    a.click();
}
