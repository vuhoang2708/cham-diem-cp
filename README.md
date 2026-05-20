# VN100 Stock Scorer 📈

Dashboard tự động chấm điểm và xếp hạng cổ phiếu trong danh mục **VN100** dựa trên:

- **MCDX Banker Smart Money** — Chỉ số dòng tiền lớn từ Fireant.vn
- **RRG Quadrant** — Vị trí vùng Relative Rotation Graph (tính từ giá)

## Tính năng

- ✅ Bảng xếp hạng cổ phiếu theo điểm tổng (cao → thấp)
- ✅ Hiển thị: Tổng điểm | MCDX score | Banker value | Vùng RRG | RS-Ratio | RS-Mom | Tail 5D
- ✅ Filter theo vùng RRG, tìm kiếm theo mã CP
- ✅ Export CSV
- ✅ Tự động cập nhật lúc 16:05 hàng ngày
- ✅ Nút Refresh thủ công với progress bar realtime

## Cách chạy

### 1. Cài đặt môi trường
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Khởi động AmiBroker
Mở ứng dụng AmiBroker (phải đang chạy).

### 3. Chạy Dashboard
```bash
$env:DATA_SOURCE="amibroker"
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
# Mở http://localhost:8000
```

## Kiến trúc

```
├── backend/
│   ├── test_playwright.py     # Test kết nối Chrome CDP
│   ├── test_tcbs_api.py       # Test tính toán RRG
│   └── (các module đang xây dựng)
├── frontend/
│   ├── index.html             # Dashboard UI
│   ├── style.css              # Dark theme
│   └── app.js                 # Logic + mock data
├── data/                      # Dữ liệu (không commit)
├── start_chrome.bat           # Khởi động Chrome với CDP
└── requirements.txt
```

## Thang điểm

| Tiêu chí | Thang điểm |
|---|---|
| MCDX Banker: 0→3→8→12→16→20 | 0→0.2→0.4→0.6→0.8→1.0 (nội suy tuyến tính) |
| RRG Tăng giá (Leading) | 1.00 |
| RRG Tích lũy (Improving) | 0.75 |
| RRG Suy yếu (Weakening) | 0.50 |
| RRG Giảm giá (Lagging) | 0.25 |
| **Tổng điểm tối đa** | **2.00** |
