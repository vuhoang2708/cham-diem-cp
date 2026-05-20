# AGENT PHASE 2: Core Implementation
**Duration**: 50 minutes  
**Steps**: 3-4  
**Output file**: `AGENT_PHASE_2_LOG.txt`  
**Prerequisite**: Phase 1 completed successfully  

---

## OVERVIEW

Phase 2 tạo module scraper_amibroker.py mới và sửa main_scorer.py để hỗ trợ AmiBroker.

**Nếu bất kỳ action nào fail → STOP và báo cáo, không tiếp tục.**

---

## STEP 3: CREATE backend/scraper_amibroker.py (30 min)

### Action 3.1: Create new file

```bash
type nul > backend\scraper_amibroker.py
```

**Expected output**: File created (no output = success)

**Log format:**
```
[ACTION 3.1] Create backend/scraper_amibroker.py
  Command: type nul > backend\scraper_amibroker.py
  Result: [OK]
```

---

### Action 3.2: Write code to file

Copy entire code from `Implementation Plan/implementation_plan_20260517_AmiConnector_Detailed.md` — **TASK 2 section** (the full `scraper_amibroker.py` code).

**File content** (copy from plan):
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

**Log format:**
```
[ACTION 3.2] Write code to backend/scraper_amibroker.py
  Lines written: X
  Classes: AmiConnector
  Functions: connect(), disconnect(), get_data(), _score_banker(), _score_rrg()
  Status: [OK]
```

---

### Action 3.3: Syntax check

```bash
.\venv\Scripts\python -m py_compile backend\scraper_amibroker.py
```

**Expected output**: (no output = success)

**If fail**:
```
SyntaxError: invalid syntax at line X
→ STOP. Report: "Syntax error in scraper_amibroker.py at line X"
```

**Log format:**
```
[ACTION 3.3] Syntax check
  Command: .\venv\Scripts\python -m py_compile backend\scraper_amibroker.py
  Result: [OK] / [FAIL]
  Error (if any): <error message>
```

---

### Action 3.4: Import test

```bash
.\venv\Scripts\python -c "import sys; sys.path.insert(0, 'backend'); from scraper_amibroker import AmiConnector; print('[OK] Module imported')"
```

**Expected output**: `[OK] Module imported`

**If fail**:
```
ModuleNotFoundError or ImportError
→ STOP. Report: "Cannot import scraper_amibroker module"
```

**Log format:**
```
[ACTION 3.4] Import test
  Command: .\venv\Scripts\python -c "import sys; sys.path.insert(0, 'backend'); from scraper_amibroker import AmiConnector; print('[OK] Module imported')"
  Result: [OK] / [FAIL]
  Error (if any): <error message>
```

---

### STEP 3 RESULT

If all actions pass:
```
[STEP 3 RESULT] ✅ MODULE CREATED AND VALIDATED
  File: backend/scraper_amibroker.py
  Size: X lines
  Syntax: Valid
  Import: OK
  Ready for STEP 4: YES
```

If any action fails:
```
[STEP 3 RESULT] ❌ BLOCKED
  Failed action: <action number>
  Reason: <reason>
  Action: STOP. Report to user.
```

---

## STEP 4: MODIFY backend/main_scorer.py (20 min)

### Action 4.1: Add USE_AMIBROKER import

**Find**: Line with `import asyncio` (around line 1)

**Add after it**:
```python
import os
USE_AMIBROKER = os.environ.get("DATA_SOURCE", "fireant").lower() == "amibroker"
```

**Log format:**
```
[ACTION 4.1] Add USE_AMIBROKER import
  Location: After "import asyncio"
  Lines added: 2
  Status: [OK]
```

---

### Action 4.2: Replace scraper initialization

**Find**: Section starting with `# Setup Scraper` (around line 36-42)

