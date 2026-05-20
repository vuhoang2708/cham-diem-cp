# Implementation Plan: AmiBroker Connector — Detailed Execution Script
**Agent**: Antigravity  
**Date**: 2026-05-17  
**Reviewer**: User (kiểm tra sau khi agent chạy xong)  
**Mục tiêu**: Hoàn thành việc chuyển nguồn dữ liệu từ Playwright/Fireant sang AmiBroker OLE/COM.

---

## TRẠNG THÁI HIỆN TẠI (trước khi chạy plan này)

| File | Trạng thái |
|---|---|
| `backend/ami_bridge.afl` | ✅ Đã có |
| `backend/test_ami_connector.py` | ✅ Đã có (nhưng có lỗi COM API — xem Task 1) |
| `backend/scraper_amibroker.py` | ❌ Chưa tồn tại — cần tạo mới |
| `backend/main_scorer.py` | ❌ Vẫn dùng MCDXScraper (Playwright) — cần sửa |
| `requirements.txt` | ✅ Đã có `pywin32` |

---

## PRE-CONDITIONS (Agent kiểm tra trước khi bắt đầu)

Trước khi chạy bất kỳ task nào, agent phải xác nhận:

1. **pywin32 đã cài**: Chạy `python -c "import win32com.client; print('OK')"` trong venv.
2. **ami_bridge.afl đã copy vào AmiBroker**: File phải tồn tại tại `C:\Program Files (x86)\AmiBroker\Formulas\Custom\ami_bridge.afl` HOẶC `C:\Program Files\AmiBroker\Formulas\Custom\ami_bridge.afl`.
3. **AmiBroker đang mở**: Không thể test COM nếu AmiBroker chưa chạy.

Nếu bất kỳ điều kiện nào fail → **dừng lại và báo cáo** cho user, không tiếp tục.

---

## TASK 1: Sửa lỗi COM API trong test_ami_connector.py

**Vấn đề**: Hàm `get_stock_data()` trong `test_ami_connector.py` dùng sai API:
- `analysis.Filter(0, "x")` — không phải AmiBroker COM API
- `analysis.Scan(0)` — không đúng

**Cách sửa**: Thay bằng cơ chế đúng — dùng `ab.ActiveDocument` để set symbol và chạy formula trực tiếp.

### Script sửa `backend/test_ami_connector.py` — hàm `get_stock_data()`:

```python
def get_stock_data(ab, symbol):
    """
    Set symbol in AmiBroker, run the bridge AFL via Analyze,
    then read back StaticVar results.
    """
    import time

    # 1. Reset ready flag trước khi chạy
    ab.StaticVarSet("ag_ready", 0)

    # 2. Set symbol hiện tại trong AmiBroker
    ab.Stocks(symbol).Selected = True
    # Hoặc dùng: ab.ActiveDocument.Name = symbol (tùy phiên bản)

    # 3. Mở Analysis document với bridge AFL
    # Đường dẫn tương đối trong AmiBroker Formulas folder
    analysis = ab.AnalysisDocs.Open(BRIDGE_AFL)
    if analysis is None:
        print(f"[FAIL] Cannot open '{BRIDGE_AFL}'. Check AmiBroker Formulas folder.")
        return None

    # 4. Chạy Scan cho symbol hiện tại (1 mã, bar cuối)
    analysis.SetFilterIncludeWatchlist(0)  # Không dùng watchlist
    analysis.SetFilterSymbol(symbol)       # Chỉ scan mã này
    analysis.Run(0)                        # 0 = Scan mode

    # 5. Poll cho đến khi ag_ready = 1 (max TIMEOUT_SECS)
    start = time.time()
    while True:
        ready = ab.StaticVarGet("ag_ready")
        if ready == 1:
            break
        if time.time() - start > TIMEOUT_SECS:
            print(f"[WARN] Timeout: AmiBroker did not set ag_ready=1 within {TIMEOUT_SECS}s")
            break
        time.sleep(0.3)

    # 6. Đọc kết quả
    results = {
        "symbol":   symbol,
        "banker":   ab.StaticVarGet("ag_banker"),
        "hotmoney": ab.StaticVarGet("ag_hotmoney"),
        "rs_ratio": ab.StaticVarGet("ag_rs_ratio"),
        "rs_mom":   ab.StaticVarGet("ag_rs_mom"),
        "quadrant": int(ab.StaticVarGet("ag_quadrant")),
        "tail_5d":  ab.StaticVarGet("ag_tail_5d"),
    }
    return results
```

