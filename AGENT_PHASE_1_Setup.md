# AGENT PHASE 1: Setup & Validation
**Duration**: 20 minutes  
**Steps**: 1-2  
**Output file**: `AGENT_PHASE_1_LOG.txt`  

---

## OVERVIEW

Phase 1 kiểm tra môi trường và sửa lỗi COM API trong test_ami_connector.py.

**Nếu bất kỳ check nào fail → STOP và báo cáo, không tiếp tục.**

---

## STEP 1: PRE-FLIGHT CHECKS (5 min)

### Check 1.1: pywin32 import
```bash
cd "c:\Users\Nguyen To Dung\.gemini\antigravity\scratch\Cham diem co phieu"
.\venv\Scripts\python -c "import win32com.client; print('[OK] pywin32 imported')"
```

**Expected output**: `[OK] pywin32 imported`

**If fail**: 
```
ModuleNotFoundError: No module named 'win32com'
→ STOP. Report: "pywin32 not installed or not in venv"
```

**Log format:**
```
[CHECK 1.1] pywin32 import
  Command: .\venv\Scripts\python -c "import win32com.client; print('[OK] pywin32 imported')"
  Result: [OK] / [FAIL]
  Error (if any): <error message>
```

---

### Check 1.2: ami_bridge.afl in AmiBroker Formulas folder

Try both paths:
```bash
dir "C:\Program Files (x86)\AmiBroker\Formulas\Custom\ami_bridge.afl"
```

If not found, try:
```bash
dir "C:\Program Files\AmiBroker\Formulas\Custom\ami_bridge.afl"
```

**Expected output**: File listing showing ami_bridge.afl

**If fail**:
```
File Not Found
→ STOP. Report: "ami_bridge.afl not found in AmiBroker Formulas/Custom/ folder"
```

**Log format:**
```
[CHECK 1.2] ami_bridge.afl in AmiBroker
  Path 1: C:\Program Files (x86)\AmiBroker\Formulas\Custom\ami_bridge.afl
  Result: [FOUND] / [NOT FOUND]
  Path 2: C:\Program Files\AmiBroker\Formulas\Custom\ami_bridge.afl
  Result: [FOUND] / [NOT FOUND]
  Final: [OK] / [FAIL]
```

---

### Check 1.3: backend/ami_bridge.afl source file
```bash
dir backend\ami_bridge.afl
```

**Expected output**: File listing

**If fail**:
```
File Not Found
→ STOP. Report: "backend/ami_bridge.afl source not found"
```

**Log format:**
```
[CHECK 1.3] backend/ami_bridge.afl source
  Command: dir backend\ami_bridge.afl
  Result: [OK] / [FAIL]
```

---

### Check 1.4: backend/test_ami_connector.py exists
```bash
dir backend\test_ami_connector.py
```

**Expected output**: File listing

**If fail**:
```
File Not Found
→ STOP. Report: "backend/test_ami_connector.py not found"
```

**Log format:**
```
[CHECK 1.4] backend/test_ami_connector.py
  Command: dir backend\test_ami_connector.py
  Result: [OK] / [FAIL]
```

---

### STEP 1 RESULT

If all 4 checks pass:
```
[STEP 1 RESULT] ✅ ALL CHECKS PASSED
  Proceed to STEP 2
```

If any check fails:
```
[STEP 1 RESULT] ❌ BLOCKED
  Failed check: <check number>
  Reason: <reason>
  Action: STOP. Report to user.
```

---

## STEP 2: FIX test_ami_connector.py (15 min)

### Action 2.1: Open and read file
```bash
type backend\test_ami_connector.py | findstr /n "def get_stock_data"
```

This shows the line number where `get_stock_data()` function starts.

**Expected output**: Line number (around 52)

**Log format:**
```
[ACTION 2.1] Locate get_stock_data() function
  Command: type backend\test_ami_connector.py | findstr /n "def get_stock_data"
  Result: Line X
```

---

### Action 2.2: Replace get_stock_data() function

**Find**: Lines from `def get_stock_data(ab, symbol):` to the end of the function (before `def quadrant_name`)

**Replace with** (copy from `Implementation Plan/implementation_plan_20260517_AmiConnector_Detailed.md` — TASK 2 section):

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

**Log format:**
```
[ACTION 2.2] Replace get_stock_data() function
  Old function: Lines X-Y (removed)
  New function: Inserted (lines X-Y)
  Status: [OK]
```

---

### Action 2.3: Syntax check
```bash
.\venv\Scripts\python -m py_compile backend\test_ami_connector.py
```

**Expected output**: (no output = success)

**If fail**:
```
SyntaxError: invalid syntax at line X
→ STOP. Report: "Syntax error in test_ami_connector.py at line X"
```

**Log format:**
```
[ACTION 2.3] Syntax check
  Command: .\venv\Scripts\python -m py_compile backend\test_ami_connector.py
  Result: [OK] / [FAIL]
  Error (if any): <error message>
```

---

### STEP 2 RESULT

If all actions pass:
```
[STEP 2 RESULT] ✅ FILE FIXED AND VALIDATED
  File: backend/test_ami_connector.py
  Changes: get_stock_data() function replaced
  Syntax: Valid
  Ready for Phase 2: YES
```

If any action fails:
```
[STEP 2 RESULT] ❌ BLOCKED
  Failed action: <action number>
  Reason: <reason>
  Action: STOP. Report to user.
```

---

## PHASE 1 FINAL REPORT

Create file: `AGENT_PHASE_1_LOG.txt`

```
================================================================================
AGENT PHASE 1 LOG — Setup & Validation
Date: 2026-05-17
Duration: X minutes
Status: ✅ COMPLETED / ❌ BLOCKED
================================================================================

[STEP 1] PRE-FLIGHT CHECKS
  [CHECK 1.1] pywin32 import ... [OK]
  [CHECK 1.2] ami_bridge.afl in AmiBroker ... [OK]
  [CHECK 1.3] backend/ami_bridge.afl source ... [OK]
  [CHECK 1.4] backend/test_ami_connector.py ... [OK]
  [RESULT] All checks passed

[STEP 2] FIX test_ami_connector.py
  [ACTION 2.1] Locate get_stock_data() function ... [OK] (Line X)
  [ACTION 2.2] Replace function ... [OK]
  [ACTION 2.3] Syntax check ... [OK]
  [RESULT] File fixed and validated

[PHASE 1 RESULT] ✅ COMPLETED
  All steps passed
  Ready for Phase 2: YES

[NOTES]
- (any issues encountered, workarounds applied, etc.)

================================================================================
```

---

## NEXT STEP

After Phase 1 completes:
1. Agent reports: "Phase 1 completed. Log: AGENT_PHASE_1_LOG.txt"
2. User reviews log
3. User approves: "Phase 1 OK. Proceed to Phase 2."
4. Agent reads: `AGENT_PHASE_2_Implementation.md`
