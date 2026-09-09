"""
Edge Case Tests — Triggered by QA Review

Two groups:
1. Phase 1 catch: Out-of-range inputs (QA found UK 54E crash)
2. Phase 4 hardening: Garbage/malformed inputs (empty, lowercase, numeric,
   whitespace, negative band, zero band) — the kind of inputs a real user
   might submit through a web form or API.

QA Catch Reference: BUILD_LOG.md → Phase 1 → AI Errors Caught #1
"""

import pytest
from sizing_engine.models import BraSize, SizeSystem
from sizing_engine.converter import convert_size


# ── Test: Out-of-range band (THE QA CATCH) ─────────────────────────────────
# UK 54E → EU should raise ValueError
# QA found this: band 54 is not in our data (max is 44)
# Real-world impact: plus-size customers would get a crash instead of a result
class TestOutOfRangeBand:

    def test_band_too_large(self):
        """Band 54 exceeds our data range (max 44). Should raise ValueError."""
        with pytest.raises(ValueError, match="Band 54 not found"):
            convert_size(BraSize(54, "E", SizeSystem.UK), SizeSystem.EU)

    def test_band_too_small(self):
        """Band 26 is below our data range (min 28). Should raise ValueError."""
        with pytest.raises(ValueError, match="Band 26 not found"):
            convert_size(BraSize(26, "A", SizeSystem.US), SizeSystem.EU)

    def test_band_between_sizes(self):
        """Band 33 doesn't exist (bands go 30, 32, 34). Should raise ValueError."""
        with pytest.raises(ValueError, match="Band 33 not found"):
            convert_size(BraSize(33, "B", SizeSystem.US), SizeSystem.EU)


# ── Test: Invalid cup letter ───────────────────────────────────────────────
# What if someone inputs a cup letter that doesn't exist in the system?
class TestInvalidCup:

    def test_nonexistent_cup(self):
        """Cup 'Z' doesn't exist in any system. Should raise ValueError."""
        with pytest.raises(ValueError, match="Cup 'Z' not found"):
            convert_size(BraSize(34, "Z", SizeSystem.US), SizeSystem.EU)

    def test_uk_cup_in_us_system(self):
        """UK uses 'FF' but US doesn't. Inputting FF as US should raise ValueError."""
        with pytest.raises(ValueError, match="Cup 'FF' not found in US"):
            convert_size(BraSize(34, "FF", SizeSystem.US), SizeSystem.EU)


# ── Test: Same-system conversion (no-op) ───────────────────────────────────
# Converting US 34B to US should return the same size unchanged
class TestSameSystemConversion:

    def test_same_system_returns_identical(self):
        """Converting to the same system should return the exact same size."""
        original = BraSize(34, "B", SizeSystem.US)
        result = convert_size(original, SizeSystem.US)
        assert result == original

    def test_same_system_eu(self):
        """Same-system conversion for EU sizes."""
        original = BraSize(75, "E", SizeSystem.EU)
        result = convert_size(original, SizeSystem.EU)
        assert result == original


# ── Test: Garbage / malformed inputs (Phase 4 hardening) ───────────────────
# Real users type all kinds of nonsense into size fields.
# A robust converter must reject bad input with clear errors, not crash.

class TestEmptyInput:

    def test_empty_cup_string(self):
        """Cup = '' (empty string). User left the cup field blank on a form."""
        with pytest.raises(ValueError, match="Cup '' not found"):
            convert_size(BraSize(34, "", SizeSystem.US), SizeSystem.EU)

    def test_whitespace_cup(self):
        """Cup = ' B ' (leading/trailing spaces). Copy-paste artifact."""
        with pytest.raises(ValueError, match="Cup ' B ' not found"):
            convert_size(BraSize(34, " B ", SizeSystem.US), SizeSystem.EU)


class TestCaseSensitivity:

    def test_lowercase_cup(self):
        """Cup = 'b' instead of 'B'. User typed lowercase.
        System should reject — cups are uppercase in all standards."""
        with pytest.raises(ValueError, match="Cup 'b' not found"):
            convert_size(BraSize(34, "b", SizeSystem.US), SizeSystem.EU)

    def test_lowercase_dd(self):
        """Cup = 'dd' instead of 'DD'. Common typo in forms."""
        with pytest.raises(ValueError, match="Cup 'dd' not found"):
            convert_size(BraSize(36, "dd", SizeSystem.US), SizeSystem.EU)


class TestGarbageCupValues:

    def test_numeric_cup(self):
        """Cup = '123'. User confused cup with band number."""
        with pytest.raises(ValueError, match="Cup '123' not found"):
            convert_size(BraSize(34, "123", SizeSystem.US), SizeSystem.EU)

    def test_special_character_cup(self):
        """Cup = 'D+'. Some brands use 'D+' informally for DD — system shouldn't accept."""
        with pytest.raises(ValueError, match=r"Cup 'D\+' not found"):
            convert_size(BraSize(34, "D+", SizeSystem.US), SizeSystem.EU)


class TestInvalidBandValues:

    def test_negative_band(self):
        """Band = -34. Nonsensical input that should be rejected."""
        with pytest.raises(ValueError, match="Band -34 not found"):
            convert_size(BraSize(-34, "B", SizeSystem.US), SizeSystem.EU)

    def test_zero_band(self):
        """Band = 0. No bra has band size zero."""
        with pytest.raises(ValueError, match="Band 0 not found"):
            convert_size(BraSize(0, "B", SizeSystem.US), SizeSystem.EU)

