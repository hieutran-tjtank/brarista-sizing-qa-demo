# Build Log — Brarista Sizing QA Demo

> This document records the step-by-step development process of this project,
> showing how Claude Code (AI) was used, what the human QA engineer reviewed,
> and where AI errors were caught.

---

## Phase 1 — Foundation (2026-09-09)

### Step 1: Project Setup
**Who did it:** Claude Code (AI)
**What was done:**
- Created project structure: `src/`, `data/`, `tests/`, `docs/`
- Created `requirements.txt` (pytest only)
- Created `pytest.ini` configuration

### Step 2: Data Models (`src/sizing_engine/models.py`)
**Who did it:** Claude Code (AI)
**What was done:**
- Defined `SizeSystem` enum: US, UK, EU (Phase 1 scope = 3 systems)
- Defined `BraSize` dataclass: band (int), cup (str), system (SizeSystem)
- Used `frozen=True` for immutability

**Design decisions:**
- Started with only 3 systems (US, UK, EU) to keep initial review manageable
- US/UK share inch-based bands but diverge on cup letters after D
- EU uses centimeters — different unit entirely

### Step 3: Size Chart Data (`data/size_charts/`)
**Who did it:** Claude Code (AI) generated initial data
**Data source:** Cross-referenced from bratabase.com, herroom.com, size.ly

**Band conversion table:**
```
Index:  0    1    2    3    4    5    6    7    8
US/UK:  28   30   32   34   36   38   40   42   44
EU:     60   65   70   75   80   85   90   95   100
```

**Cup conversion table (the critical part):**
```
Volume: 0    1    2    3    4     5      6    7    8    9
US:     A    B    C    D    DD    DDD    G    H    I    J
UK:     A    B    C    D    DD    E      F    FF   G    GG
EU:     A    B    C    D    E     F      G    H    I    J
```

**⚠️ Key insight:** Cups A–D are identical across all systems. From volume index 4 onwards, each system uses completely different letter sequences for the same physical cup volume.

**🔍 QA Review needed:**
- [ ] Verify band mapping against real brand charts
- [ ] Verify cup sequences — especially US DDD vs UK E vs EU F
- [ ] Check if any cups are missing between D and DD

### Step 4: Converter Logic (`src/sizing_engine/converter.py`)
**Who did it:** Claude Code (AI)
**How it works:**
1. Band conversion: index-based lookup (find position in source system → get value at same position in target system)
2. Cup conversion: same index-based approach using volume index
3. Full size conversion: converts band and cup independently, combines into new BraSize

### Step 5: Test Cases (`tests/test_basic_conversion.py`)
**Who did it:** Claude Code (AI) generated 10 test cases
**Test design strategy:**
- Tests 1-2: Simple conversions (cups ≤ D, all systems agree)
- Tests 3-4: DD divergence zone (US/UK DD vs EU E)
- Tests 5-6: Beyond DD (DDD divergence)
- Tests 7-9: Reverse conversions
- Test 10: Large cup edge case

**🔍 QA Review needed:**
- [ ] Are the 10 expected outputs correct?
- [ ] Any edge cases missing that should be in the first 10?
- [ ] Do the test names clearly describe what they verify?

### Step 6: Test Execution
**Who did it:** Claude Code (AI) ran tests
**Result:** ✅ **10/10 passed** (0.01s)

```
tests/test_basic_conversion.py::test_01_us_to_eu_simple PASSED           [ 10%]
tests/test_basic_conversion.py::test_02_us_to_uk_simple PASSED           [ 20%]
tests/test_basic_conversion.py::test_03_us_dd_to_uk PASSED               [ 30%]
tests/test_basic_conversion.py::test_04_us_dd_to_eu PASSED               [ 40%]
tests/test_basic_conversion.py::test_05_us_ddd_to_uk PASSED              [ 50%]
tests/test_basic_conversion.py::test_06_us_ddd_to_eu PASSED              [ 60%]
tests/test_basic_conversion.py::test_07_uk_f_to_us PASSED                [ 70%]
tests/test_basic_conversion.py::test_08_eu_to_us PASSED                  [ 80%]
tests/test_basic_conversion.py::test_09_eu_e_to_uk PASSED                [ 90%]
tests/test_basic_conversion.py::test_10_uk_gg_to_eu PASSED               [100%]

============================== 10 passed in 0.01s ==============================
```

---

## QA Review Notes — Phase 1 (Completed 2026-09-09)

**Reviewer:** Hieu Tran (Manual QC)

### Data Verification
- [x] Band conversion verified against: online bra size charts (bratabase, herroom)
- [x] Cup conversion verified against: cross-referenced US/UK/EU cup sequences
- [x] Cup divergence after D confirmed: US DD = UK DD = EU E ✅

