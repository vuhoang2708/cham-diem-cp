# AGENT EXECUTION PROMPT — AmiBroker Connector Implementation
**Target Agent**: Antigravity (or any capable agent)  
**Date**: 2026-05-17  
**Task**: Hoàn thành việc chuyển nguồn dữ liệu từ Playwright/Fireant sang AmiBroker OLE/COM  
**Expected Duration**: ~2-3 giờ  
**Output Format**: Structured log file + checklist verification

---

## CONTEXT & BACKGROUND

Dự án VN100 Stock Scoring Dashboard hiện đang sử dụng Playwright để scrape dữ liệu MCDX từ Fireant (chậm ~75 phút cho 100 mã). Plan mới đề xuất chuyển sang AmiBroker OLE/COM (nhanh ~2 phút cho 100 mã).

**Trạng thái hiện tại:**
- ✅ `backend/ami_bridge.afl` — đã tạo (file AFL để AmiBroker tính toán)
- ✅ `backend/test_ami_connector.py` — đã tạo (nhưng có lỗi COM API)
- ❌ `backend/scraper_amibroker.py` — chưa tạo (module Python chính)
- ❌ `backend/main_scorer.py` — chưa sửa (vẫn dùng Playwright)

**Tài liệu tham khảo:**
- Chi tiết plan: `Implementation Plan/implementation_plan_20260517_AmiConnector_Detailed.md`
- Hệ thống hiện tại: `TECHNICAL_SPEC.md`, `README.md`

---

## EXECUTION STEPS (Tuần tự, không bỏ qua)

### STEP 1: PRE-FLIGHT CHECKS (5 phút)
**Mục tiêu**: Xác nhận môi trường sẵn sàng trước khi code.

**Hành động:**
1. Kiểm tra pywin32 đã cài:
   ```bash
   cd "c:\Users\Nguyen To Dung\.gemini\antigravity\scratch\Cham diem co phieu"
   .\venv\Scripts\python -c "import win32com.client; print('[OK] pywin32 imported')"
   ```
   - Nếu fail → báo lỗi và dừng

2. Kiểm tra ami_bridge.afl tồn tại:
   ```bash
   dir "C:\Program Files (x86)\AmiBroker\Formulas\Custom\ami_bridge.afl"
   ```
   - Nếu không tìm thấy → thử `C:\Program Files\AmiBroker\Formulas\Custom\ami_bridge.afl`
   - Nếu vẫn không có → báo lỗi: "ami_bridge.afl not found in AmiBroker Formulas folder"

3. Kiểm tra backend/ami_bridge.afl (source) tồn tại:
   ```bash
   dir backend\ami_bridge.afl
   ```

**Output log format:**
```
[STEP 1] PRE-FLIGHT CHECKS
  [CHECK 1.1] pywin32 import ... [OK] / [FAIL]
  [CHECK 1.2] AmiBroker Formulas folder ... [OK] / [FAIL]
  [CHECK 1.3] backend/ami_bridge.afl source ... [OK] / [FAIL]
  [RESULT] All checks passed / BLOCKED: <reason>
```

---

### STEP 2: FIX test_ami_connector.py (15 phút)
**Mục tiêu**: Sửa lỗi COM API trong hàm `get_stock_data()`.

**Hành động:**
1. Mở file `backend/test_ami_connector.py`
2. Tìm hàm `get_stock_data(ab, symbol)` (khoảng dòng 52-98)
3. Thay toàn bộ hàm bằng code mới từ plan (TASK 2 section)
4. Lưu file

**Verification:**
```bash
.\venv\Scripts\python -m py_compile backend\test_ami_connector.py
```
- Nếu syntax error → báo lỗi, không tiếp tục

**Output log format:**
```
[STEP 2] FIX test_ami_connector.py
  [ACTION 2.1] Replace get_stock_data() function ... [OK]
  [ACTION 2.2] Syntax check ... [OK] / [FAIL: <error>]
  [RESULT] File fixed and validated
```

---

### STEP 3: CREATE backend/scraper_amibroker.py (30 phút)
**Mục tiêu**: Tạo module Python mới để kết nối AmiBroker.

**Hành động:**
1. Tạo file mới: `backend/scraper_amibroker.py`
2. Copy toàn bộ code từ plan (TASK 3 section) vào file
3. Lưu file
4. Syntax check:
   ```bash
   .\venv\Scripts\python -m py_compile backend\scraper_amibroker.py
   ```

