"""
Sizing Engine — Sister Sizing

Sister sizes are alternative bra sizes that maintain the SAME CUP VOLUME
but change the band length. This is the core recommendation logic that
Brarista's AI uses when a customer's "ideal" size isn't available or
when the band fit isn't comfortable.

The Golden Rule:
- Band feels too TIGHT → go UP one band, DOWN one cup = same volume
  Example: 34C → 36B (looser band, same cup volume)

- Band feels too LOOSE → go DOWN one band, UP one cup = same volume
  Example: 34C → 32D (tighter band, same cup volume)

Why this matters for QA:
- If AI recommends wrong sister sizes, customers buy the wrong fit
- Edge cases: cup A has no sister-size-down, maximum band has no sister-size-up
- Sister sizing MUST work within the same sizing system (no cross-system)
"""

from .models import BraSize, SizeSystem

# Band sequences per system (same as converter, but needed here too)
_BANDS = {
    "US": [28, 30, 32, 34, 36, 38, 40, 42, 44],
    "UK": [28, 30, 32, 34, 36, 38, 40, 42, 44],
    "EU": [60, 65, 70, 75, 80, 85, 90, 95, 100],
    "FR": [75, 80, 85, 90, 95, 100, 105, 110, 115],
    "AU": [6, 8, 10, 12, 14, 16, 18, 20, 22],
    "JP": [60, 65, 70, 75, 80, 85, 90, 95, 100],
}

# Cup sequences per system (same as converter)
_CUPS = {
    "US":  ["A", "B", "C", "D", "DD", "DDD", "G", "H", "I", "J"],
    "UK":  ["A", "B", "C", "D", "DD", "E", "F", "FF", "G", "GG"],
    "EU":  ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"],
    "FR":  ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"],
    "AU":  ["A", "B", "C", "D", "DD", "E", "F", "FF", "G", "GG"],
    "JP":  ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"],
}


def get_sister_sizes(size: BraSize) -> dict:
    """Calculate sister sizes for a given bra size.

    Returns a dictionary with 'up' and 'down' sister sizes.
    If a sister size is impossible (e.g., cup A can't go down),
    that direction is set to None.

    Args:
        size: The base BraSize to find sisters for

    Returns:
        dict with keys:
            'up': BraSize with band+1, cup-1 (or None if impossible)
            'down': BraSize with band-1, cup+1 (or None if impossible)
            'base': The original input size

    Examples:
        >>> get_sister_sizes(BraSize(34, "C", SizeSystem.US))
        {'base': BraSize(US 34C), 'up': BraSize(US 36B), 'down': BraSize(US 32D)}

        >>> get_sister_sizes(BraSize(34, "A", SizeSystem.US))
        {'base': BraSize(US 34A), 'up': BraSize(US 36?), 'down': None}
        # Cup A has no cup below it → no sister-down
    """
    system = size.system.value
    bands = _BANDS[system]
    cups = _CUPS[system]

    # Find current positions
    if size.band not in bands:
        raise ValueError(
            f"Band {size.band} not found in {system} system. "
            f"Valid bands: {bands}"
        )
    if size.cup not in cups:
        raise ValueError(
            f"Cup '{size.cup}' not found in {system} system. "
            f"Valid cups: {cups}"
        )

    band_idx = bands.index(size.band)
    cup_idx = cups.index(size.cup)

    result = {"base": size, "up": None, "down": None}

    # Sister UP: band goes up (+1 index), cup goes down (-1 index)
    # = looser band, smaller cup letter, SAME volume
    if band_idx + 1 < len(bands) and cup_idx - 1 >= 0:
        result["up"] = BraSize(
            band=bands[band_idx + 1],
            cup=cups[cup_idx - 1],
            system=size.system,
        )

    # Sister DOWN: band goes down (-1 index), cup goes up (+1 index)
    # = tighter band, bigger cup letter, SAME volume
    if band_idx - 1 >= 0 and cup_idx + 1 < len(cups):
        result["down"] = BraSize(
            band=bands[band_idx - 1],
            cup=cups[cup_idx + 1],
            system=size.system,
        )

    return result