### Test Case Review
- [x] All 10 tests reviewed — expected outputs verified correct
- [x] Test design strategy approved (simple → divergence → reverse → edge)
- [x] Ran `python3 -m pytest tests/ -v` → **10/10 passed**

### AI Errors Caught 🎯

| # | What AI Generated | What's Wrong | How Caught | Severity |
|---|-------------------|--------------|------------|----------|
| 1 | Band data only covers 28–44 (9 bands) | Plus-size bands (46, 48, 50, 52, 54) are missing. Converter raises `ValueError` and crashes when encountering any band outside this range — e.g., `UK 54E → EU` fails. Real brands sell sizes up to band 54+. | QA tested edge case: input `UK 54E`, got `ValueError: Band 54 not found`. No graceful handling. | 🟡 Medium — data gap, not logic bug |
| 2 | AI implemented sister sizing (band↑ + cup↓ = same volume) but **did not implement cup adjustment** (same band, different cup) | Missing an entire recommendation feature. Sister sizing only covers "band doesn't fit" scenarios. But when cup doesn't fit (too tight/loose) and band is fine, the system has no recommendation. | QA asked: "What about products with different cup volume but same band?" — realized this common real-world scenario was completely missing. | 🔴 High — missing feature |
| 3 | After Phase 2, AI proposed skipping Phase 3 (Scale) and jumping straight to Phase 4 (Polish & Ship) | AI forgot its own plan — Phase 3 was supposed to add FR/AU/JP systems and body measurement module. Would have shipped an incomplete project missing 3 planned sizing systems. | QA checked plan: "Phase 3 as planned is Scale" — caught AI deviating from agreed implementation plan. | 🟡 Medium — process error |

### QA Verdict
> Phase 1 logic is sound. Data tables are correct for the covered range. **Key gap:** band range is incomplete — should either expand data or handle out-of-range gracefully. Proceed to Phase 2.

---

## Phase 2 — Expand & Harden (2026-09-09)

### Step 7: Edge Case Tests (from QA catch)
**Who did it:** Claude Code (AI), triggered by QA finding
**What was done:**
- Added test for out-of-range band (the catch from Phase 1)
- Added test for invalid cup letter
- Added test for same-system conversion (no-op)

### Step 8: Sister Sizing Module
**Who did it:** Claude Code (AI)
**What was done:**
- Implemented sister sizing logic: band ↑1 + cup ↓1 = same cup volume
- Business rule: if band feels too tight → go up 1 band, down 1 cup
- Edge cases: cup A (no sister down), max band (no sister up)

### Step 9: Sister Sizing Tests
**Who did it:** Claude Code (AI) generated test cases
**Test design:**
- Normal sister sizing (up and down)
- Boundary: cup A has no sister-size-down
- Boundary: max band has no sister-size-up

### Step 10: Parametrized Conversion Matrix
**Who did it:** Claude Code (AI)
**What was done:**
- Parametrized all band × system pairs for exhaustive coverage
- Parametrized cup divergence zone tests

### Step 11: Test Execution (before cup adjustment)
**Result:** ✅ **57/57 passed** (0.04s)

### Step 12: Cup Adjustment Module (from QA catch #2)
**Who did it:** Claude Code (AI), triggered by QA finding
**QA Catch:** "Sister sizing only covers band-fit problems. What about cup-fit problems?"
**What was done:**
- Created `src/sizing_engine/cup_adjustment.py` — keeps band, adjusts cup ↑/↓
- Created `tests/test_cup_adjustment.py` — 10 tests including DD/DDD zone
- Edge cases: cup A (no cup-down), max cup (no cup-up)

### Step 13: Full Test Execution
**Result:** ✅ **67/67 passed** (0.04s)