**Verification:**
```bash
.\venv\Scripts\python -c "from backend.scraper_amibroker import AmiConnector; print('[OK] Module imported')"
```
- Nếu import fail → báo lỗi

**Output log format:**
```
[STEP 3] CREATE backend/scraper_amibroker.py
  [ACTION 3.1] Create file ... [OK]
  [ACTION 3.2] Copy code from plan ... [OK]
  [ACTION 3.3] Syntax check ... [OK] / [FAIL: <error>]
  [ACTION 3.4] Import test ... [OK] / [FAIL: <error>]
  [RESULT] Module created and validated
```

---

### STEP 4: MODIFY backend/main_scorer.py (20 phút)
**Mục tiêu**: Thêm logic chọn nguồn dữ liệu (AmiBroker vs Playwright).

**Hành động:**
1. Mở file `backend/main_scorer.py`
2. Thêm import ở đầu file (sau dòng `import asyncio`):
   ```python
   import os
   USE_AMIBROKER = os.environ.get("DATA_SOURCE", "fireant").lower() == "amibroker"
   ```
3. Tìm dòng `scraper = MCDXScraper()` (khoảng dòng 37)
4. Thay section "Setup Scraper" bằng code mới từ plan (TASK 4 section)
5. Tìm dòng `mcdx_res = await scraper.get_banker_value(symbol)` (khoảng dòng 56)
6. Thay section "MCDX Scraping" bằng code mới từ plan
7. Thêm cleanup section trước `return` cuối hàm
8. Lưu file

**Verification:**
```bash
.\venv\Scripts\python -m py_compile backend\main_scorer.py
```

**Output log format:**
```
[STEP 4] MODIFY backend/main_scorer.py
  [ACTION 4.1] Add USE_AMIBROKER import ... [OK]
  [ACTION 4.2] Replace scraper initialization ... [OK]
  [ACTION 4.3] Replace MCDX scraping logic ... [OK]
  [ACTION 4.4] Add cleanup section ... [OK]
  [ACTION 4.5] Syntax check ... [OK] / [FAIL: <error>]
  [RESULT] File modified and validated
```

---

### STEP 5: TEST — test_ami_connector.py (10 phút)
**Mục tiêu**: Xác nhận kết nối AmiBroker hoạt động.

**Hành động:**
1. Đảm bảo AmiBroker đang mở
2. Chạy test:
   ```bash
   .\venv\Scripts\python backend\test_ami_connector.py
   ```

**Expected output:**
```
============================================================
  ANTIGRAVITY — AmiBroker Connection Test
============================================================

[OK] Connected to AmiBroker: version X.X
[INFO] Fetching data for symbol: VCB ...

============================================================
  Kết quả cho mã: VCB
============================================================
  MCDX Banker Value : X.XXXX
  MCDX HotMoney     : X.XXXX
  MCDX Score        : X.XX / 1.0
------------------------------------------------------------
  RRG RS-Ratio (X)  : XXX.XXXX
  RRG RS-Mom   (Y)  : XXX.XXXX
  RRG Quadrant      : LEADING/WEAKENING/LAGGING/IMPROVING
  RRG Score         : X.XX / 1.0
  RRG Tail 5D       : X.XXXX (tham khảo)
------------------------------------------------------------
  TỔNG ĐIỂM         : X.XX / 2.0
============================================================

[SUCCESS] AmiBroker connection test passed!
```

**Nếu fail:**
- Lỗi "Cannot connect to AmiBroker" → AmiBroker chưa mở
- Lỗi "Cannot open ami_bridge.afl" → File chưa copy vào Formulas/Custom/
- Lỗi "Timeout" → AmiBroker không chạy AFL đúng cách (xem ghi chú cuối)

**Output log format:**
```
[STEP 5] TEST — test_ami_connector.py
  [TEST 5.1] AmiBroker connection ... [OK] / [FAIL: <error>]
  [TEST 5.2] VCB data fetch ... [OK] / [FAIL: <error>]
  [TEST 5.3] Score calculation ... [OK] / [FAIL: <error>]
  [RESULT] Test passed / BLOCKED: <reason>
  [DATA] Banker=X.XX, Quadrant=<name>, Total=X.XX
```

---

