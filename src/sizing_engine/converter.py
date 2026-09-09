"""
Sizing Engine — Size Converter

Converts bra sizes between different regional sizing systems (US, UK, EU).

How it works:
1. BAND conversion: Look up the band number's index in the source system,
   then find the corresponding band number at the same index in the target system.
   Example: US 34 is at index 3 → EU index 3 = 75 → band converts to 75.

2. CUP conversion: Look up the cup letter's volume index in the source system,
   then find the corresponding cup letter at the same index in the target system.
   Example: US "DD" is at volume index 4 → EU index 4 = "E" → cup converts to "E".

Key trap (where AI often gets it wrong):
- US "DD" and UK "DD" are the SAME volume (both at index 4)
- But EU calls that same volume "E" (not "DD")
- Beyond D cup, every system uses different letter sequences
"""

import json
from pathlib import Path
from .models import BraSize, SizeSystem


# ── Load size chart data ────────────────────────────────────────────────────

_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "size_charts"


def _load_json(filename: str) -> dict:
    """Load a JSON data file from the size_charts directory."""
    filepath = _DATA_DIR / filename
    with open(filepath, "r") as f:
        return json.load(f)


# Load band and cup conversion tables at module level
_BAND_TABLE: dict[str, list[int]] = _load_json("band_conversion.json")
_CUP_TABLE: dict[str, list[str]] = {
    k: v for k, v in _load_json("cup_conversion.json").items()
    if k != "_comment"
}


# ── Conversion functions ────────────────────────────────────────────────────

def convert_band(band: int, from_system: SizeSystem, to_system: SizeSystem) -> int:
    """Convert a band number from one sizing system to another.

    Uses index-based lookup: find the band's position in the source system,
    then return the band at the same position in the target system.

    Args:
        band: The band number to convert (e.g., 34 for US, 75 for EU)
        from_system: The source sizing system
        to_system: The target sizing system

    Returns:
        The equivalent band number in the target system

    Raises:
        ValueError: If the band number is not found in the source system

    Examples:
        >>> convert_band(34, SizeSystem.US, SizeSystem.EU)
        75
        >>> convert_band(80, SizeSystem.EU, SizeSystem.UK)
        36
    """
    source_bands = _BAND_TABLE[from_system.value]
    target_bands = _BAND_TABLE[to_system.value]

    if band not in source_bands:
        raise ValueError(
            f"Band {band} not found in {from_system.value} system. "
            f"Valid bands: {source_bands}"
        )

    index = source_bands.index(band)
    return target_bands[index]


def convert_cup(cup: str, from_system: SizeSystem, to_system: SizeSystem) -> str:
    """Convert a cup letter from one sizing system to another.

    Uses volume-index lookup: find the cup's volume position in the source
    system, then return the cup letter at the same position in the target system.

    This is where most conversion errors happen — cup letters diverge after "D":
    - US:  A, B, C, D, DD, DDD, G, H, I, J
    - UK:  A, B, C, D, DD, E,   F, FF, G, GG
    - EU:  A, B, C, D, E,  F,   G, H, I, J

    Args:
        cup: The cup letter(s) to convert (e.g., "DD", "DDD", "FF")
        from_system: The source sizing system
        to_system: The target sizing system

    Returns:
        The equivalent cup letter(s) in the target system

    Raises:
        ValueError: If the cup letter is not found in the source system

    Examples:
        >>> convert_cup("DD", SizeSystem.US, SizeSystem.EU)
        'E'
        >>> convert_cup("DDD", SizeSystem.US, SizeSystem.UK)
        'E'
    """
    source_cups = _CUP_TABLE[from_system.value]
    target_cups = _CUP_TABLE[to_system.value]

    if cup not in source_cups:
        raise ValueError(
            f"Cup '{cup}' not found in {from_system.value} system. "
            f"Valid cups: {source_cups}"
        )

    index = source_cups.index(cup)
    return target_cups[index]


def convert_size(size: BraSize, to_system: SizeSystem) -> BraSize:
    """Convert a complete bra size from one system to another.

    Converts both band and cup independently, then combines them into
    a new BraSize in the target system.

    Args:
        size: The source BraSize to convert
        to_system: The target sizing system

    Returns:
        A new BraSize in the target system

    Examples:
        >>> convert_size(BraSize(34, "C", SizeSystem.US), SizeSystem.EU)
        BraSize(EU 75C)
        >>> convert_size(BraSize(36, "DD", SizeSystem.US), SizeSystem.EU)
        BraSize(EU 80E)
    """
    if size.system == to_system:
        return size

    new_band = convert_band(size.band, size.system, to_system)
    new_cup = convert_cup(size.cup, size.system, to_system)

    return BraSize(band=new_band, cup=new_cup, system=to_system)
