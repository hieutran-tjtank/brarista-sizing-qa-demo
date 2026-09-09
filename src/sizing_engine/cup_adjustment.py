"""
Sizing Engine — Cup Adjustment

Cup adjustment finds alternative sizes when the BAND fits well but the
CUP doesn't. Unlike sister sizing (which changes both band and cup to
keep the same volume), cup adjustment keeps the band and changes only
the cup volume.

Real-world scenario:
- Customer wears 34C, band fits perfectly
- But cup feels too tight → recommend 34D (one cup up)
- Or cup feels too loose → recommend 34B (one cup down)

Why this was missing (QA Catch #2):
- Claude Code implemented sister sizing but forgot cup adjustment
- QA engineer caught this gap from domain knowledge:
  "What about when band is fine but cup doesn't fit?"
- This is a separate and equally common recommendation in bra fitting

Edge cases:
- Cup A → no cup-down (smallest cup)
- Cup J/GG (max cup) → no cup-up
- Cup adjustment stays within the SAME sizing system
"""

from .models import BraSize, SizeSystem

# Cup sequences per system
_CUPS = {
    "US":  ["A", "B", "C", "D", "DD", "DDD", "G", "H", "I", "J"],
    "UK":  ["A", "B", "C", "D", "DD", "E", "F", "FF", "G", "GG"],
    "EU":  ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"],
    "FR":  ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"],
    "AU":  ["A", "B", "C", "D", "DD", "E", "F", "FF", "G", "GG"],
    "JP":  ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"],
}


def get_cup_adjustment(size: BraSize) -> dict:
    """Find adjacent cup sizes while keeping the band unchanged.

    Returns a dictionary with cup-up and cup-down options.
    If an adjustment is impossible (e.g., already at smallest/largest cup),
    that direction is set to None.

    Args:
        size: The base BraSize to adjust

    Returns:
        dict with keys:
            'base': The original input size
            'cup_up': BraSize with next larger cup (or None)
            'cup_down': BraSize with next smaller cup (or None)

    Examples:
        >>> get_cup_adjustment(BraSize(34, "C", SizeSystem.US))
        {'base': BraSize(US 34C), 'cup_up': BraSize(US 34D), 'cup_down': BraSize(US 34B)}

        >>> get_cup_adjustment(BraSize(34, "A", SizeSystem.US))
        {'base': BraSize(US 34A), 'cup_up': BraSize(US 34B), 'cup_down': None}
    """
    system = size.system.value
    cups = _CUPS[system]

    if size.cup not in cups:
        raise ValueError(
            f"Cup '{size.cup}' not found in {system} system. "
            f"Valid cups: {cups}"
        )

    cup_idx = cups.index(size.cup)

    result = {"base": size, "cup_up": None, "cup_down": None}

    # Cup UP: next larger cup (more volume, same band)
    if cup_idx + 1 < len(cups):
        result["cup_up"] = BraSize(
            band=size.band,
            cup=cups[cup_idx + 1],
            system=size.system,
        )

    # Cup DOWN: next smaller cup (less volume, same band)
    if cup_idx - 1 >= 0:
        result["cup_down"] = BraSize(
            band=size.band,
            cup=cups[cup_idx - 1],
            system=size.system,
        )

    return result
