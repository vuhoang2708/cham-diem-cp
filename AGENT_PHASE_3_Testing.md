# AGENT PHASE 3: Testing & Verification
**Duration**: 35 minutes  
**Steps**: 5-7  
**Output file**: `AGENT_PHASE_3_LOG.txt`  
**Prerequisite**: Phase 2 completed, AmiBroker running with VCB data loaded  

---

## OVERVIEW

Phase 3 chạy 3 test độc lập để xác nhận mỗi module hoạt động đúng.

**Nếu bất kỳ test nào fail → báo lỗi chi tiết, nhưng tiếp tục các test khác (không stop).**

---

## STEP 5: TEST — test_ami_connector.py (10 min)

### Prerequisite: AmiBroker must be running

**Check**: 
```bash
tasklist | findstr "AmiBroker"
```

**Expected output**: `AmiBroker.exe` in process list

**If not found**:
```
→ WARN: AmiBroker not running. Cannot proceed with test.
  Action: User must open AmiBroker before running this test.
  Skip to STEP 6 (module import test).
```

**Log format:**
```
[STEP 5 PREREQUISITE] AmiBroker running check
  Command: tasklist | findstr "AmiBroker"
  Result: [RUNNING] / [NOT RUNNING]
```

---

### Test 5.1: Run test_ami_connector.py

```bash
.\venv\Scripts\python backend\test_ami_connector.py
```

**Expected output**:
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

**Possible errors**:

| Error | Cause | Action |
|---|---|---|
| `Cannot connect to AmiBroker` | AmiBroker not running | WARN: Skip this test, continue to 5.2 |
| `Cannot open ami_bridge.afl` | File not in Formulas/Custom/ | FAIL: Report path issue |
| `Timeout waiting for AmiBroker` | AFL not running correctly | FAIL: Check AFL in AmiBroker Editor |
| `MCDX Banker Value : 0.0000` | Data not loaded | WARN: Check VCB data in AmiBroker |

**Log format:**
```
[TEST 5.1] Run test_ami_connector.py
  Command: .\venv\Scripts\python backend\test_ami_connector.py
  Result: [OK] / [FAIL] / [WARN]
  Output:
    - AmiBroker connection: [OK] / [FAIL]
    - VCB data fetch: [OK] / [FAIL]
    - MCDX Banker: X.XXXX
    - RRG Quadrant: <name>
    - Total Score: X.XX
  Error (if any): <error message>
```

---

### Test 5.2: Verify output values

If test 5.1 passed, check:
- MCDX Banker Value is between 0-20
- MCDX Score is between 0-1.0
- RRG Quadrant is one of: LEADING, WEAKENING, LAGGING, IMPROVING
- RRG Score is one of: 1.0, 0.75, 0.5, 0.25
- Total Score is between 0-2.0

**Log format:**
```
[TEST 5.2] Verify output values
  MCDX Banker: X.XXXX (range 0-20) ... [OK]
  MCDX Score: X.XX (range 0-1.0) ... [OK]
  RRG Quadrant: <name> (valid) ... [OK]
  RRG Score: X.XX (valid) ... [OK]
  Total Score: X.XX (range 0-2.0) ... [OK]
  Result: [OK] / [FAIL]
```

---

### STEP 5 RESULT

```
[STEP 5 RESULT] ✅ TEST PASSED / ⚠️ TEST SKIPPED / ❌ TEST FAILED
  (details based on test results)
```

---

## STEP 6: TEST — scraper_amibroker.py (10 min)

### Test 6.1: Module import

```bash
.\venv\Scripts\python -c "import sys; sys.path.insert(0, 'backend'); from scraper_amibroker import AmiConnector; print('[OK] Module imported')"
```

**Expected output**: `[OK] Module imported`

**If fail**:
```
ModuleNotFoundError or ImportError
→ FAIL: Report import error
```

**Log format:**
```
[TEST 6.1] Module import
  Command: .\venv\Scripts\python -c "import sys; sys.path.insert(0, 'backend'); from scraper_amibroker import AmiConnector; print('[OK] Module imported')"
  Result: [OK] / [FAIL]
  Error (if any): <error message>
```

---

### Test 6.2: AmiConnector.connect()

```bash
.\venv\Scripts\python -c "
import sys
sys.path.insert(0, 'backend')
from scraper_amibroker import AmiConnector
c = AmiConnector()
result = c.connect()
print(f'[RESULT] connect() returned: {result}')
if result:
    print('[OK] Connected to AmiBroker')
    c.disconnect()
else:
    print('[WARN] Cannot connect (AmiBroker may not be running)')
"
```

**Expected output**: 
```
[RESULT] connect() returned: True
[OK] Connected to AmiBroker
```

or

```
[RESULT] connect() returned: False
[WARN] Cannot connect (AmiBroker may not be running)
```

**Log format:**
```
[TEST 6.2] AmiConnector.connect()
  Result: [OK] / [WARN] / [FAIL]
  Output: <output>
  Error (if any): <error message>
```

---

### Test 6.3: AmiConnector.get_data('VCB')

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
    print('[WARN] Cannot connect to AmiBroker')
"
```

**Expected output**:
```
[OK] Data retrieved:
  Banker: X.XXXX
  Quadrant: X
  MCDX Score: X.XX
  RRG Score: X.XX
```

**Log format:**
```
[TEST 6.3] AmiConnector.get_data('VCB')
  Result: [OK] / [WARN] / [FAIL]
  Data:
    - Banker: X.XXXX
    - Quadrant: X
    - MCDX Score: X.XX
    - RRG Score: X.XX
  Error (if any): <error message>
