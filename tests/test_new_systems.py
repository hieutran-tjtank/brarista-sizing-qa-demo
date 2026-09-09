"""
Phase 3 — New System Conversion Tests (FR, AU, JP)

Tests specific to the 3 new sizing systems added in Phase 3.
Focuses on the unique characteristics of each:
- FR: bands = EU + 15cm, cups = EU cups
- AU: unique band numbering, cups follow UK system
- JP: bands = EU bands, cups = EU cups

These tests verify that the new systems integrate correctly with
the existing converter.
"""

import pytest
from sizing_engine.models import BraSize, SizeSystem
from sizing_engine.converter import convert_size


# ── French system: EU + 15cm offset ───────────────────────────────────────

def test_fr_band_is_eu_plus_15():
    """EU 75C → FR 90C. French band = EU band + 15."""
    result = convert_size(BraSize(75, "C", SizeSystem.EU), SizeSystem.FR)
    assert result == BraSize(90, "C", SizeSystem.FR)


def test_fr_to_us():
    """FR 95D → US 36D. FR 95 = EU 80 = US 36."""
    result = convert_size(BraSize(95, "D", SizeSystem.FR), SizeSystem.US)
    assert result == BraSize(36, "D", SizeSystem.US)


def test_us_to_fr_with_cup_divergence():
    """US 36DD → FR 95E. DD(US) = E(FR/EU)."""
    result = convert_size(BraSize(36, "DD", SizeSystem.US), SizeSystem.FR)
    assert result == BraSize(95, "E", SizeSystem.FR)


# ── Australian system: unique bands, UK-style cups ─────────────────────────

def test_au_band_numbering():
    """US 34C → AU 12C. AU uses 6,8,10,12,14..."""
    result = convert_size(BraSize(34, "C", SizeSystem.US), SizeSystem.AU)
    assert result == BraSize(12, "C", SizeSystem.AU)


def test_au_uses_uk_cups():
    """US 36DDD → AU 14E. AU follows UK cup naming (E, not DDD)."""
    result = convert_size(BraSize(36, "DDD", SizeSystem.US), SizeSystem.AU)
    assert result == BraSize(14, "E", SizeSystem.AU)


def test_au_to_eu():
    """AU 16DD → EU 85E. AU DD = EU E (AU follows UK cups)."""
    result = convert_size(BraSize(16, "DD", SizeSystem.AU), SizeSystem.EU)
    assert result == BraSize(85, "E", SizeSystem.EU)


# ── Japanese system: same as EU ────────────────────────────────────────────

def test_jp_equals_eu():
    """JP 75C → EU 75C. JP uses same bands and cups as EU."""
    result = convert_size(BraSize(75, "C", SizeSystem.JP), SizeSystem.EU)
    assert result == BraSize(75, "C", SizeSystem.EU)


def test_jp_to_us():
    """JP 80E → US 36DD. JP E = US DD (same volume index)."""
    result = convert_size(BraSize(80, "E", SizeSystem.JP), SizeSystem.US)
    assert result == BraSize(36, "DD", SizeSystem.US)


def test_us_to_jp():
    """US 34B → JP 75B. Basic conversion through EU equivalent."""
    result = convert_size(BraSize(34, "B", SizeSystem.US), SizeSystem.JP)
    assert result == BraSize(75, "B", SizeSystem.JP)


# ── Cross-system roundtrip with new systems ────────────────────────────────

@pytest.mark.parametrize("original, via_system", [
    (BraSize(90, "D", SizeSystem.FR), SizeSystem.US),
    (BraSize(14, "C", SizeSystem.AU), SizeSystem.EU),
    (BraSize(75, "E", SizeSystem.JP), SizeSystem.UK),
    (BraSize(36, "DD", SizeSystem.US), SizeSystem.FR),
    (BraSize(85, "F", SizeSystem.EU), SizeSystem.AU),
])
def test_roundtrip_new_systems(original, via_system):
    """Converting A→B→A must return original for new systems too."""
    converted = convert_size(original, via_system)
    roundtrip = convert_size(converted, original.system)
    assert roundtrip == original, (
        f"Roundtrip failed: {original} → {converted} → {roundtrip}"
    )
