// =============================================
// VN100 Stock Scorer — App Logic (Connected to API)
// =============================================

const API_BASE = "/api";

// ---- State ----
let allData = [];
let filteredData = [];
let currentSort = { key: 'total_score', dir: -1 }; // -1 = desc
let isRefreshing = false;
let currentCategory = 'vn30'; // Mặc định là VN30

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
        if (btn.innerText.toLowerCase().includes(category)) btn.classList.add('active');
    });
    
    // Đặc biệt cho Tab Custom
    const importSection = document.getElementById('importSection');
    if (category === 'custom') {
        importSection.style.display = 'block';
    } else {
        importSection.style.display = 'none';
    }

    // Reset filter và load data mới
    document.getElementById('searchInput').value = '';
    document.getElementById('filterQuadrant').value = '';
    fetchScores();
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
    allData = data || [];
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
    // Map keys to column index mới
    const keyIdx = { 
        'symbol': 2, 
        'mcdx_score': 3, 
        'banker_left': 4, 
        'banker_right': 5, 
        'total_score': 7, 
        'rs_ratio': 8, 
        'rs_mom': 9, 
        'tail_5d': 10 
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
        tbody.innerHTML = `<tr><td colspan="10" style="text-align:center; padding:48px; color:var(--text-muted);">Không có dữ liệu cho nhóm này. Hãy bấm Cập nhật ngay.</td></tr>`;
        document.getElementById('rowCount').textContent = 'Hiển thị 0 mã';
        return;
    }

    tbody.innerHTML = filteredData.map((d, i) => {
        const totalPct = (d.total_score / 2.0 * 100).toFixed(0);
        const totalClass = d.total_score >= 1.5 ? 'high' : d.total_score >= 0.8 ? 'mid' : 'low';

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
            <td><span class="score-val ${d.mcdx_score >= 0.8 ? 'high' : d.mcdx_score >= 0.4 ? 'mid' : 'low'}">${(d.mcdx_score || 0).toFixed(2)}</span></td>
            <td><span class="banker-value ${(d.banker_left || 0) >= 16 ? 'hot' : (d.banker_left || 0) >= 8 ? 'warm' : 'cold'}">${(d.banker_left || 0).toFixed(1)}</span></td>
            <td><span class="banker-value ${(d.banker_right || 0) >= 16 ? 'hot' : (d.banker_right || 0) >= 8 ? 'warm' : 'cold'}">${(d.banker_right || 0).toFixed(1)}</span></td>
            <td><span class="rrg-badge ${rrgClasses[d.rrg_quadrant] || ''}">${rrgDots[d.rrg_quadrant] || ''} ${d.rrg_quadrant}</span></td>
            <td>
                <div class="score-bar-wrap">
                    <div class="score-bar"><div class="score-bar-fill" style="width:${totalPct}%"></div></div>
                    <span class="score-val ${totalClass}">${d.total_score.toFixed(2)}</span>
                </div>
            </td>
            <td><span class="num-cell ${d.rs_ratio >= 100 ? 'above100' : 'below100'}">${d.rs_ratio.toFixed(2)}</span></td>
            <td><span class="num-cell ${d.rs_mom >= 100 ? 'above100' : 'below100'}">${d.rs_mom.toFixed(2)}</span></td>
            <td><span class="tail-value ${d.tail_5d >= 4 ? 'active' : ''}">${d.tail_5d.toFixed(2)}</span></td>
        </tr>`;
    }).join('');

    document.getElementById('rowCount').textContent = `Hiển thị ${filteredData.length} mã`;
}

// ---- Export CSV ----
function exportCSV() {
    const headers = ['STT','Mã CP','Tổng điểm','MCDX Score','Banker Left','Banker Right','Vùng RRG','RS-Ratio','RS-Mom','Tail 5D'];
    const rows = filteredData.map((d, i) =>
        [i+1, d.symbol, d.total_score.toFixed(2), d.mcdx_score.toFixed(2), d.banker_left, d.banker_right, d.rrg_quadrant,
         d.rs_ratio.toFixed(2), d.rs_mom.toFixed(2), d.tail_5d.toFixed(2)].join(',')
    );
    const csv = [headers.join(','), ...rows].join('\n');
    const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8;' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `${currentCategory.toUpperCase()}_Score_${new Date().toISOString().slice(0,10)}.csv`;
    a.click();
}