| Test file | Tests | Status |
|-----------|-------|--------|
| `test_basic_conversion.py` | 10 | ✅ All passed |
| `test_edge_cases.py` | 7 (from QA catch #1) | ✅ All passed |
| `test_sister_sizing.py` | 10 | ✅ All passed |
| `test_conversion_matrix.py` | 30 (parametrized) | ✅ All passed |
| `test_cup_adjustment.py` | 10 (from QA catch #2) | ✅ All passed |
| **Total** | **67** | **✅ All passed** |

> **Note:** Edge case coverage for malformed inputs (empty values, lowercase,
> garbage characters) was further expanded in Phase 4 — see Step 19.

---

## Phase 3 — Scale (2026-09-09)

> ⚠️ **QA Catch #3**: AI tried to skip this phase and jump to Phase 4 (Polish). QA caught it.

### Step 14: Expand to 6 Sizing Systems
**Who did it:** Claude Code (AI)
**What was done:**
- Added FR (French), AU (Australian), JP (Japanese) to `SizeSystem` enum
- Updated `band_conversion.json` and `cup_conversion.json` with 6 systems
- Updated sister_sizing.py and cup_adjustment.py with new system data

**Key relationships:**
- FR bands = EU bands + 15cm (e.g., EU 75 = FR 90)
- AU uses own band numbering (6, 8, 10...) but UK cup letters
- JP = EU (same bands in cm, same cup letters)

### Step 15: Body Measurement Module
**Who did it:** Claude Code (AI)
**What was done:**
- Created `src/sizing_engine/measurement.py`
- Underbust (cm) → band size, bust-underbust difference → cup size
- Supports all 6 systems

### Step 16: New System Tests
**Who did it:** Claude Code (AI)
**What was done:**
- `tests/test_new_systems.py` — 14 tests for FR/AU/JP conversion + roundtrips
- `tests/test_measurement.py` — 10 tests for measurement → size recommendation

### Step 17: AI Error During Testing 🎯
**What happened:** test_07 (smallest band measurement) FAILED on first run.
- AI wrote expected value `EU 60B` but actual was `EU 60A`
- Bust 70 - underbust 58 = 12cm → falls in A range (10-12.5cm), not B
- **AI miscalculated the cup from its own measurement ranges**
- Fixed by correcting expected value to `EU 60A`

> This is **QA Catch #4** — AI wrote incorrect expected value in a test case. If QA had not been running tests, this wrong expectation would have gone unnoticed.

### Step 18: Full Test Execution
**Result:** ✅ **91/91 passed** (0.04s)

| Test file | Tests | Status |
|-----------|-------|--------|
| `test_basic_conversion.py` | 10 | ✅ All passed |
| `test_edge_cases.py` | 7 (QA catch #1) | ✅ All passed |
| `test_sister_sizing.py` | 10 | ✅ All passed |
| `test_conversion_matrix.py` | 30 (parametrized) | ✅ All passed |
| `test_cup_adjustment.py` | 10 (QA catch #2) | ✅ All passed |
| `test_new_systems.py` | 14 (Phase 3) | ✅ All passed |
| `test_measurement.py` | 10 (Phase 3) | ✅ All passed |
| **Total** | **91** | **✅ All passed** |

---

## All AI Catches Summary

| # | Phase | Category | What AI Got Wrong | How QA Caught It | Severity |
|---|-------|----------|-------------------|------------------|----------|
| 1 | 1 | Data gap | Band range only 28-44 | Edge case test: UK 54E | 🟡 Medium |
| 2 | 2 | Missing feature | No cup adjustment module | Domain knowledge question | 🔴 High |
| 3 | 2→3 | Process error | AI skipped Phase 3 (Scale) | QA checked against plan | 🟡 Medium |
| 4 | 3 | Wrong test data | Expected EU 60B, actual EU 60A | Test execution caught mismatch | 🟡 Medium |

---

## Phase 4 — Polish & Ship (2026-09-09)

### Step 19: Input Hardening Tests
**Who did it:** Claude Code (AI), directed by QA
**What was done:**
- Added 8 new edge case tests to `test_edge_cases.py` for malformed inputs
- Tests cover: empty cup, whitespace cup, lowercase cup, numeric cup, special characters, negative band, zero band

**New test classes:**
- `TestEmptyInput` — blank and whitespace cup values
- `TestCaseSensitivity` — lowercase `"b"` vs `"B"`, `"dd"` vs `"DD"`
- `TestGarbageCupValues` — numeric `"123"`, special char `"D+"`
- `TestInvalidBandValues` — negative and zero band numbers

### Step 20: README.md Rewrite
**Who did it:** Claude Code (AI), directed by QA
**What was done:**
- Rewrote README from 24 lines to full professional documentation
- Added architecture diagram, test methodology table, edge case coverage list
- Added AI catches summary with link to narrative log

### Step 21: AI Catches Narrative Log
**Who did it:** Claude Code (AI) drafted, QA reviewed content
**What was done:**
- Created `docs/ai_catches_log.md` — narrative-style documentation of all 4 catches
- Each catch includes: what happened, why it matters, how QA caught it, what was fixed
- Maps each catch to a QA skill: edge case thinking, domain knowledge, process discipline, data verification

### Step 22: Full Test Execution
**Result:** ✅ **99/99 passed** (0.05s)

| Test file | Tests | Status |
|-----------|-------|--------|
| `test_basic_conversion.py` | 10 | ✅ All passed |
| `test_edge_cases.py` | 15 (7 original + 8 hardening) | ✅ All passed |
| `test_sister_sizing.py` | 10 | ✅ All passed |
| `test_conversion_matrix.py` | 30 (parametrized) | ✅ All passed |
| `test_cup_adjustment.py` | 10 (QA catch #2) | ✅ All passed |
| `test_new_systems.py` | 14 (Phase 3) | ✅ All passed |
| `test_measurement.py` | 10 (Phase 3) | ✅ All passed |
| **Total** | **99** | **✅ All passed** |

---

*Last updated: 2026-09-09*
