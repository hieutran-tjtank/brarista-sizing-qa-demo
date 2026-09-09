"""
Sizing Engine — Data Models

Defines the core data structures for bra sizing:
- SizeSystem: Which regional sizing standard (US, UK, EU)
- BraSize: A specific bra size in a specific system

Why these 3 systems first?
- US & UK share the same band numbers (inches) but diverge on cup letters after D
- EU uses centimeters for bands and a simpler cup sequence
- This US/UK/EU triangle captures the most common conversion errors
"""

from enum import Enum
from dataclasses import dataclass


class SizeSystem(Enum):
    """Regional bra sizing standards.

    Phase 1: US, UK, EU (core 3)
    Phase 3: Added FR, AU, JP (expanded to 6 systems)

    Key relationships:
    - FR bands = EU bands + 15cm (e.g., EU 75 = FR 90)
    - AU uses its own numbering (6, 8, 10...) but UK cup letters
    - JP bands = EU bands (same cm), JP cups = EU cups
    """
    US = "US"
    UK = "UK"
    EU = "EU"
    FR = "FR"
    AU = "AU"
    JP = "JP"


@dataclass(frozen=True)
class BraSize:
    """Represents a specific bra size in a specific sizing system.

    Attributes:
        band: The band number (e.g., 34 for US/UK, 75 for EU)
        cup: The cup letter(s) (e.g., "B", "DD", "DDD")
        system: Which sizing system this size belongs to

    Examples:
        US 34C  → BraSize(band=34, cup="C", system=SizeSystem.US)
        EU 75B  → BraSize(band=75, cup="B", system=SizeSystem.EU)
        UK 36DD → BraSize(band=36, cup="DD", system=SizeSystem.UK)
    """
    band: int
    cup: str
    system: SizeSystem

    def __str__(self) -> str:
        return f"{self.system.value} {self.band}{self.cup}"

    def __repr__(self) -> str:
        return f"BraSize({self.system.value} {self.band}{self.cup})"