### STEP 6: TEST — scraper_amibroker.py (10 phút)
**Mục tiêu**: Xác nhận module scraper_amibroker hoạt động độc lập.

**Hành động:**
```bash
.\venv\Scripts\python -c "
import sys
sys.path.insert(0, 'backend')
from scraper_amibroker import AmiConnector
c = AmiConnector()
if c.connect():
    data = c.get_data('VCB')
    if data:
        print('[OK] Data retrieved:')
        print(f'  Banker: {data[\"banker\"]}')
        print(f'  Quadrant: {data[\"quadrant\"]}')
        print(f'  MCDX Score: {data[\"mcdx_score\"]}')
        print(f'  RRG Score: {data[\"rrg_score\"]}')
    else:
        print('[FAIL] get_data returned None')
    c.disconnect()
else:
    print('[FAIL] Cannot connect')
"
```

**Output log format:**
```
[STEP 6] TEST — scraper_amibroker.py
  [TEST 6.1] Module import ... [OK]
  [TEST 6.2] AmiConnector.connect() ... [OK] / [FAIL: <error>]
  [TEST 6.3] AmiConnector.get_data('VCB') ... [OK] / [FAIL: <error>]
  [RESULT] Module works correctly
  [DATA] Banker=X.XX, Quadrant=<name>, Scores=X.XX/X.XX
```

---

### STEP 7: TEST — Full Pipeline (15 phút)
**Mục tiêu**: Xác nhận main_scorer.py hoạt động với AmiBroker.

**Hành động:**
1. Chạy scoring cho 3 mã test:
   ```bash
   set DATA_SOURCE=amibroker
   .\venv\Scripts\python -c "
   import asyncio, sys, os
   sys.path.insert(0, 'backend')
   os.chdir('backend')
   import main_scorer
   asyncio.run(main_scorer.run_scoring(category='vn30', symbols=['VCB', 'VHM', 'TCB']))
   "
   ```

2. Kiểm tra output log có chứa:
   - `[1/3] Processing VCB in vn30...`
   - `Success: Total Score = X.XX`
   - Tương tự cho VHM, TCB

**Output log format:**
```
[STEP 7] TEST — Full Pipeline
  [TEST 7.1] Set DATA_SOURCE=amibroker ... [OK]
  [TEST 7.2] Run scoring for VCB ... [OK] / [FAIL: <error>]
  [TEST 7.3] Run scoring for VHM ... [OK] / [FAIL: <error>]
  [TEST 7.4] Run scoring for TCB ... [OK] / [FAIL: <error>]
  [RESULT] Pipeline works correctly
  [DATA] 
    VCB: Total=X.XX (MCDX=X.XX, RRG=X.XX)
    VHM: Total=X.XX (MCDX=X.XX, RRG=X.XX)
    TCB: Total=X.XX (MCDX=X.XX, RRG=X.XX)
```

---

### STEP 8: VERIFY DATABASE (5 phút)
**Mục tiêu**: Xác nhận dữ liệu đã lưu vào SQLite.

**Hành động:**
```bash
.\venv\Scripts\python -c "
import sys, sqlite3
sys.path.insert(0, 'backend')
from database import get_latest_scores
scores = get_latest_scores('vn30')
print(f'[OK] Found {len(scores)} scores in database')
for s in scores[:3]:
    print(f'  {s[\"symbol\"]}: {s[\"total_score\"]} (MCDX={s[\"mcdx_score\"]}, RRG={s[\"rrg_score\"]})')
"
```

**Output log format:**
```
[STEP 8] VERIFY DATABASE
  [CHECK 8.1] Database query ... [OK] / [FAIL: <error>]
  [CHECK 8.2] Record count ... [OK] (N records found)
  [RESULT] Data persisted correctly
```

---

### STEP 9: UPDATE DOCUMENTATION (15 phút)
**Mục tiêu**: Cập nhật tài liệu để phản ánh workflow mới.

**Hành động:**

**9a. Sửa HUONG_DAN_SU_DUNG.md:**
- Thay toàn bộ nội dung bằng:
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

**9b. Sửa TECHNICAL_SPEC.md:**
- Tìm mục "5. Quy trình Quét dữ liệu (Scoring Logic)"
- Thay bằng:
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

**9c. Sửa README.md:**
- Thay mục "Cách chạy" bằng:
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

