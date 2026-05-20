# Plan: Hướng tiếp cận mới — Lấy dữ liệu FA_MCDX/FA_RRG từ AmiBroker

**Ngày**: 2026-05-17  
**Bối cảnh**: COM automation approach bị block bởi 2 vấn đề: `fopen` không ghi file và không filter được 1 symbol.

---

## Phân tích root cause thực sự

### Tại sao `fopen` không ghi file?

AmiBroker khi chạy scan qua COM có thể bị ảnh hưởng bởi **UAC File System Virtualization** — Windows redirect write vào `C:\Windows\Temp` sang `VirtualStore` của user. File thực sự được ghi vào:
```
C:\Users\Nguyen To Dung\AppData\Local\VirtualStore\Windows\Temp\ag_bridge_out.txt
```

Đây là lý do Python không tìm thấy file ở path gốc.

### Tại sao scan chậm?

`ApplyTo=0` = tất cả symbols trong database. AmiBroker không expose API để set filter symbol từ COM trong bản 6.30 crack này.

---

## Hướng tiếp cận mới — 3 options

### Option A: Fix VirtualStore path (Nhanh nhất, thử trước)

**Ý tưởng**: Python đọc file từ VirtualStore thay vì `C:\Windows\Temp`.

**Bước thực hiện**:
1. Chạy scan như hiện tại (ApplyTo=0, FormulaPath)
2. Sau khi scan xong, đọc file từ:
   ```
   C:\Users\Nguyen To Dung\AppData\Local\VirtualStore\Windows\Temp\ag_bridge_out.txt
   ```
3. Nếu có file → vấn đề chỉ là path, fix ngay được

**Ưu điểm**: Không cần thay đổi AFL, không cần thay đổi approach  
**Nhược điểm**: Vẫn phải scan 8887 symbols (89s/lần) — chậm

**Thời gian thử**: 5 phút

---

### Option B: Scan 1 symbol bằng Watchlist thủ công (Khả thi nhất)