**Lưu ý quan trọng**: AmiBroker COM API có thể khác nhau giữa các phiên bản. Nếu `SetFilterSymbol` không tồn tại, thử:
```python
analysis.Filter(0, "x")  # Clear
analysis.Filter(symbol, "x")  # Set symbol
```

---

## TASK 2: Tạo `backend/scraper_amibroker.py`

Đây là module chính thay thế `scraper_mcdx.py`. Phải có interface tương thích để `main_scorer.py` có thể swap dễ dàng.

### File cần tạo: `backend/scraper_amibroker.py`

```python
"""
AmiBroker Scraper — thay thế scraper_mcdx.py
Lấy dữ liệu MCDX Banker + RRG từ AmiBroker qua OLE COM.
"""
import time
import sys

try:
    import win32com.client
    import pywintypes
    HAS_PYWIN32 = True
except ImportError:
    HAS_PYWIN32 = False

BRIDGE_AFL   = "Custom\\ami_bridge.afl"
TIMEOUT_SECS = 15


class AmiConnector:
    """Kết nối AmiBroker COM và lấy dữ liệu cho từng mã CP."""

    def __init__(self):
        self.ab = None
        self.analysis = None

    def connect(self) -> bool:
        """Kết nối tới AmiBroker đang chạy. Trả về True nếu thành công."""
        if not HAS_PYWIN32:
            print("[AmiConnector] ERROR: pywin32 not installed. Run: pip install pywin32")
            return False
        try:
            self.ab = win32com.client.Dispatch("Broker.Application")
            print(f"[AmiConnector] Connected to AmiBroker v{self.ab.Version}")
            # Mở analysis document một lần, dùng lại cho tất cả mã
            self.analysis = self.ab.AnalysisDocs.Open(BRIDGE_AFL)
            if self.analysis is None:
                print(f"[AmiConnector] WARN: Cannot open '{BRIDGE_AFL}'. Check Formulas/Custom/ folder.")
                return False
            return True
        except Exception as e:
            print(f"[AmiConnector] Cannot connect to AmiBroker: {e}")
            print("  -> Make sure AmiBroker is OPEN before running.")
            return False

    def disconnect(self):
        """Đóng analysis document."""
        try:
            if self.analysis:
                self.analysis.Close()
        except Exception:
            pass
        self.ab = None
        self.analysis = None

    def get_data(self, symbol: str) -> dict | None:
        """
        Lấy dữ liệu MCDX + RRG cho một mã CP.
        Trả về dict hoặc None nếu lỗi.
        """
        if not self.ab or not self.analysis:
            return None
        try:
            # Reset cờ ready
            self.ab.StaticVarSet("ag_ready", 0)

            # Set symbol và chạy scan
            self.analysis.SetFilterSymbol(symbol)
            self.analysis.Run(0)  # 0 = Scan

            # Chờ kết quả
            start = time.time()
            while True:
                if self.ab.StaticVarGet("ag_ready") == 1:
                    break
                if time.time() - start > TIMEOUT_SECS:
                    print(f"[AmiConnector] Timeout for {symbol}")
                    return None
                time.sleep(0.2)

            # Đọc kết quả
            banker   = self.ab.StaticVarGet("ag_banker")
            hotmoney = self.ab.StaticVarGet("ag_hotmoney")
            rs_ratio = self.ab.StaticVarGet("ag_rs_ratio")
            rs_mom   = self.ab.StaticVarGet("ag_rs_mom")
            quadrant = int(self.ab.StaticVarGet("ag_quadrant"))
            tail_5d  = self.ab.StaticVarGet("ag_tail_5d")

            return {
                "symbol":   symbol,
                "banker":   banker,
                "hotmoney": hotmoney,
                "rs_ratio": rs_ratio,
                "rs_mom":   rs_mom,
                "quadrant": quadrant,
                "tail_5d":  tail_5d,
                # Tính điểm ngay tại đây
                "mcdx_score": _score_banker(banker),
                "rrg_score":  _score_rrg(quadrant),
                # Tương thích với interface cũ của scraper_mcdx
                "banker_left":  banker,
                "banker_right": hotmoney,
                "banker_value": banker,
            }
        except Exception as e:
            print(f"[AmiConnector] Error getting data for {symbol}: {e}")
            return None


def _score_banker(value: float) -> float:
    """Nội suy tuyến tính: 0→0, 3→0.2, 8→0.4, 12→0.6, 16→0.8, 20→1.0"""
    breakpoints = [(0, 0.0), (3, 0.2), (8, 0.4), (12, 0.6), (16, 0.8), (20, 1.0)]
    if value <= 0:  return 0.0
    if value >= 20: return 1.0
    for i in range(len(breakpoints) - 1):
        x0, y0 = breakpoints[i]
        x1, y1 = breakpoints[i + 1]
        if x0 <= value <= x1:
            return round(y0 + (y1 - y0) * (value - x0) / (x1 - x0), 4)
    return 0.0


def _score_rrg(quadrant: int) -> float:
    """1=Leading→1.0, 4=Improving→0.75, 2=Weakening→0.5, 3=Lagging→0.25"""
    return {1: 1.0, 4: 0.75, 2: 0.5, 3: 0.25}.get(quadrant, 0.0)
```

