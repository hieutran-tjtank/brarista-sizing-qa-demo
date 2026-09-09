"""
Body Measurement Tests — Phase 3

Tests the measurement → size recommendation logic.
This is the core of Brarista's AI: customer provides body measurements,
system recommends a bra size.

Test Design:
- Tests 1-3: Normal measurements → correct size in EU, US, UK
- Tests 4-5: FR, AU, JP systems (new Phase 3 systems)
- Tests 6-7: Boundary measurements (edge of ranges)
- Tests 8-10: Invalid inputs (bust < underbust, out of range)

Key verification for QA:
- Underbust 78cm should give EU band 80 (not 75 or 85)
- Bust-underbust difference of 15cm = cup C (not B or D)
- Same measurements → different system = different band number but same cup volume
"""

import pytest
from sizing_engine.models import BraSize, SizeSystem
from sizing_engine.measurement import recommend_size


# ── Normal measurements ────────────────────────────────────────────────────

def test_01_basic_eu():
    """Underbust 78cm, bust 93cm → EU 80C
    Band: 78cm falls in 78-82 range → EU 80
    Cup: 93-78 = 15cm difference → cup index 2 = C"""
    result = recommend_size(78, 93, SizeSystem.EU)
    assert result == BraSize(80, "C", SizeSystem.EU)


def test_02_basic_us():
    """Same measurements, US system → US 36C
    Band: EU 80 → US 36
    Cup: C is the same in US"""
    result = recommend_size(78, 93, SizeSystem.US)
    assert result == BraSize(36, "C", SizeSystem.US)


def test_03_basic_uk():
    """Same measurements, UK system → UK 36C"""
    result = recommend_size(78, 93, SizeSystem.UK)
    assert result == BraSize(36, "C", SizeSystem.UK)


# ── New Phase 3 systems ────────────────────────────────────────────────────

def test_04_french_system():
    """Underbust 78cm, bust 93cm → FR 95C
    FR band = EU band + 15 → 80 + 15 = 95
    FR cup = same as EU cup = C"""
    result = recommend_size(78, 93, SizeSystem.FR)
    assert result == BraSize(95, "C", SizeSystem.FR)


def test_05_australian_system():
    """Underbust 78cm, bust 93cm → AU 14C
    AU uses own numbering. EU 80 maps to AU 14.
    AU cups A-D same as US/UK/EU"""
    result = recommend_size(78, 93, SizeSystem.AU)
    assert result == BraSize(14, "C", SizeSystem.AU)


def test_06_japanese_system():
    """Underbust 78cm, bust 93cm → JP 80C
    JP bands = EU bands (both use cm)
    JP cups = EU cups"""
    result = recommend_size(78, 93, SizeSystem.JP)
    assert result == BraSize(80, "C", SizeSystem.JP)


# ── Boundary measurements ─────────────────────────────────────────────────

def test_07_smallest_band():
    """Underbust 58cm (smallest) → EU 60A
    58cm is the low end of the first range
    Bust 70cm - underbust 58cm = 12cm diff → cup A (10-12.5cm range)"""
    result = recommend_size(58, 70, SizeSystem.EU)
    assert result == BraSize(60, "A", SizeSystem.EU)


def test_08_dd_cup_threshold():
    """Underbust 73cm, bust 94cm → difference 21cm → cup DD/E
    21cm falls in 20-22.5 range → cup index 4
    EU cup index 4 = E, US cup index 4 = DD"""
    eu_result = recommend_size(73, 94, SizeSystem.EU)
    us_result = recommend_size(73, 94, SizeSystem.US)
    assert eu_result.cup == "E", f"EU should be E, got {eu_result.cup}"
    assert us_result.cup == "DD", f"US should be DD, got {us_result.cup}"


# ── Invalid inputs ─────────────────────────────────────────────────────────

def test_09_bust_smaller_than_underbust():
    """Bust 70cm < underbust 80cm → should raise ValueError"""
    with pytest.raises(ValueError, match="must be larger than underbust"):
        recommend_size(80, 70, SizeSystem.EU)


def test_10_underbust_out_of_range():
    """Underbust 120cm is outside our supported range → ValueError"""
    with pytest.raises(ValueError, match="outside supported range"):
        recommend_size(120, 140, SizeSystem.EU)