**Old code**:
```python
# Setup Scraper
scraper = MCDXScraper()
connected = await scraper.connect()
if not connected:
    print("Critical Error: Could not connect to Chrome CDP.")
    return
```

**Replace with**:
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

**Log format:**
```
[ACTION 4.2] Replace scraper initialization
  Location: Lines X-Y
  Old code: Removed (6 lines)
  New code: Inserted (12 lines)
  Status: [OK]
```

---

### Action 4.3: Replace MCDX scraping logic

**Find**: Line with `mcdx_res = await scraper.get_banker_value(symbol)` (around line 56)

**Old code**:
```python
# 2. MCDX Scraping (Banker Value, MCDX Score)
mcdx_res = await scraper.get_banker_value(symbol)
```

**Replace with**:
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

**Log format:**
```
[ACTION 4.3] Replace MCDX scraping logic
  Location: Lines X-Y
  Old code: Removed (2 lines)
  New code: Inserted (15 lines)
  Status: [OK]
```

---

### Action 4.4: Add cleanup section

**Find**: End of `run_scoring()` function, before `return` or at the very end

**Add**:
```python
# Cleanup
if USE_AMIBROKER:
    connector.disconnect()
else:
    await scraper.disconnect()
```

**Log format:**
```
[ACTION 4.4] Add cleanup section
  Location: End of run_scoring() function
  Lines added: 5
  Status: [OK]
```

---

### Action 4.5: Syntax check

```bash
.\venv\Scripts\python -m py_compile backend\main_scorer.py
```

**Expected output**: (no output = success)

**If fail**:
```
SyntaxError: invalid syntax at line X
→ STOP. Report: "Syntax error in main_scorer.py at line X"
```

**Log format:**
```
[ACTION 4.5] Syntax check
  Command: .\venv\Scripts\python -m py_compile backend\main_scorer.py
  Result: [OK] / [FAIL]
  Error (if any): <error message>
```

---

### STEP 4 RESULT

If all actions pass:
```
[STEP 4 RESULT] ✅ FILE MODIFIED AND VALIDATED
  File: backend/main_scorer.py
  Changes: 4 sections modified
  Syntax: Valid
  Ready for Phase 3: YES
```

If any action fails:
```
[STEP 4 RESULT] ❌ BLOCKED
  Failed action: <action number>
  Reason: <reason>
  Action: STOP. Report to user.
```

---

## PHASE 2 FINAL REPORT

Create file: `AGENT_PHASE_2_LOG.txt`

```
================================================================================
AGENT PHASE 2 LOG — Core Implementation
Date: 2026-05-17
Duration: X minutes
Status: ✅ COMPLETED / ❌ BLOCKED
================================================================================

[STEP 3] CREATE backend/scraper_amibroker.py
  [ACTION 3.1] Create file ... [OK]
  [ACTION 3.2] Write code ... [OK] (X lines)
  [ACTION 3.3] Syntax check ... [OK]
  [ACTION 3.4] Import test ... [OK]
  [RESULT] Module created and validated

[STEP 4] MODIFY backend/main_scorer.py
  [ACTION 4.1] Add USE_AMIBROKER import ... [OK]
  [ACTION 4.2] Replace scraper initialization ... [OK]
  [ACTION 4.3] Replace MCDX scraping logic ... [OK]
  [ACTION 4.4] Add cleanup section ... [OK]
  [ACTION 4.5] Syntax check ... [OK]
  [RESULT] File modified and validated

[PHASE 2 RESULT] ✅ COMPLETED
  All steps passed
  Ready for Phase 3: YES

[NOTES]
- (any issues encountered, workarounds applied, etc.)

================================================================================
```

---

## NEXT STEP

After Phase 2 completes:
1. Agent reports: "Phase 2 completed. Log: AGENT_PHASE_2_LOG.txt"
2. User reviews log
3. User approves: "Phase 2 OK. Proceed to Phase 3."
4. Agent reads: `AGENT_PHASE_3_Testing.md`
