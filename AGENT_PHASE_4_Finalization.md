# AGENT PHASE 4: Finalization
**Duration**: 20 minutes  
**Steps**: 8-9  
**Output file**: `AGENT_PHASE_4_LOG.txt`  
**Prerequisite**: Phase 3 completed (tests passed or partial)  

---

## OVERVIEW

Phase 4 xác nhận dữ liệu đã lưu vào database và cập nhật tài liệu.

---

## STEP 8: VERIFY DATABASE (5 min)

### Test 8.1: Query database for recent records

```bash
.\venv\Scripts\python -c "
import sys, sqlite3, os
sys.path.insert(0, 'backend')
from database import get_latest_scores

# Query all categories
for category in ['vn30', 'vn100', 'custom']:
    try:
        scores = get_latest_scores(category)
        print(f'[{category.upper()}] Found {len(scores)} records')
        if scores:
            for s in scores[:2]:
                print(f'  - {s[\"symbol\"]}: {s[\"total_score\"]}')
    except Exception as e:
        print(f'[{category.upper()}] Error: {e}')
"
```

**Expected output**:
```
[VN30] Found X records
  - VCB: X.XX
  - VHM: X.XX
[VN100] Found X records
  - ...
[CUSTOM] Found X records
  - ...
```

**Log format:**
```
[TEST 8.1] Query database for recent records
  Command: .\venv\Scripts\python -c "..."
  Result: [OK]
  Records:
    - VN30: X records
    - VN100: X records
    - CUSTOM: X records
```

---

### Test 8.2: Check database file size

```bash
dir data\scores.db
```

**Expected output**: File listing with size > 0

**Log format:**
```
[TEST 8.2] Check database file size
  Command: dir data\scores.db
  Result: [OK]
  File size: X bytes
```

---

### STEP 8 RESULT

```
[STEP 8 RESULT] ✅ DATABASE VERIFIED
  Records persisted correctly
  Ready for STEP 9: YES
```

---

## STEP 9: UPDATE DOCUMENTATION (15 min)

### Action 9.1: Update HUONG_DAN_SU_DUNG.md

**File**: `HUONG_DAN_SU_DUNG.md`

**Replace entire content with**:

```markdown
# 📖 Hướng dẫn Sử dụng VN100 Stock Scorer (AmiBroker Version)

Hệ thống chấm điểm cổ phiếu tự động dựa trên **MCDX (Dòng tiền nhà cái)** và **RRG (Chu kỳ sức mạnh giá)** từ **AmiBroker**.

---

## 🚀 3 Bước Vận hành Hàng ngày

### Bước 1: Khởi động AmiBroker
- Mở ứng dụng **AmiBroker** (phải đang chạy để hệ thống lấy dữ liệu).
- Đảm bảo dữ liệu VN100 đã được load (File → Open → chọn database).

### Bước 2: Khởi động Dashboard
- Mở Terminal/PowerShell tại thư mục gốc dự án.
- Chạy lệnh:
  ```bash
  set DATA_SOURCE=amibroker
  .\venv\Scripts\python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
  ```
- Mở trình duyệt: `http://localhost:8000`

### Bước 3: Chấm điểm & Cập nhật
- Tại Dashboard, nhấn nút **"Cập nhật ngay"** cho danh mục mong muốn (VN30, VN100, Custom).
- Hệ thống sẽ lấy dữ liệu từ AmiBroker (~2 phút cho VN100).
- Kết quả hiển thị tự động sau khi hoàn thành.

---

## 🛠 Giải quyết sự cố thường gặp

1. **Lỗi "Cannot connect to AmiBroker"?**
   - Kiểm tra AmiBroker đã mở chưa.
   - Kiểm tra file `ami_bridge.afl` tồn tại tại `C:\Program Files (x86)\AmiBroker\Formulas\Custom\`.

2. **Điểm MCDX bằng 0?**
   - Kiểm tra FireAnt indicators đã cài trong AmiBroker (FA_MCDX, FA_RRG).
   - Mở AmiBroker Editor, chạy `ami_bridge.afl` thủ công để xem lỗi.

3. **Muốn dừng giữa chừng?**
   - Nhấn Ctrl+C trong Terminal để dừng server.

---

*Chúc bạn săn được những siêu cổ phiếu với dòng tiền cá mập mạnh nhất!* 📈
```

