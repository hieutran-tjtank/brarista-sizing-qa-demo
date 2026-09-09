"""
Phase 1 — Basic Size Conversion Tests (10 cases)

These 10 test cases cover the fundamental conversion logic between US, UK, and EU
sizing systems. They are designed to be reviewed manually before scaling to
hundreds of parametrized tests.

Test Design Strategy:
- Tests 1-2: Simple conversions (cups A-D, where all systems agree)
- Tests 3-4: The DD divergence zone (US/UK DD vs EU E)
- Tests 5-6: Beyond DD (US DDD = UK E = EU F)
- Tests 7-9: Reverse conversions (UK→US, EU→US, EU→UK)
- Test 10: Large cup edge case (UK GG)

How to review:
1. Read each test case — does the expected output make sense?
2. Cross-reference with a real size chart (e.g., https://www.bratabase.com/knowledge/)
3. Pay special attention to tests 3-6: this is where AI typically makes mistakes
"""

import pytest
from sizing_engine.models import BraSize, SizeSystem
from sizing_engine.converter import convert_size


# ── Test 1: Basic band + simple cup ─────────────────────────────────────────
# US 34B → EU 75B
# Band: 34 (US/inch) → 75 (EU/cm) — straightforward index mapping
# Cup: B → B — cups A through D are identical across all 3 systems
def test_01_us_to_eu_simple():
    result = convert_size(BraSize(34, "B", SizeSystem.US), SizeSystem.EU)
    assert result == BraSize(75, "B", SizeSystem.EU)


# ── Test 2: US to UK for cups ≤ D ──────────────────────────────────────────
# US 34C → UK 34C
# Band: US and UK both use inches, so 34 → 34
# Cup: C is the same in both systems (divergence starts at DD)
def test_02_us_to_uk_simple():
    result = convert_size(BraSize(34, "C", SizeSystem.US), SizeSystem.UK)
    assert result == BraSize(34, "C", SizeSystem.UK)


# ── Test 3: DD is the same in US and UK ────────────────────────────────────
# US 36DD → UK 36DD
# Both US and UK call volume index 4 "DD"
# This is a common confusion point — people assume they might differ
def test_03_us_dd_to_uk():
    result = convert_size(BraSize(36, "DD", SizeSystem.US), SizeSystem.UK)
    assert result == BraSize(36, "DD", SizeSystem.UK)


# ── Test 4: DD (US) → E (EU) — THE KEY TRAP ───────────────────────────────
# US 36DD → EU 80E
# US "DD" is volume index 4. EU calls volume index 4 "E" (not "DD").
# This is the #1 conversion error that AI makes — mapping DD → DD across systems.
# ⚠️ If this test fails, the converter has the most common real-world bug.
def test_04_us_dd_to_eu():
    result = convert_size(BraSize(36, "DD", SizeSystem.US), SizeSystem.EU)
    assert result == BraSize(80, "E", SizeSystem.EU)


# ── Test 5: DDD (US) → E (UK) — deeper divergence ─────────────────────────
# US 36DDD → UK 36E
# US uses "DDD" for volume index 5. UK calls the same volume "E".
# Beyond DD, the naming conventions split completely.
def test_05_us_ddd_to_uk():
    result = convert_size(BraSize(36, "DDD", SizeSystem.US), SizeSystem.UK)
    assert result == BraSize(36, "E", SizeSystem.UK)


# ── Test 6: DDD (US) → F (EU) ─────────────────────────────────────────────
# US 36DDD → EU 80F
# Volume index 5: US="DDD", EU="F"
# Band: 36 (US/inch) → 80 (EU/cm)
def test_06_us_ddd_to_eu():
    result = convert_size(BraSize(36, "DDD", SizeSystem.US), SizeSystem.EU)
    assert result == BraSize(80, "F", SizeSystem.EU)


# ── Test 7: Reverse — UK F → US G ─────────────────────────────────────────
# UK 34F → US 34G
# Volume index 6: UK="F", US="G"
# Tests that reverse conversion also works correctly
def test_07_uk_f_to_us():
    result = convert_size(BraSize(34, "F", SizeSystem.UK), SizeSystem.US)
    assert result == BraSize(34, "G", SizeSystem.US)


# ── Test 8: EU to US — band + simple cup ───────────────────────────────────
# EU 70A → US 32A
# Band: 70 (EU/cm) → 32 (US/inch)
# Cup: A is the same everywhere
def test_08_eu_to_us():
    result = convert_size(BraSize(70, "A", SizeSystem.EU), SizeSystem.US)
    assert result == BraSize(32, "A", SizeSystem.US)


# ── Test 9: EU E → UK DD — reverse of the key trap ────────────────────────
# EU 80E → UK 36DD
# Volume index 4: EU="E", UK="DD"
# This is the reverse of Test 4 — verifying bidirectional conversion
def test_09_eu_e_to_uk():
    result = convert_size(BraSize(80, "E", SizeSystem.EU), SizeSystem.UK)
    assert result == BraSize(36, "DD", SizeSystem.UK)


# ── Test 10: Large cup edge case ───────────────────────────────────────────
# UK 38GG → EU 85J
# Volume index 9 (the largest in our chart): UK="GG", EU="J"
# Band: 38 (UK/inch) → 85 (EU/cm)
# Tests the boundary of our cup conversion table
def test_10_uk_gg_to_eu():
    result = convert_size(BraSize(38, "GG", SizeSystem.UK), SizeSystem.EU)
    assert result == BraSize(85, "J", SizeSystem.EU)
