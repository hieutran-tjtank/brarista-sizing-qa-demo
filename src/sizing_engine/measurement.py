"""
Sizing Engine — Body Measurement to Size Recommendation

This is the core of how Brarista's AI Fit-Assistance works:
a customer provides body measurements, and the system recommends a bra size.

How it works:
1. UNDERBUST measurement (cm) → determines the BAND size
   - Round to nearest band in the target sizing system
   - Example: underbust 78cm → EU band 80, US band 36

2. BUST measurement (cm) → combined with underbust to determine CUP size
   - Difference = bust - underbust
   - Each 2.5cm of difference ≈ 1 cup size
   - Example: bust 92cm - underbust 78cm = 14cm difference → ~cup C/D

Measurement-to-cup mapping (approximate, industry standard):
   Diff (cm)    Cup
   10-12.5      A
   12.5-15      B
   15-17.5      C
   17.5-20      D
   20-22.5      DD/E (depends on system)
   22.5-25      DDD/E/F (depends on system)
   ...and so on

Edge cases:
- Underbust too small/large for available bands
- Bust measurement smaller than underbust (invalid)
- Measurements that fall between standard sizes
"""

from .models import BraSize, SizeSystem

# Band sequences per system
_BANDS = {
    "US": [28, 30, 32, 34, 36, 38, 40, 42, 44],
    "UK": [28, 30, 32, 34, 36, 38, 40, 42, 44],
    "EU": [60, 65, 70, 75, 80, 85, 90, 95, 100],
    "FR": [75, 80, 85, 90, 95, 100, 105, 110, 115],
    "AU": [6, 8, 10, 12, 14, 16, 18, 20, 22],
    "JP": [60, 65, 70, 75, 80, 85, 90, 95, 100],
}

# Cup sequences per system
_CUPS = {
    "US":  ["A", "B", "C", "D", "DD", "DDD", "G", "H", "I", "J"],
    "UK":  ["A", "B", "C", "D", "DD", "E", "F", "FF", "G", "GG"],
    "EU":  ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"],
    "FR":  ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"],
    "AU":  ["A", "B", "C", "D", "DD", "E", "F", "FF", "G", "GG"],
    "JP":  ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"],
}

# Underbust (cm) ranges → EU band mapping
# Each range maps to the nearest EU band size
_UNDERBUST_TO_EU_BAND = [
    (58, 62, 60),    # 58-62cm → EU 60
    (63, 67, 65),    # 63-67cm → EU 65
    (68, 72, 70),    # 68-72cm → EU 70
    (73, 77, 75),    # 73-77cm → EU 75
    (78, 82, 80),    # 78-82cm → EU 80
    (83, 87, 85),    # 83-87cm → EU 85
    (88, 92, 90),    # 88-92cm → EU 90
    (93, 97, 95),    # 93-97cm → EU 95
    (98, 102, 100),  # 98-102cm → EU 100
]

# Bust-underbust difference (cm) → cup volume index
_DIFF_TO_CUP_INDEX = [
    (10.0, 12.5, 0),   # 10-12.5cm → cup index 0 (A)
    (12.5, 15.0, 1),   # 12.5-15cm → cup index 1 (B)
    (15.0, 17.5, 2),   # 15-17.5cm → cup index 2 (C)
    (17.5, 20.0, 3),   # 17.5-20cm → cup index 3 (D)
    (20.0, 22.5, 4),   # 20-22.5cm → cup index 4 (DD/E)
    (22.5, 25.0, 5),   # 22.5-25cm → cup index 5 (DDD/E/F)
    (25.0, 27.5, 6),   # 25-27.5cm → cup index 6 (G/F)
    (27.5, 30.0, 7),   # 27.5-30cm → cup index 7 (H/FF)
    (30.0, 32.5, 8),   # 30-32.5cm → cup index 8 (I/G)
    (32.5, 35.0, 9),   # 32.5-35cm → cup index 9 (J/GG)
]


def _find_eu_band(underbust_cm: float) -> int:
    """Find the closest EU band size for a given underbust measurement."""
    for low, high, band in _UNDERBUST_TO_EU_BAND:
        if low <= underbust_cm <= high:
            return band
    raise ValueError(
        f"Underbust {underbust_cm}cm is outside supported range "
        f"({_UNDERBUST_TO_EU_BAND[0][0]}-{_UNDERBUST_TO_EU_BAND[-1][1]}cm)"
    )


def _find_cup_index(bust_cm: float, underbust_cm: float) -> int:
    """Calculate cup index from bust-underbust difference."""
    diff = bust_cm - underbust_cm

    if diff < _DIFF_TO_CUP_INDEX[0][0]:
        raise ValueError(
            f"Bust-underbust difference ({diff:.1f}cm) is too small. "
            f"Minimum is {_DIFF_TO_CUP_INDEX[0][0]}cm for cup A."
        )

    for low, high, cup_idx in _DIFF_TO_CUP_INDEX:
        if low <= diff < high:
            return cup_idx

    # If diff exceeds the largest range, return max cup
    if diff >= _DIFF_TO_CUP_INDEX[-1][0]:
        return _DIFF_TO_CUP_INDEX[-1][2]

    raise ValueError(f"Could not determine cup for difference {diff:.1f}cm")


def _eu_band_to_target(eu_band: int, target_system: SizeSystem) -> int:
    """Convert an EU band to the target sizing system."""
    eu_bands = _BANDS["EU"]
    target_bands = _BANDS[target_system.value]

    if eu_band not in eu_bands:
        raise ValueError(f"EU band {eu_band} not in known bands")

    idx = eu_bands.index(eu_band)
    return target_bands[idx]


def recommend_size(
    underbust_cm: float,
    bust_cm: float,
    target_system: SizeSystem = SizeSystem.EU,
) -> BraSize:
    """Recommend a bra size based on body measurements.

    This is the core function that Brarista's AI uses: take body measurements
    and output a size recommendation in any sizing system.

    Args:
        underbust_cm: Underbust measurement in centimeters
        bust_cm: Bust measurement in centimeters
        target_system: Which sizing system to recommend in (default: EU)

    Returns:
        A BraSize recommendation in the target system

    Raises:
        ValueError: If measurements are out of range or invalid

    Examples:
        >>> recommend_size(78, 92, SizeSystem.EU)
        BraSize(EU 80C)
        >>> recommend_size(78, 92, SizeSystem.US)
        BraSize(US 36C)
    """
    # Validate inputs
    if bust_cm <= underbust_cm:
        raise ValueError(
            f"Bust ({bust_cm}cm) must be larger than underbust ({underbust_cm}cm)"
        )

    # Step 1: Underbust → EU band
    eu_band = _find_eu_band(underbust_cm)

    # Step 2: Convert EU band to target system
    target_band = _eu_band_to_target(eu_band, target_system)

    # Step 3: Bust-underbust difference → cup index
    cup_index = _find_cup_index(bust_cm, underbust_cm)

    # Step 4: Cup index → cup letter in target system
    cups = _CUPS[target_system.value]
    cup_letter = cups[cup_index]

    return BraSize(band=target_band, cup=cup_letter, system=target_system)
