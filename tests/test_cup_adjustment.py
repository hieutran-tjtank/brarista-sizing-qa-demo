"""
Cup Adjustment Tests — QA Catch #2

This entire test file exists because the QA engineer identified a gap:
"Sister sizing changes band+cup to keep same volume. But what about
when the band fits fine and only the cup needs adjusting?"

Claude Code (AI) only implemented sister sizing. This module was added
after QA review caught the missing feature.

Test Design:
- Tests 1-3: Normal cup adjustment (both up and down exist)
- Tests 4-5: Boundary — smallest cup (A), no cup-down
- Tests 6-7: Boundary — largest cup (J/GG), no cup-up
- Tests 8-9: US DD/DDD zone — verify correct cup sequence
- Test 10: Band stays unchanged (core invariant)
"""

import pytest
from sizing_engine.models import BraSize, SizeSystem
from sizing_engine.cup_adjustment import get_cup_adjustment


# ── Normal cup adjustment ──────────────────────────────────────────────────

def test_01_us_34c_cup_adjust():
    """US 34C → cup up: 34D, cup down: 34B. Band stays 34."""
    result = get_cup_adjustment(BraSize(34, "C", SizeSystem.US))
    assert result["base"] == BraSize(34, "C", SizeSystem.US)
    assert result["cup_up"] == BraSize(34, "D", SizeSystem.US)
    assert result["cup_down"] == BraSize(34, "B", SizeSystem.US)


def test_02_uk_36d_cup_adjust():
    """UK 36D → cup up: 36DD, cup down: 36C"""
    result = get_cup_adjustment(BraSize(36, "D", SizeSystem.UK))
    assert result["cup_up"] == BraSize(36, "DD", SizeSystem.UK)
    assert result["cup_down"] == BraSize(36, "C", SizeSystem.UK)


def test_03_eu_80d_cup_adjust():
    """EU 80D → cup up: 80E, cup down: 80C"""
    result = get_cup_adjustment(BraSize(80, "D", SizeSystem.EU))
    assert result["cup_up"] == BraSize(80, "E", SizeSystem.EU)
    assert result["cup_down"] == BraSize(80, "C", SizeSystem.EU)


# ── Boundary: Smallest cup (A) — no cup-down ──────────────────────────────

def test_04_cup_a_no_down():
    """US 34A → cup up: 34B, cup down: None (A is smallest)"""
    result = get_cup_adjustment(BraSize(34, "A", SizeSystem.US))
    assert result["cup_up"] == BraSize(34, "B", SizeSystem.US)
    assert result["cup_down"] is None, "Cup A is smallest — no cup-down"


def test_05_eu_cup_a_no_down():
    """EU 75A → cup up: 75B, cup down: None"""
    result = get_cup_adjustment(BraSize(75, "A", SizeSystem.EU))
    assert result["cup_up"] == BraSize(75, "B", SizeSystem.EU)
    assert result["cup_down"] is None


# ── Boundary: Largest cup — no cup-up ─────────────────────────────────────

def test_06_us_max_cup_no_up():
    """US 36J → cup up: None (J is largest), cup down: 36I"""
    result = get_cup_adjustment(BraSize(36, "J", SizeSystem.US))
    assert result["cup_up"] is None, "Cup J is largest in US — no cup-up"
    assert result["cup_down"] == BraSize(36, "I", SizeSystem.US)


def test_07_uk_max_cup_no_up():
    """UK 36GG → cup up: None (GG is largest), cup down: 36G"""
    result = get_cup_adjustment(BraSize(36, "GG", SizeSystem.UK))
    assert result["cup_up"] is None, "Cup GG is largest in UK — no cup-up"
    assert result["cup_down"] == BraSize(36, "G", SizeSystem.UK)


# ── DD/DDD zone — the tricky sequence ─────────────────────────────────────
# US cup sequence: ...D, DD, DDD, G, H...
# Going up from DD should give DDD, NOT E (E is UK/EU, not US)

def test_08_us_dd_cup_up_is_ddd():
    """US 34DD → cup up: 34DDD (NOT 34E — that's EU/UK)"""
    result = get_cup_adjustment(BraSize(34, "DD", SizeSystem.US))
    assert result["cup_up"] == BraSize(34, "DDD", SizeSystem.US)
    assert result["cup_down"] == BraSize(34, "D", SizeSystem.US)


def test_09_uk_dd_cup_up_is_e():
    """UK 34DD → cup up: 34E (UK uses E after DD, unlike US which uses DDD)"""
    result = get_cup_adjustment(BraSize(34, "DD", SizeSystem.UK))
    assert result["cup_up"] == BraSize(34, "E", SizeSystem.UK)
    assert result["cup_down"] == BraSize(34, "D", SizeSystem.UK)


# ── Core invariant: band NEVER changes ─────────────────────────────────────

def test_10_band_unchanged_all_adjustments():
    """For any cup adjustment, the band number must stay exactly the same."""
    sizes_to_test = [
        BraSize(32, "C", SizeSystem.US),
        BraSize(36, "DD", SizeSystem.UK),
        BraSize(80, "F", SizeSystem.EU),
    ]
    for size in sizes_to_test:
        result = get_cup_adjustment(size)
        if result["cup_up"]:
            assert result["cup_up"].band == size.band, (
                f"Cup-up changed band! {size} → {result['cup_up']}"
            )
        if result["cup_down"]:
            assert result["cup_down"].band == size.band, (
                f"Cup-down changed band! {size} → {result['cup_down']}"
            )
