# AI Catches Log — What I Found Wrong in AI-Generated Code

> This document records specific instances where Claude Code (AI) produced
> incorrect output during development, and how I (the QA engineer) caught each one.
> Each catch demonstrates a different QA skill: domain knowledge, edge case thinking,
> process discipline, and data verification.

---

## Catch #1: Band Range Data Gap

**Phase:** 1 (Foundation)
**Category:** Data gap
**Severity:** 🟡 Medium

### What happened
After Phase 1 was built with 10 passing tests, I decided to test an edge case
that wasn't covered: **what happens with plus-size bands?**

I asked: *"What does the system do with UK 54E → EU?"*

The system crashed with an unhandled `ValueError: Band 54 not found`. The band
conversion table only covered sizes 28–44 (9 bands). Band 54 is a real size
sold by plus-size brands like Elomi and Goddess.

### Why this matters
In a production bra-fitting app, a plus-size customer entering their real size
would get an application crash instead of a helpful error message. This is both
a data completeness issue and an error handling issue.

### How I caught it
**Edge case thinking.** After verifying the "happy path" tests passed, I
immediately asked: *what's the largest band size that exists in the real world?*
My 2 years working in lingerie wholesale at Bình Tây market taught me that
plus-size bands go well beyond 44.

### What was fixed
- Added 7 edge case tests to `test_edge_cases.py`
- Converter now raises a clear `ValueError` with the valid range
- Tests verify the error message includes helpful context

---

## Catch #2: Missing Cup Adjustment Feature

**Phase:** 2 (Expand & Harden)
**Category:** Missing feature
**Severity:** 🔴 High — entire feature was missing

### What happened
AI built the sister sizing module, which recommends alternative sizes when the
**band** doesn't fit (e.g., 34C → 36B or 32D — same cup volume, different band).

I asked: *"Sister sizing changes band + cup to keep the same volume. But what
about when the band fits fine and only the cup needs adjusting?"*

AI had no answer — this feature simply didn't exist. The system could only
suggest alternatives where both band AND cup change. It couldn't handle the
common scenario: "My band fits perfectly, but the cup is slightly too small."

### Why this matters
In real bra fitting, cup adjustment (same band, different cup) is just as
common as sister sizing. A customer who says "the band is fine but the cup
spills over" needs cup-up recommendations, not sister sizes.

### How I caught it
**Domain knowledge.** Working in lingerie sales, I knew that customers
frequently ask for the same band but a different cup. This is a fundamental
fitting recommendation that any sizing engine must support.

### What was fixed
- Created entirely new module: `src/sizing_engine/cup_adjustment.py`
- Created 10 tests in `tests/test_cup_adjustment.py`
- Covers boundary cases: cup A (smallest, no cup-down), max cup (no cup-up)

---

## Catch #3: AI Skipped an Entire Phase

**Phase:** 2 → 3 transition
**Category:** Process error
**Severity:** 🟡 Medium — would have shipped incomplete project

### What happened
After Phase 2 was complete (67 tests passing), AI proposed moving directly
to Phase 4 (Polish & Ship). It completely skipped Phase 3 (Scale), which was
supposed to:
- Add 3 new sizing systems (FR, AU, JP)
- Build the body measurement module
- Add roundtrip and cross-system tests

### Why this matters
If I had agreed, the project would have been shipped missing 3 planned sizing
systems and the measurement-to-size feature — key functionality that
demonstrates the engine's real-world capability.

### How I caught it
**Process discipline.** I checked AI's proposal against the original
implementation plan and noticed the gap immediately:
*"Phase 3 as planned is Scale, right? The tasks you described above belong to
Phase 4."*

### What was fixed
- AI acknowledged the error and implemented Phase 3 as planned
- Added FR/AU/JP systems, measurement module, 24 new tests
- Total tests went from 67 to 91

---

## Catch #4: Wrong Expected Value in Test Case

**Phase:** 3 (Scale)
**Category:** Wrong test data
**Severity:** 🟡 Medium — test would have passed with wrong assertion

### What happened
AI generated `test_07_smallest_band` in `test_measurement.py` with this
expected output:

```python
# AI wrote:
result = recommend_size(58, 70, SizeSystem.EU)
assert result == BraSize(60, "B", SizeSystem.EU)  # WRONG
```

The actual correct value is `EU 60A`, not `EU 60B`.

**The math:**
- Underbust 58cm → EU band 60 ✅
- Bust 70cm - underbust 58cm = 12cm difference
- 12cm falls in cup range 10–12.5cm → cup index 0 = **A** (not B)
- AI miscounted the cup index from its own measurement ranges

### Why this matters
This is a subtle but critical error. If the test had been written with the
wrong expected value AND the code also had the same bug, both would have
agreed and the test would pass — hiding a real calculation error. Only by
running the test against the actual implementation (which was correct) did
the mismatch surface.

### How I caught it
**Test execution + manual verification.** I ran `pytest -v`, saw the assertion
failure, then manually calculated the expected value using the measurement
ranges defined in the code. The code was right; the test expectation was wrong.

### What was fixed
- Changed expected value from `EU 60B` to `EU 60A`
- All 91 tests passed after the fix

---

## Summary

| # | Category | Skill Demonstrated | Impact |
|---|----------|-------------------|--------|
| 1 | Data gap | Edge case thinking | Prevented plus-size customer crashes |
| 2 | Missing feature | Domain knowledge | Added entire cup adjustment module |
| 3 | Process error | Process discipline | Prevented shipping incomplete product |
| 4 | Wrong test data | Data verification | Corrected silent calculation error |

**Key takeaway:** AI tools generate code fast, but they don't know what they
don't know. A QA engineer brings domain expertise, edge case instincts, and
process discipline that AI currently cannot replicate.