**Ý tưởng**: Tạo sẵn 1 Watchlist trong AmiBroker (ví dụ Watchlist #0 tên "AG_Bridge"), dùng `ApplyTo=3` (watchlist) trong .apx. Trước mỗi scan, Python xóa watchlist cũ và thêm symbol mới vào bằng cách **ghi trực tiếp vào file watchlist của AmiBroker**.

**AmiBroker lưu watchlist tại**:
```
C:\Program Files (x86)\AmiBroker\Broker.newcharts  (hoặc)
C:\Users\Nguyen To Dung\AppData\Roaming\AmiBroker\
```

**Bước thực hiện**:
1. Tìm file watchlist của AmiBroker (binary hoặc text)
2. Viết Python script để update watchlist file với 1 symbol
3. Gọi `ab.RefreshAll()` để AmiBroker reload watchlist
4. Chạy scan với `ApplyTo=3, WatchlistIndex=X`
5. Đọc output

**Ưu điểm**: Scan chỉ 1 symbol → ~1-2 giây  
**Nhược điểm**: Cần reverse-engineer format watchlist file

**Thời gian thử**: 30-60 phút

---

### Option C: Dùng AmiBroker OLE Automation đúng cách — `ab.Import()` + chart formula (Robust nhất)

**Ý tưởng**: Thay vì dùng Analysis scan, dùng **chart formula** — set symbol trên chart, trigger recalculation, đọc kết quả qua `ab.GetLastQuotation()` hoặc custom output.

**Cụ thể**:
1. Dùng `ab.LoadDatabase()` để đảm bảo data loaded
2. Dùng `ab.Documents` để tìm chart window đang mở
3. Set symbol trên chart window
4. Trigger formula recalculation
5. Đọc kết quả từ file (chart formula cũng có thể dùng `fopen`)

**Hoặc approach khác trong Option C**:
- Dùng **AmiBroker AFL Editor** qua COM để chạy formula trực tiếp
- Dùng `ab.Documents.Open()` để mở chart với formula

**Thời gian thử**: 1-2 giờ

---

### Option D: Bỏ COM, dùng AmiBroker Export trực tiếp (Đơn giản nhất)

**Ý tưởng**: Không dùng COM automation. Thay vào đó:
1. Tạo sẵn 1 AFL formula trong AmiBroker chạy **tự động theo lịch** (RunEvery=5min hoặc dùng AmiBroker Scheduler)
2. Formula này scan VN100 watchlist và ghi kết quả ra file CSV/JSON
3. Python chỉ đọc file đó — không cần COM

**Bước thực hiện**:
1. Tạo watchlist VN100 trong AmiBroker (100 symbols)
2. Tạo AFL formula scan VN100, ghi ra `C:\Users\Public\vn100_scores.json`
3. Set `RunEvery=5min` trong Analysis window
4. Python đọc file JSON thay vì gọi COM

**Ưu điểm**: Đơn giản, không cần COM, không bị block bởi API limitations  
**Nhược điểm**: Cần setup thủ công trong AmiBroker UI, data có thể stale (5 phút)

**Thời gian setup**: 20-30 phút

---

### Option E: Giữ Fireant nhưng tối ưu tốc độ (Fallback an toàn)

**Ý tưởng**: Thay vì thay thế hoàn toàn, tối ưu Playwright scraper hiện tại:
- Chạy parallel 10 symbols cùng lúc thay vì tuần tự
- Cache kết quả 24h (dữ liệu MCDX không thay đổi trong ngày)
- Chỉ refresh symbols có trong watchlist hôm nay

**Ước tính**: 75 phút → ~8-10 phút với parallel 10x

---

## Khuyến nghị thứ tự thử

```
1. Option A (5 phút)  → Check VirtualStore path
   ↓ nếu không có file
2. Option D (30 phút) → Setup AmiBroker auto-export
   ↓ nếu muốn real-time
3. Option B (1 giờ)   → Watchlist file manipulation
   ↓ nếu vẫn muốn COM
4. Option E (fallback) → Optimize Fireant parallel
```

---

## Action items ngay bây giờ

### Kiểm tra VirtualStore (Option A — 5 phút)

```powershell
# Chạy scan 1 lần, sau đó check:
$vstore = "$env:LOCALAPPDATA\VirtualStore\Windows\Temp\ag_bridge_out.txt"
if (Test-Path $vstore) { Get-Content $vstore }
```

### Nếu Option A thất bại — Setup Option D

1. Mở AmiBroker
2. Symbol → Watchlist → New → đặt tên "VN100"
3. Thêm 100 symbols VN100 vào watchlist
4. Analysis → New → load formula `ami_bridge_export.afl` (ghi JSON)
5. Set Apply To = Watchlist "VN100", RunEvery = 5min
6. Python đọc file JSON

---

## Thay đổi cần làm trong code

### Nếu Option A thành công (chỉ fix path):
```python
# scraper_amibroker.py
import os
VSTORE = os.path.expandvars(
    r"%LOCALAPPDATA%\VirtualStore\Windows\Temp\ag_bridge_out.txt"
)
OUTPUT_FILE = VSTORE if os.path.exists(os.path.dirname(VSTORE)) else r"C:\Windows\Temp\ag_bridge_out.txt"
```

### Nếu Option D (file-based export):
```python
# scraper_amibroker.py — đọc từ pre-generated JSON
import json, os
EXPORT_FILE = r"C:\Users\Public\vn100_scores.json"

def get_data(symbol: str) -> dict | None:
    if not os.path.exists(EXPORT_FILE):
        return None
    with open(EXPORT_FILE) as f:
        data = json.load(f)
    return data.get(symbol)
```

---

## Ghi chú kỹ thuật

- AmiBroker 6.30 (crack) — không có type library, late binding only
- COM API rất hạn chế: chỉ có `AnalysisDocs`, `Stocks`, `Documents`, `RefreshAll`, `Import`, `LoadDatabase`
- `CategoryAddSymbol` không tồn tại trong bản này
- `fopen` trong AFL có thể bị redirect bởi UAC virtualization
- 32-bit Python bắt buộc (venv32 tại project root)
- Scan 8887 symbols với FA_MCDX mất ~89 giây