---

## TASK 3: Sửa `backend/main_scorer.py` — thêm AmiBroker mode

Không xóa Playwright scraper cũ. Thêm logic chọn nguồn dữ liệu qua biến môi trường `DATA_SOURCE`.

### Thay đổi trong `main_scorer.py`:

**Thêm import ở đầu file:**
```python
import os
USE_AMIBROKER = os.environ.get("DATA_SOURCE", "fireant").lower() == "amibroker"
```

**Thay đổi phần khởi tạo scraper (khoảng dòng 37-42):**

Thay:
```python
# Setup Scraper
scraper = MCDXScraper()
connected = await scraper.connect()
if not connected:
    print("Critical Error: Could not connect to Chrome CDP.")
    return
```

Thành:
```python
# Setup data source
if USE_AMIBROKER:
    from scraper_amibroker import AmiConnector
    connector = AmiConnector()
    if not connector.connect():
        print("Critical Error: Cannot connect to AmiBroker. Is it open?")
        return
else:
    scraper = MCDXScraper()
    connected = await scraper.connect()
    if not connected:
        print("Critical Error: Could not connect to Chrome CDP.")
        return
```

**Thay đổi phần lấy dữ liệu trong vòng lặp (khoảng dòng 55-57):**

Thay:
```python
# 2. MCDX Scraping (Banker Value, MCDX Score)
mcdx_res = await scraper.get_banker_value(symbol)
```

Thành:
```python
# 2. Lấy dữ liệu MCDX + RRG
if USE_AMIBROKER:
    ami_res = connector.get_data(symbol)
    if ami_res:
        # AmiBroker cung cấp cả RRG lẫn MCDX — override rrg_res
        mcdx_res = ami_res
        rrg_res = {
            "rrg_score": ami_res["rrg_score"],
            "quadrant":  ami_res["quadrant"],
            "rs_ratio":  ami_res["rs_ratio"],
            "rs_mom":    ami_res["rs_mom"],
            "tail_5d":   ami_res["tail_5d"],
        }
    else:
        mcdx_res = None
else:
    mcdx_res = await scraper.get_banker_value(symbol)
```

**Thêm cleanup sau vòng lặp:**
```python
# Cleanup
if USE_AMIBROKER:
    connector.disconnect()
else:
    await scraper.disconnect()
```

---

## TASK 4: Kiểm tra & Xác nhận

