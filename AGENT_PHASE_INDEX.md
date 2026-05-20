# AGENT EXECUTION — Phase Index & Master Checklist
**Project**: VN100 Stock Scoring Dashboard — AmiBroker Connector  
**Date**: 2026-05-17  
**Total Phases**: 5  
**Estimated Duration**: 2-3 hours  

---

## PHASE OVERVIEW

| Phase | Steps | Duration | Focus | Output |
|---|---|---|---|---|
| **Phase 1: Setup & Validation** | 1-2 | 20 min | Environment check, fix COM API | `AGENT_PHASE_1_LOG.txt` |
| **Phase 2: Core Implementation** | 3-4 | 50 min | Create scraper_amibroker.py, modify main_scorer.py | `AGENT_PHASE_2_LOG.txt` |
| **Phase 3: Testing & Verification** | 5-7 | 35 min | Test individual modules, full pipeline | `AGENT_PHASE_3_LOG.txt` |
| **Phase 4: Finalization** | 8-9 | 20 min | Verify database, update docs | `AGENT_PHASE_4_LOG.txt` |
| **Phase 5: Sign-off** | 10 | 5 min | Final checklist | `AGENT_PHASE_5_CHECKLIST.txt` |

---

## HOW TO USE THIS INDEX

**Agent workflow:**
1. Read this file (AGENT_PHASE_INDEX.md)
2. Execute Phase 1 → read `AGENT_PHASE_1_Setup.md` → run steps → create log
3. Execute Phase 2 → read `AGENT_PHASE_2_Implementation.md` → run steps → create log
4. ... (repeat for Phase 3, 4, 5)
5. After all phases complete → create `AGENT_FINAL_SUMMARY.txt`

**User workflow:**
1. Send agent this index file
2. Agent reports completion of each phase
3. User reviews each phase log before proceeding to next
4. After all phases → user reviews final summary

---

## PHASE 1: Setup & Validation
**File**: `AGENT_PHASE_1_Setup.md`  
**Steps**: 1-2  
**Duration**: 20 min  
**Prerequisite**: None  
**Blocker**: If any check fails, stop and report

**What it does:**
- Check pywin32, ami_bridge.afl, backend files
- Fix COM API errors in test_ami_connector.py
- Validate syntax

**Output**: `AGENT_PHASE_1_LOG.txt`

---

## PHASE 2: Core Implementation
**File**: `AGENT_PHASE_2_Implementation.md`  
**Steps**: 3-4  
**Duration**: 50 min  
**Prerequisite**: Phase 1 completed successfully  
**Blocker**: If syntax check fails, stop and report

**What it does:**
- Create `backend/scraper_amibroker.py` (new module)
- Modify `backend/main_scorer.py` (add AmiBroker support)
- Validate imports and syntax

**Output**: `AGENT_PHASE_2_LOG.txt`

---

## PHASE 3: Testing & Verification
**File**: `AGENT_PHASE_3_Testing.md`  
**Steps**: 5-7  
**Duration**: 35 min  
**Prerequisite**: Phase 2 completed, AmiBroker running  
**Blocker**: If any test fails, report error and stop

**What it does:**
- Test test_ami_connector.py (VCB data fetch)
- Test scraper_amibroker.py (module import + get_data)
- Test full pipeline (main_scorer.py with 3 symbols)

**Output**: `AGENT_PHASE_3_LOG.txt`

---

## PHASE 4: Finalization
**File**: `AGENT_PHASE_4_Finalization.md`  
**Steps**: 8-9  
**Duration**: 20 min  
**Prerequisite**: Phase 3 completed successfully  
**Blocker**: None (documentation updates)

**What it does:**
- Verify database has correct records
- Update HUONG_DAN_SU_DUNG.md
- Update TECHNICAL_SPEC.md
- Update README.md

**Output**: `AGENT_PHASE_4_LOG.txt`

---

## PHASE 5: Sign-off
**File**: `AGENT_PHASE_5_Checklist.md`  
**Steps**: 10  
**Duration**: 5 min  
**Prerequisite**: All phases 1-4 completed  
**Blocker**: None (final report)

**What it does:**
- Verify all 12 checklist items
- Create final summary report

**Output**: `AGENT_PHASE_5_CHECKLIST.txt` + `AGENT_FINAL_SUMMARY.txt`

---

## MASTER CHECKLIST (Track Progress)

### Phase 1: Setup & Validation
- [ ] Phase 1 started
- [ ] Phase 1 completed
- [ ] Log file created: `AGENT_PHASE_1_LOG.txt`
- [ ] No blockers found

### Phase 2: Core Implementation
- [ ] Phase 2 started
- [ ] Phase 2 completed
- [ ] Log file created: `AGENT_PHASE_2_LOG.txt`
- [ ] No blockers found

### Phase 3: Testing & Verification
- [ ] Phase 3 started
- [ ] Phase 3 completed
- [ ] Log file created: `AGENT_PHASE_3_LOG.txt`
- [ ] No blockers found

### Phase 4: Finalization
- [ ] Phase 4 started
- [ ] Phase 4 completed
- [ ] Log file created: `AGENT_PHASE_4_LOG.txt`
- [ ] No blockers found

### Phase 5: Sign-off
- [ ] Phase 5 started
- [ ] Phase 5 completed
- [ ] Checklist file created: `AGENT_PHASE_5_CHECKLIST.txt`
- [ ] Summary file created: `AGENT_FINAL_SUMMARY.txt`

---

## COMMUNICATION PROTOCOL

**Agent reports after each phase:**
```
[PHASE X COMPLETE]
Status: ✅ SUCCESS / ❌ BLOCKED
Log file: AGENT_PHASE_X_LOG.txt
Blocker (if any): <description>
Ready for Phase X+1: YES / NO
```

**User reviews and approves:**
```
[USER REVIEW]
Phase X log reviewed: ✅ OK / ❌ ISSUE
Approval for Phase X+1: ✅ APPROVED / ❌ HOLD
```

---

## FILE LOCATIONS

All files in: `c:\Users\Nguyen To Dung\.gemini\antigravity\scratch\Cham diem co phieu\`

**Phase prompts:**
- `AGENT_PHASE_1_Setup.md`
- `AGENT_PHASE_2_Implementation.md`
- `AGENT_PHASE_3_Testing.md`
- `AGENT_PHASE_4_Finalization.md`
- `AGENT_PHASE_5_Checklist.md`

**Phase logs (created by agent):**
- `AGENT_PHASE_1_LOG.txt`
- `AGENT_PHASE_2_LOG.txt`
- `AGENT_PHASE_3_LOG.txt`
- `AGENT_PHASE_4_LOG.txt`
- `AGENT_PHASE_5_CHECKLIST.txt`
- `AGENT_FINAL_SUMMARY.txt`

**Reference docs:**
- `Implementation Plan/implementation_plan_20260517_AmiConnector_Detailed.md` (code snippets)
- `TECHNICAL_SPEC.md`, `README.md`, `HUONG_DAN_SU_DUNG.md` (docs to update)

---

## NEXT STEP

**Agent**: Read `AGENT_PHASE_1_Setup.md` and begin Phase 1.

**User**: Wait for agent to report Phase 1 completion, then review log.