**Log format:**
```
[ACTION 9.1] Update HUONG_DAN_SU_DUNG.md
  File: HUONG_DAN_SU_DUNG.md
  Changes: Entire content replaced
  Status: [OK]
```

---

### Action 9.2: Update TECHNICAL_SPEC.md

**File**: `TECHNICAL_SPEC.md`

**Find**: Section "5. Quy trình Quét dữ liệu (Scoring Logic)"

**Replace with**:

```markdown
## 5. Quy trình Quét dữ liệu (Scoring Logic)
1.  **RRG Calculation**: Lấy dữ liệu từ AmiBroker qua OLE COM, tính RS-Ratio và RS-Momentum.
2.  **MCDX Scraping**:
    - Kết nối AmiBroker COM.
    - Chạy file AFL `ami_bridge.afl` để tính MCDX Banker.
    - Đọc giá trị từ StaticVar.
3.  **Final Scoring**: `Total = RRG_Score (0-1) + MCDX_Score (0-1)`.

### Prerequisites:
- AmiBroker 6.0+ (bản Crack hoạt động)
- FireAnt indicators cài trong AmiBroker
- pywin32 cài trong Python environment
```

**Log format:**
```
[ACTION 9.2] Update TECHNICAL_SPEC.md
  File: TECHNICAL_SPEC.md
  Section: 5. Quy trình Quét dữ liệu
  Changes: Replaced with AmiBroker workflow
  Status: [OK]
```

---

### Action 9.3: Update README.md

**File**: `README.md`

**Find**: Section "## Cách chạy"

**Replace with**:

```markdown
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
set DATA_SOURCE=amibroker
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
# Mở http://localhost:8000
```
```

**Log format:**
```
[ACTION 9.3] Update README.md
  File: README.md
  Section: Cách chạy
  Changes: Replaced with AmiBroker workflow
  Status: [OK]
```

---

### STEP 9 RESULT

```
[STEP 9 RESULT] ✅ DOCUMENTATION UPDATED
  Files updated: 3
  - HUONG_DAN_SU_DUNG.md
  - TECHNICAL_SPEC.md
  - README.md
  Ready for Phase 5: YES
```

---

## PHASE 4 FINAL REPORT

Create file: `AGENT_PHASE_4_LOG.txt`

```
================================================================================
AGENT PHASE 4 LOG — Finalization
Date: 2026-05-17
Duration: X minutes
Status: ✅ COMPLETED
================================================================================

[STEP 8] VERIFY DATABASE
  [TEST 8.1] Query database for recent records ... [OK]
    - VN30: X records
    - VN100: X records
    - CUSTOM: X records
  [TEST 8.2] Check database file size ... [OK]
    - File size: X bytes
  [RESULT] Database verified

[STEP 9] UPDATE DOCUMENTATION
  [ACTION 9.1] Update HUONG_DAN_SU_DUNG.md ... [OK]
  [ACTION 9.2] Update TECHNICAL_SPEC.md ... [OK]
  [ACTION 9.3] Update README.md ... [OK]
  [RESULT] Documentation updated

[PHASE 4 RESULT] ✅ COMPLETED
  All steps passed
  Ready for Phase 5: YES

[NOTES]
- (any issues encountered, etc.)

================================================================================
```

---

## NEXT STEP

After Phase 4 completes:
1. Agent reports: "Phase 4 completed. Log: AGENT_PHASE_4_LOG.txt"
2. User reviews log
3. User approves: "Phase 4 OK. Proceed to Phase 5."
4. Agent reads: `AGENT_PHASE_5_Checklist.md`