```

---

### STEP 6 RESULT

```
[STEP 6 RESULT] ✅ MODULE WORKS CORRECTLY / ⚠️ PARTIAL / ❌ FAILED
  (details based on test results)
```

---

## STEP 7: TEST — Full Pipeline (15 min)

### Test 7.1: Set environment variable

```bash
set DATA_SOURCE=amibroker
echo %DATA_SOURCE%
```

**Expected output**: `amibroker`

**Log format:**
```
[TEST 7.1] Set DATA_SOURCE environment variable
  Command: set DATA_SOURCE=amibroker
  Verification: echo %DATA_SOURCE%
  Result: [OK]
```

---

### Test 7.2: Run scoring for 3 symbols

```bash
.\venv\Scripts\python -c "
import asyncio, sys, os
sys.path.insert(0, 'backend')
os.chdir('backend')
import main_scorer
asyncio.run(main_scorer.run_scoring(category='vn30', symbols=['VCB', 'VHM', 'TCB']))
"
```

**Expected output**:
```
Starting VN30 Scoring Process...
[1/3] Processing VCB in vn30...
   Success: Total Score = X.XX
[2/3] Processing VHM in vn30...
   Success: Total Score = X.XX
[3/3] Processing TCB in vn30...
   Success: Total Score = X.XX
```

**Possible errors**:

| Error | Cause | Action |
|---|---|---|
| `Critical Error: Cannot connect to AmiBroker` | AmiBroker not running | FAIL: User must open AmiBroker |
| `Failed to process VCB` | Data fetch failed | WARN: Check AmiBroker data |
| `SyntaxError` | Code error | FAIL: Report error |

**Log format:**
```
[TEST 7.2] Run scoring for 3 symbols
  Command: .\venv\Scripts\python -c "..."
  Result: [OK] / [FAIL]
  Output:
    [1/3] VCB ... [OK] / [FAIL]
      Total Score: X.XX (MCDX=X.XX, RRG=X.XX)
    [2/3] VHM ... [OK] / [FAIL]
      Total Score: X.XX (MCDX=X.XX, RRG=X.XX)
    [3/3] TCB ... [OK] / [FAIL]
      Total Score: X.XX (MCDX=X.XX, RRG=X.XX)
  Error (if any): <error message>
```

---

### Test 7.3: Verify database records

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

**Expected output**:
```
[OK] Found 3 scores in database
  VCB: X.XX (MCDX=X.XX, RRG=X.XX)
  VHM: X.XX (MCDX=X.XX, RRG=X.XX)
  TCB: X.XX (MCDX=X.XX, RRG=X.XX)
```

**Log format:**
```
[TEST 7.3] Verify database records
  Query: get_latest_scores('vn30')
  Result: [OK] / [FAIL]
  Records found: X
  Sample records:
    - VCB: X.XX
    - VHM: X.XX
    - TCB: X.XX
  Error (if any): <error message>
```

---

### STEP 7 RESULT

```
[STEP 7 RESULT] ✅ PIPELINE WORKS CORRECTLY / ⚠️ PARTIAL / ❌ FAILED
  (details based on test results)
```

---

## PHASE 3 FINAL REPORT

Create file: `AGENT_PHASE_3_LOG.txt`

```
================================================================================
AGENT PHASE 3 LOG — Testing & Verification
Date: 2026-05-17
Duration: X minutes
Status: ✅ COMPLETED / ⚠️ PARTIAL / ❌ FAILED
================================================================================

[STEP 5] TEST — test_ami_connector.py
  [TEST 5.1] Run test_ami_connector.py ... [OK] / [WARN] / [FAIL]
  [TEST 5.2] Verify output values ... [OK] / [FAIL]
  [RESULT] Test passed / skipped / failed

[STEP 6] TEST — scraper_amibroker.py
  [TEST 6.1] Module import ... [OK] / [FAIL]
  [TEST 6.2] AmiConnector.connect() ... [OK] / [WARN] / [FAIL]
  [TEST 6.3] AmiConnector.get_data('VCB') ... [OK] / [WARN] / [FAIL]
  [RESULT] Module works correctly / partial / failed

[STEP 7] TEST — Full Pipeline
  [TEST 7.1] Set DATA_SOURCE=amibroker ... [OK]
  [TEST 7.2] Run scoring for 3 symbols ... [OK] / [FAIL]
    - VCB: X.XX (MCDX=X.XX, RRG=X.XX)
    - VHM: X.XX (MCDX=X.XX, RRG=X.XX)
    - TCB: X.XX (MCDX=X.XX, RRG=X.XX)
  [TEST 7.3] Verify database records ... [OK] / [FAIL]
  [RESULT] Pipeline works correctly / failed

[PHASE 3 RESULT] ✅ COMPLETED / ⚠️ PARTIAL / ❌ FAILED
  All tests passed / some tests failed
  Ready for Phase 4: YES / NO

[NOTES]
- (any issues encountered, workarounds applied, etc.)

================================================================================
```

---

## NEXT STEP

After Phase 3 completes:
1. Agent reports: "Phase 3 completed. Log: AGENT_PHASE_3_LOG.txt"
2. User reviews log
3. If all tests passed: "Phase 3 OK. Proceed to Phase 4."
4. If some tests failed: "Fix issues and re-run Phase 3, or proceed with caution."
5. Agent reads: `AGENT_PHASE_4_Finalization.md`
