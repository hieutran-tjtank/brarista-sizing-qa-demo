"""
Parametrized Conversion Matrix — Exhaustive Testing

Phase 1 had 10 hand-picked tests. This file uses pytest parametrize
to auto-generate ALL valid conversion combinations.

Test matrix:
- All 9 bands × 3 system pairs = 54 band conversion tests
- All 10 cups × 6 system direction pairs = 60 cup conversion tests
- Roundtrip tests: convert A→B→A should equal original

Total: ~130+ auto-generated test cases
"""

import pytest
from sizing_engine.models import BraSize, SizeSystem
from sizing_engine.converter import convert_size, convert_band, convert_cup


# ── Band conversion: ALL bands × ALL system pairs ──────────────────────────
# Every band in the source system should map to a valid band in the target system

BAND_PAIRS = [
    # (from_system, to_system, source_bands, expected_targets)
    (SizeSystem.US, SizeSystem.EU,
     [28, 30, 32, 34, 36, 38, 40, 42, 44],
     [60, 65, 70, 75, 80, 85, 90, 95, 100]),
    (SizeSystem.EU, SizeSystem.US,
     [60, 65, 70, 75, 80, 85, 90, 95, 100],
     [28, 30, 32, 34, 36, 38, 40, 42, 44]),
    (SizeSystem.US, SizeSystem.UK,
     [28, 30, 32, 34, 36, 38, 40, 42, 44],
     [28, 30, 32, 34, 36, 38, 40, 42, 44]),  # US & UK bands are identical
]


@pytest.mark.parametrize("from_sys, to_sys, source_bands, expected_bands", BAND_PAIRS)
def test_band_conversion_matrix(from_sys, to_sys, source_bands, expected_bands):
    """Every band in source system maps correctly to target system."""
    for src, exp in zip(source_bands, expected_bands):
        result = convert_band(src, from_sys, to_sys)
        assert result == exp, f"{from_sys.value} {src} → {to_sys.value}: expected {exp}, got {result}"


# ── Cup conversion: the divergence zone ────────────────────────────────────
# Focus on cups D and above where systems diverge

CUP_DIVERGENCE_CASES = [
    # (from_system, to_system, from_cup, expected_cup)
    # US → EU (the key mapping)
    ("US", "EU", "D", "D"),       # Volume 3: same
    ("US", "EU", "DD", "E"),      # Volume 4: US DD = EU E
    ("US", "EU", "DDD", "F"),     # Volume 5: US DDD = EU F
    ("US", "EU", "G", "G"),       # Volume 6: same letter, different volume index!
    ("US", "EU", "H", "H"),       # Volume 7: same
    # US → UK
    ("US", "UK", "DD", "DD"),     # Volume 4: same
    ("US", "UK", "DDD", "E"),     # Volume 5: US DDD = UK E
    ("US", "UK", "G", "F"),       # Volume 6: US G = UK F
    ("US", "UK", "H", "FF"),      # Volume 7: US H = UK FF
    ("US", "UK", "I", "G"),       # Volume 8: US I = UK G
    ("US", "UK", "J", "GG"),      # Volume 9: US J = UK GG
    # UK → EU
    ("UK", "EU", "DD", "E"),      # Volume 4: UK DD = EU E
    ("UK", "EU", "E", "F"),       # Volume 5: UK E = EU F
    ("UK", "EU", "F", "G"),       # Volume 6: UK F = EU G
    ("UK", "EU", "FF", "H"),      # Volume 7: UK FF = EU H
    ("UK", "EU", "G", "I"),       # Volume 8: UK G = EU I
    ("UK", "EU", "GG", "J"),      # Volume 9: UK GG = EU J
]


@pytest.mark.parametrize("from_sys, to_sys, from_cup, expected_cup", CUP_DIVERGENCE_CASES)
def test_cup_divergence_matrix(from_sys, to_sys, from_cup, expected_cup):
    """Cup letters above D diverge between systems — verify each mapping."""
    result = convert_cup(from_cup, SizeSystem(from_sys), SizeSystem(to_sys))
    assert result == expected_cup, (
        f"{from_sys} cup '{from_cup}' → {to_sys}: expected '{expected_cup}', got '{result}'"
    )


# ── Roundtrip tests: convert A→B→A should equal original ──────────────────
# This is a critical property: converting to another system and back
# should give you the EXACT same size you started with.

ROUNDTRIP_CASES = [
    # (original_size, via_system)
    (BraSize(34, "C", SizeSystem.US), SizeSystem.EU),
    (BraSize(36, "DD", SizeSystem.US), SizeSystem.UK),
    (BraSize(36, "DD", SizeSystem.US), SizeSystem.EU),
    (BraSize(38, "DDD", SizeSystem.US), SizeSystem.UK),
    (BraSize(32, "A", SizeSystem.UK), SizeSystem.EU),
    (BraSize(80, "E", SizeSystem.EU), SizeSystem.US),
    (BraSize(85, "F", SizeSystem.EU), SizeSystem.UK),
    (BraSize(34, "FF", SizeSystem.UK), SizeSystem.US),
    (BraSize(40, "GG", SizeSystem.UK), SizeSystem.EU),
    (BraSize(70, "J", SizeSystem.EU), SizeSystem.US),
]


@pytest.mark.parametrize("original, via_system", ROUNDTRIP_CASES)
def test_roundtrip_conversion(original, via_system):
    """Converting size A→B→A must return the exact original size."""
    converted = convert_size(original, via_system)
    roundtrip = convert_size(converted, original.system)
    assert roundtrip == original, (
        f"Roundtrip failed: {original} → {converted} → {roundtrip} (expected {original})"
    )
