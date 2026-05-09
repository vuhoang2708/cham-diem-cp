// =============================================
// VN100 Stock Scorer — App Logic
// =============================================

// ---- Mock data: 20 mã CP ----
const MOCK_DATA = [
  { symbol: "FPT",  banker_value: 20,    mcdx_score: 1.0, rrg: "TĂNG GIÁ",  rs_ratio: 104.32, rs_mom: 101.87, tail_5d: 3.21 },
  { symbol: "MWG",  banker_value: 16,    mcdx_score: 0.8, rrg: "TĂNG GIÁ",  rs_ratio: 102.15, rs_mom: 100.93, tail_5d: 2.88 },
  { symbol: "ACB",  banker_value: 20,    mcdx_score: 1.0, rrg: "TÍCH LŨY",  rs_ratio: 98.74,  rs_mom: 101.22, tail_5d: 4.55 },
  { symbol: "TCB",  banker_value: 12,    mcdx_score: 0.6, rrg: "TĂNG GIÁ",  rs_ratio: 101.88, rs_mom: 100.41, tail_5d: 2.10 },
  { symbol: "HPG",  banker_value: 16,    mcdx_score: 0.8, rrg: "TÍCH LŨY",  rs_ratio: 97.55,  rs_mom: 100.78, tail_5d: 5.32 },
  { symbol: "VHM",  banker_value: 8,     mcdx_score: 0.4, rrg: "TĂNG GIÁ",  rs_ratio: 103.44, rs_mom: 101.02, tail_5d: 1.97 },
  { symbol: "MSN",  banker_value: 12,    mcdx_score: 0.6, rrg: "TÍCH LŨY",  rs_ratio: 99.12,  rs_mom: 100.55, tail_5d: 3.78 },
  { symbol: "VIC",  banker_value: 8,     mcdx_score: 0.4, rrg: "TÍCH LŨY",  rs_ratio: 98.21,  rs_mom: 100.33, tail_5d: 2.45 },
  { symbol: "BID",  banker_value: 3,     mcdx_score: 0.2, rrg: "TĂNG GIÁ",  rs_ratio: 100.98, rs_mom: 100.12, tail_5d: 1.23 },
  { symbol: "CTG",  banker_value: 12,    mcdx_score: 0.6, rrg: "SUY YẾU",   rs_ratio: 100.44, rs_mom: 99.55,  tail_5d: 3.11 },
  { symbol: "GAS",  banker_value: 3,     mcdx_score: 0.2, rrg: "TÍCH LŨY",  rs_ratio: 97.88,  rs_mom: 100.21, tail_5d: 2.67 },
  { symbol: "VNM",  banker_value: 0,     mcdx_score: 0.0, rrg: "TĂNG GIÁ",  rs_ratio: 101.23, rs_mom: 100.44, tail_5d: 0.98 },
  { symbol: "SAB",  banker_value: 8,     mcdx_score: 0.4, rrg: "SUY YẾU",   rs_ratio: 101.55, rs_mom: 99.33,  tail_5d: 2.88 },
  { symbol: "VPB",  banker_value: 0,     mcdx_score: 0.0, rrg: "TÍCH LŨY",  rs_ratio: 96.44,  rs_mom: 100.11, tail_5d: 4.22 },
  { symbol: "PLX",  banker_value: 0,     mcdx_score: 0.0, rrg: "SUY YẾU",   rs_ratio: 100.77, rs_mom: 99.12,  tail_5d: 1.55 },
  { symbol: "VCB",  banker_value: 0,     mcdx_score: 0.0, rrg: "GIẢM GIÁ",  rs_ratio: 98.49,  rs_mom: 99.93,  tail_5d: 7.53 },
  { symbol: "SSI",  banker_value: 0,     mcdx_score: 0.0, rrg: "GIẢM GIÁ",  rs_ratio: 97.11,  rs_mom: 98.88,  tail_5d: 3.91 },
  { symbol: "VRE",  banker_value: 3,     mcdx_score: 0.2, rrg: "GIẢM GIÁ",  rs_ratio: 96.22,  rs_mom: 98.33,  tail_5d: 2.14 },
  { symbol: "HDB",  banker_value: 0,     mcdx_score: 0.0, rrg: "GIẢM GIÁ",  rs_ratio: 95.88,  rs_mom: 97.77,  tail_5d: 5.88 },
  { symbol: "PDR",  banker_value: 0,     mcdx_score: 0.0, rrg: "GIẢM GIÁ",  rs_ratio: 94.11,  rs_mom: 97.22,  tail_5d: 6.44 },
];

