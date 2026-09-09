"""Shared test fixtures and configuration."""

import sys
from pathlib import Path

# Add src/ to Python path so tests can import from src.sizing_engine
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