**Output log format:**
```
[STEP 9] UPDATE DOCUMENTATION
  [ACTION 9.1] Update HUONG_DAN_SU_DUNG.md ... [OK]
  [ACTION 9.2] Update TECHNICAL_SPEC.md ... [OK]
  [ACTION 9.3] Update README.md ... [OK]
  [RESULT] Documentation updated
```

---

### STEP 10: FINAL CHECKLIST (5 phút)
**Mục tiêu**: Xác nhận toàn bộ công việc hoàn thành.

**Hành động:** Agent báo cáo từng mục:

```
[FINAL CHECKLIST]
  [ ] pywin32 import thành công
  [ ] ami_bridge.afl tìm thấy trong AmiBroker Formulas folder
  [ ] test_ami_connector.py chạy không lỗi, kết quả đúng
  [ ] scraper_amibroker.py đã tạo, import thành công
  [ ] main_scorer.py đã sửa, DATA_SOURCE=amibroker hoạt động
  [ ] VCB test: Banker value khớp với AmiBroker UI (±0.01)
  [ ] VCB test: RRG Quadrant khớp với AmiBroker UI
  [ ] VHM test: Scores khớp
  [ ] TCB test: Scores khớp
  [ ] Database lưu dữ liệu đúng
  [ ] HUONG_DAN_SU_DUNG.md đã cập nhật
  [ ] TECHNICAL_SPEC.md đã cập nhật
  [ ] README.md đã cập nhật

[OVERALL RESULT] ✅ ALL TASKS COMPLETED / ❌ BLOCKED AT STEP X: <reason>
```

---

## OUTPUT REQUIREMENTS

**Agent phải tạo 1 file log tổng hợp:**

**File**: `AGENT_EXECUTION_LOG_20260517.txt`

**Format:**
```
================================================================================
AGENT EXECUTION LOG — AmiBroker Connector Implementation
Date: 2026-05-17
Agent: [Agent Name]
Status: [COMPLETED / BLOCKED]
================================================================================

[STEP 1] PRE-FLIGHT CHECKS
  [CHECK 1.1] pywin32 import ... [OK]
  [CHECK 1.2] AmiBroker Formulas folder ... [OK]
  [CHECK 1.3] backend/ami_bridge.afl source ... [OK]
  [RESULT] All checks passed

[STEP 2] FIX test_ami_connector.py
  [ACTION 2.1] Replace get_stock_data() function ... [OK]
  [ACTION 2.2] Syntax check ... [OK]
  [RESULT] File fixed and validated

... (tương tự cho các step khác)

[FINAL CHECKLIST]
  [✓] pywin32 import thành công
  [✓] ami_bridge.afl tìm thấy
  ... (tất cả các mục)

[OVERALL RESULT] ✅ ALL TASKS COMPLETED

[NOTES]
- Nếu có vấn đề gặp phải, ghi chi tiết ở đây
- Nếu cần sửa plan, ghi rõ điểm nào cần thay đổi

================================================================================
```

---

## IMPORTANT NOTES FOR AGENT

1. **Không bỏ qua bất kỳ step nào** — tuần tự từ 1 đến 10.
2. **Nếu bất kỳ step nào fail** → dừng lại, báo cáo chi tiết, không tiếp tục.
3. **Nếu COM API không hoạt động** → thử các biến thể khác (xem ghi chú cuối plan chi tiết).
4. **Lưu log chi tiết** — mỗi action, mỗi test result, mỗi error message.
5. **Không sửa code ngoài những gì được chỉ định** — tránh side effects.
6. **Kiểm tra syntax** trước khi chạy test.

---

## REVIEWER CHECKLIST (User kiểm tra sau khi agent xong)

Sau khi agent báo hoàn thành, user cần:

1. ✅ Đọc file log `AGENT_EXECUTION_LOG_20260517.txt`
2. ✅ Kiểm tra tất cả mục trong FINAL CHECKLIST đều [✓]
3. ✅ Chạy lại test thủ công:
   ```bash
   set DATA_SOURCE=amibroker
   .\venv\Scripts\python backend\test_ami_connector.py
   ```
4. ✅ Mở Dashboard, nhấn "Cập nhật ngay" cho VN30, kiểm tra kết quả
5. ✅ So sánh 3-5 mã với AmiBroker UI để xác nhận giá trị khớp
6. ✅ Nếu tất cả OK → merge vào main branch

---

**End of Agent Prompt**