// ---- Scoring config ----
const RRG_SCORES = {
  "TĂNG GIÁ":  1.00,
  "TÍCH LŨY":  0.75,
  "SUY YẾU":   0.50,
  "GIẢM GIÁ":  0.25,
};

const MCDX_BREAKPOINTS = [
  [0, 0.0], [3, 0.2], [8, 0.4], [12, 0.6], [16, 0.8], [20, 1.0]
];

function interpolateMCDX(value) {
  if (value <= 0) return 0;
  if (value >= 20) return 1;
  for (let i = 0; i < MCDX_BREAKPOINTS.length - 1; i++) {
    const [x0, y0] = MCDX_BREAKPOINTS[i];
    const [x1, y1] = MCDX_BREAKPOINTS[i + 1];
    if (value >= x0 && value <= x1) {
      return y0 + (y1 - y0) * (value - x0) / (x1 - x0);
    }
  }
  return 0;
}

// ---- Enrich data ----
let allData = MOCK_DATA.map(d => {
  const rrg_score = RRG_SCORES[d.rrg] ?? 0.25;
  const total = parseFloat((d.mcdx_score + rrg_score).toFixed(2));
  return { ...d, rrg_score, total };
});

// ---- State ----
let currentSort = { key: 'total', dir: -1 }; // -1 = desc
let filteredData = [];

// ---- Init ----
document.addEventListener('DOMContentLoaded', () => {
  filteredData = [...allData];
  sortAndRender();
  updateStats();
});

// ---- Stats ----
function updateStats() {
  const counts = { "TĂNG GIÁ": 0, "TÍCH LŨY": 0, "SUY YẾU": 0, "GIẢM GIÁ": 0 };
  allData.forEach(d => { if (counts[d.rrg] !== undefined) counts[d.rrg]++; });

  document.getElementById('statTotal').textContent = allData.length;
  document.getElementById('statLeading').textContent = counts["TĂNG GIÁ"];
  document.getElementById('statImproving').textContent = counts["TÍCH LŨY"];
  document.getElementById('statWeakening').textContent = counts["SUY YẾU"];
  document.getElementById('statLagging').textContent = counts["GIẢM GIÁ"];
  const maxScore = Math.max(...allData.map(d => d.total));
  document.getElementById('statTopScore').textContent = maxScore.toFixed(2);
}

// ---- Sort ----
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
  const keyMap = {
    'symbol': 1, 'total': 2, 'mcdx_score': 3,
    'banker_value': 4, 'rs_ratio': 6, 'rs_mom': 7, 'tail_5d': 8
  };
  const idx = keyMap[currentSort.key];
  if (idx !== undefined) {
    const th = document.querySelector(`thead th:nth-child(${idx})`);
    if (th) {
      th.classList.add('active-sort');
      const icon = th.querySelector('.sort-icon');
      if (icon) icon.textContent = currentSort.dir > 0 ? '↑' : '↓';
    }
  }
}

// ---- Filter ----
function filterTable() {
  const search = document.getElementById('searchInput').value.trim().toUpperCase();
  const quadrant = document.getElementById('filterQuadrant').value;
  filteredData = allData.filter(d => {
    const matchSearch = !search || d.symbol.includes(search);
    const matchQuadrant = !quadrant || d.rrg === quadrant;
    return matchSearch && matchQuadrant;
  });
  sortAndRender();
}