### Bước 4a — Test kết nối AmiBroker (chạy với AmiBroker đang mở):
```bash
cd "c:\Users\Nguyen To Dung\.gemini\antigravity\scratch\Cham diem co phieu"
.\venv\Scripts\python backend\test_ami_connector.py
```

**Kết quả mong đợi:**
```
[OK] Connected to AmiBroker: version X.X
[INFO] Fetching data for symbol: VCB ...
  MCDX Banker Value : X.XXXX
  RRG Quadrant      : LEADING/WEAKENING/LAGGING/IMPROVING
  TỔNG ĐIỂM         : X.XXXX / 2.0
[SUCCESS] AmiBroker connection test passed!
```

### Bước 4b — Test scraper_amibroker.py độc lập:
```bash
.\venv\Scripts\python -c "
from backend.scraper_amibroker import AmiConnector
c = AmiConnector()
if c.connect():
    data = c.get_data('VCB')
    print(data)
    c.disconnect()
"
```

### Bước 4c — Test full scoring pipeline với AmiBroker:
```bash
set DATA_SOURCE=amibroker
.\venv\Scripts\python -c "
import asyncio, sys
sys.path.insert(0, 'backend')
import main_scorer
asyncio.run(main_scorer.run_scoring(category='vn30', symbols=['VCB', 'VHM', 'TCB']))
"
```

### Bước 4d — So sánh kết quả:
Mở Dashboard tại `http://localhost:8000` (hoặc 8888), so sánh giá trị Banker và Vùng RRG với màn hình AmiBroker cho ít nhất 3 mã.

---

## TASK 5: Cập nhật tài liệu

### 5a — Sửa `HUONG_DAN_SU_DUNG.md`:
Thay toàn bộ nội dung bằng workflow mới:
- Bước 1: Mở AmiBroker (không cần Chrome/Fireant)
- Bước 2: Chạy `set DATA_SOURCE=amibroker && uvicorn backend.main:app`
- Bước 3: Vào Dashboard, nhấn "Cập nhật ngay"

### 5b — Sửa `TECHNICAL_SPEC.md`:
- Cập nhật mục 5 "Quy trình Quét dữ liệu" để phản ánh AmiBroker COM thay vì Playwright
- Thêm mục về prerequisite: AmiBroker + FireAnt indicators

### 5c — Sửa `README.md`:
- Thống nhất cổng server (8000 hay 8888 — chọn 1)
- Xóa đề cập Vercel (tính năng chưa implement)
- Cập nhật "Cách chạy" theo workflow AmiBroker

---

## CHECKLIST CUỐI (Agent báo cáo từng mục)

- [ ] pywin32 import thành công
- [ ] ami_bridge.afl tìm thấy trong AmiBroker Formulas folder
- [ ] test_ami_connector.py chạy không lỗi
- [ ] scraper_amibroker.py đã tạo
- [ ] main_scorer.py đã sửa, DATA_SOURCE=amibroker hoạt động
- [ ] VCB test: Banker value khớp với AmiBroker UI
- [ ] VCB test: RRG Quadrant khớp với AmiBroker UI
- [ ] Tài liệu đã cập nhật

---

## GHI CHÚ CHO REVIEWER (User kiểm tra sau)

1. **Nếu `SetFilterSymbol` không tồn tại** trong phiên bản AmiBroker của bạn → thử `analysis.Filter(symbol, "x")` và báo lại để sửa plan.
2. **Nếu ag_ready không bao giờ = 1** → AmiBroker có thể không chạy AFL trong Scan mode. Thử dùng `Explore` mode thay vì `Scan`.
3. **Nếu giá trị Banker luôn = 0** → Kiểm tra `#include_once <FireAnt.h>` trong ami_bridge.afl có load được không. Mở AFL trong AmiBroker Editor và chạy thử.
4. **Race condition**: Nếu chạy nhiều mã liên tiếp mà kết quả bị lẫn lộn → cần thêm symbol prefix vào StaticVar names (ag_banker_VCB, ag_banker_VHM...) và sửa cả AFL lẫn Python.
