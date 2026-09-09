"""
Sister Sizing Tests

Tests the sister sizing logic — finding alternative sizes with the same
cup volume but different band fit.

Test Design:
- Tests 1-3: Normal sister sizing (both up and down exist)
- Tests 4-5: Boundary — cup A (no sister-down possible)
- Tests 6-7: Boundary — max band or min band limits
- Tests 8-9: UK system (different cup letters, same rules)
- Test 10: EU system (different band numbers)

Key verification for QA:
- Sister UP = band +1 step, cup -1 step → SAME cup volume
- Sister DOWN = band -1 step, cup +1 step → SAME cup volume
- Boundary cases should return None, NOT crash
"""

import pytest
from sizing_engine.models import BraSize, SizeSystem
from sizing_engine.sister_sizing import get_sister_sizes


# ── Normal sister sizing ───────────────────────────────────────────────────

def test_01_us_34c_sisters():
    """US 34C → up: 36B, down: 32D"""
    result = get_sister_sizes(BraSize(34, "C", SizeSystem.US))
    assert result["base"] == BraSize(34, "C", SizeSystem.US)
    assert result["up"] == BraSize(36, "B", SizeSystem.US)
    assert result["down"] == BraSize(32, "D", SizeSystem.US)


def test_02_us_36dd_sisters():
    """US 36DD → up: 38D, down: 34DDD"""
    result = get_sister_sizes(BraSize(36, "DD", SizeSystem.US))
    assert result["up"] == BraSize(38, "D", SizeSystem.US)
    assert result["down"] == BraSize(34, "DDD", SizeSystem.US)


def test_03_us_32b_sisters():
    """US 32B → up: 34A, down: 30C"""
    result = get_sister_sizes(BraSize(32, "B", SizeSystem.US))
    assert result["up"] == BraSize(34, "A", SizeSystem.US)
    assert result["down"] == BraSize(30, "C", SizeSystem.US)


# ── Boundary: Cup A — no sister-down ───────────────────────────────────────
# Cup A is the smallest cup. There's no cup below A.
# Sister-down (smaller band + bigger cup) IS possible: 34A → 32B
# Sister-up (bigger band + smaller cup) is NOT possible: no cup below A

def test_04_cup_a_no_sister_up():
    """US 34A → up: None (no cup below A), down: 32B"""
    result = get_sister_sizes(BraSize(34, "A", SizeSystem.US))
    assert result["up"] is None, "Cup A has no smaller cup — sister-up should be None"
    assert result["down"] == BraSize(32, "B", SizeSystem.US)


def test_05_cup_a_min_band():
    """US 28A → up: None, down: None (both boundaries hit)"""
    result = get_sister_sizes(BraSize(28, "A", SizeSystem.US))
    assert result["up"] is None, "Cup A: no smaller cup"
    assert result["down"] is None, "Band 28: no smaller band"


# ── Boundary: Max/Min band ─────────────────────────────────────────────────

def test_06_max_band_no_sister_up():
    """US 44D → up: None (no band above 44), down: 42DD"""
    result = get_sister_sizes(BraSize(44, "D", SizeSystem.US))
    assert result["up"] is None, "Band 44 is max — no sister-up"
    assert result["down"] == BraSize(42, "DD", SizeSystem.US)


def test_07_min_band_no_sister_down():
    """US 28C → up: 30B, down: None (no band below 28)"""
    result = get_sister_sizes(BraSize(28, "C", SizeSystem.US))
    assert result["up"] == BraSize(30, "B", SizeSystem.US)
    assert result["down"] is None, "Band 28 is min — no sister-down"


# ── UK system — different cup letters, same rules ──────────────────────────

def test_08_uk_36e_sisters():
    """UK 36E → up: 38DD, down: 34F
    Note: UK cup sequence is ...D, DD, E, F, FF...
    So E-1 = DD (sister up), E+1 = F (sister down)"""
    result = get_sister_sizes(BraSize(36, "E", SizeSystem.UK))
    assert result["up"] == BraSize(38, "DD", SizeSystem.UK)
    assert result["down"] == BraSize(34, "F", SizeSystem.UK)


def test_09_uk_34ff_sisters():
    """UK 34FF → up: 36F, down: 32G
    FF is a UK-specific cup. FF-1 = F, FF+1 = G"""
    result = get_sister_sizes(BraSize(34, "FF", SizeSystem.UK))
    assert result["up"] == BraSize(36, "F", SizeSystem.UK)
    assert result["down"] == BraSize(32, "G", SizeSystem.UK)


# ── EU system — different band numbers ─────────────────────────────────────

def test_10_eu_75d_sisters():
    """EU 75D → up: 80C, down: 70E
    EU bands go in steps of 5cm: ...70, 75, 80...
    EU cups: ...C, D, E, F..."""
    result = get_sister_sizes(BraSize(75, "D", SizeSystem.EU))
    assert result["up"] == BraSize(80, "C", SizeSystem.EU)
    assert result["down"] == BraSize(70, "E", SizeSystem.EU)