// ---- Render ----
function renderTable() {
  const tbody = document.getElementById('tableBody');

  if (filteredData.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="9" style="text-align:center; padding:48px; color:var(--text-muted); font-size:14px;">
          Không tìm thấy cổ phiếu nào phù hợp
        </td>
      </tr>`;
    document.getElementById('rowCount').textContent = 'Hiển thị 0 mã';
    return;
  }

  tbody.innerHTML = filteredData.map((d, i) => {
    const totalPct = (d.total / 2.0 * 100).toFixed(0);
    const totalClass = d.total >= 1.5 ? 'high' : d.total >= 0.8 ? 'mid' : 'low';

    const bankerClass = d.banker_value >= 16 ? 'hot' : d.banker_value >= 8 ? 'warm' : 'cold';

    const rrgClass = {
      "TĂNG GIÁ": "rrg-leading",
      "TÍCH LŨY": "rrg-improving",
      "SUY YẾU":  "rrg-weakening",
      "GIẢM GIÁ": "rrg-lagging",
    }[d.rrg] || "rrg-lagging";

    const rrgDot = {
      "TĂNG GIÁ": "🟢",
      "TÍCH LŨY": "🔵",
      "SUY YẾU":  "🟠",
      "GIẢM GIÁ": "🔴",
    }[d.rrg] || "⚪";

    const rsRatioClass = d.rs_ratio >= 100 ? 'above100' : 'below100';
    const rsMomClass   = d.rs_mom   >= 100 ? 'above100' : 'below100';
    const tailClass    = d.tail_5d  >= 4   ? 'active'   : '';

    return `<tr>
      <td class="col-rank">${i + 1}</td>
      <td><span class="symbol-badge">${d.symbol}</span></td>
      <td>
        <div class="score-bar-wrap">
          <div class="score-bar">
            <div class="score-bar-fill" style="width:${totalPct}%"></div>
          </div>
          <span class="score-val ${totalClass}">${d.total.toFixed(2)}</span>
        </div>
      </td>
      <td><span class="score-val ${d.mcdx_score >= 0.8 ? 'high' : d.mcdx_score >= 0.4 ? 'mid' : 'low'}">${d.mcdx_score.toFixed(1)}</span></td>
      <td><span class="banker-value ${bankerClass}">${d.banker_value.toFixed(0)}</span></td>
      <td><span class="rrg-badge ${rrgClass}">${rrgDot} ${d.rrg}</span></td>
      <td><span class="num-cell ${rsRatioClass}">${d.rs_ratio.toFixed(2)}</span></td>
      <td><span class="num-cell ${rsMomClass}">${d.rs_mom.toFixed(2)}</span></td>
      <td><span class="tail-value ${tailClass}">${d.tail_5d.toFixed(2)}</span></td>
    </tr>`;
  }).join('');

  document.getElementById('rowCount').textContent = `Hiển thị ${filteredData.length} mã`;
}

// ---- Refresh simulation ----
let refreshInterval = null;

function startRefresh() {
  const btn = document.getElementById('btnRefresh');
  const icon = document.getElementById('refreshIcon');
  const dot  = document.getElementById('statusDot');
  const txt  = document.getElementById('updateText');
  const prog = document.getElementById('progressContainer');
  const bar  = document.getElementById('progressBar');
  const lbl  = document.getElementById('progressLabel');

  btn.disabled = true;
  btn.classList.add('loading');
  dot.classList.add('running');
  dot.classList.remove('error');
  txt.textContent = 'Đang cập nhật...';
  prog.classList.add('visible');

  const symbols = ["VCB","ACB","TCB","BID","CTG","VPB","MBB","STB","VIC","VHM",
                   "VNM","SAB","MSN","GAS","PLX","HPG","FPT","MWG","VRE","SSI"];
  let idx = 0;

  clearInterval(refreshInterval);
  refreshInterval = setInterval(() => {
    idx++;
    const pct = Math.min(Math.round((idx / symbols.length) * 100), 100);
    bar.style.width = pct + '%';
    lbl.textContent = `Đang xử lý ${symbols[idx - 1] || ''}... (${idx}/${symbols.length})`;

    if (idx >= symbols.length) {
      clearInterval(refreshInterval);
      setTimeout(() => {
        prog.classList.remove('visible');
        bar.style.width = '0%';
        btn.disabled = false;
        btn.classList.remove('loading');
        dot.classList.remove('running');
        const now = new Date();
        txt.textContent = `Cập nhật: ${now.toLocaleDateString('vi-VN')} ${now.toLocaleTimeString('vi-VN', {hour:'2-digit', minute:'2-digit'})}`;
      }, 800);
    }
  }, 250);
}

// ---- Export CSV ----
function exportCSV() {
  const headers = ['STT','Mã CP','Tổng điểm','MCDX Score','Banker Value','Vùng RRG','RS-Ratio','RS-Mom','Tail 5D'];
  const rows = filteredData.map((d, i) =>
    [i+1, d.symbol, d.total.toFixed(2), d.mcdx_score.toFixed(1), d.banker_value, d.rrg,
     d.rs_ratio.toFixed(2), d.rs_mom.toFixed(2), d.tail_5d.toFixed(2)].join(',')
  );
  const csv = [headers.join(','), ...rows].join('\n');
  const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8;' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `VN100_Score_${new Date().toISOString().slice(0,10)}.csv`;
  a.click();
}
