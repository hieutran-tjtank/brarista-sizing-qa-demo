# Brarista Sizing QA Demo

A QA testing demonstration project that simulates a bra sizing engine — similar to what [Brarista](https://www.brarista.fit) uses for AI Fit-Assistance — and tests it exhaustively using Pytest.

## Why This Project Exists

I built this to demonstrate my QA workflow with AI-assisted coding tools. The key insight: **AI can generate code fast, but only a QA engineer knows what questions to ask.**

This project shows:
- ✅ **What AI did:** Generated all source code, test scaffolding, and data tables
- ✅ **What I did:** Verified data against real brand charts, caught 4 AI errors, identified missing features
- ✅ **AI errors I caught:** Documented in detail — [see AI Catches Log](docs/ai_catches_log.md)

## Architecture

```
src/sizing_engine/
├── models.py          # BraSize, SizeSystem (US/UK/EU/FR/AU/JP)
├── converter.py       # Size conversion across 6 systems
├── sister_sizing.py   # Same volume, different band fit
├── cup_adjustment.py  # Same band, different cup (QA-initiated feature)
└── measurement.py     # Body measurements → size recommendation

data/size_charts/
├── band_conversion.json   # Band mapping across 6 systems
└── cup_conversion.json    # Cup letter mapping (divergence after D)

tests/                     # 99 automated tests
├── test_basic_conversion.py      # 10 — Core US/UK/EU conversion
├── test_edge_cases.py            # 15 — Invalid & malformed inputs
├── test_sister_sizing.py         # 10 — Alternative size recommendations
├── test_cup_adjustment.py        # 10 — Cup-only adjustments (QA catch)
├── test_conversion_matrix.py     # 30 — Parametrized exhaustive matrix
├── test_new_systems.py           # 14 — FR/AU/JP + cross-system roundtrips
└── test_measurement.py           # 10 — Body measurement → size
```

## Test Design & QA Methodology

### Testing Techniques Used

| Technique | What It Proves | Example |
|-----------|---------------|---------|
| **Roundtrip (A→B→A)** | Conversion is lossless — no data lost in translation | US 36DD → EU 80E → US 36DD ✅ |
| **Boundary Value** | System handles limits gracefully, no crashes | Band 54 (above max 44) → clear `ValueError` |
| **Equivalence Partitioning** | Representative inputs from each class are tested | Cup A–D (simple zone) vs DD+ (divergence zone) |
| **Negative Testing** | Invalid inputs rejected with clear errors | Empty cup `""`, lowercase `"b"`, numeric `"123"` |
| **Cross-system Matrix** | Every system pair produces correct results | 30 parametrized band × cup × system combinations |

### Edge Case Coverage

These tests reflect real-world scenarios a QA engineer should anticipate:

- **Out-of-range sizes:** Band 54 (plus-size), Band 26 (below minimum)
- **Empty values:** Blank cup field from a web form
- **Case sensitivity:** Lowercase `"b"` vs uppercase `"B"`
- **Garbage input:** Numeric `"123"`, special characters `"D+"`
- **Whitespace:** Copy-paste artifact `" B "` with spaces
- **Impossible values:** Negative band, zero band, bust < underbust
- **Cross-system traps:** UK cup `"FF"` submitted as US input

## AI Catches — What Went Wrong

During development, I caught **4 errors** in AI-generated code:

| # | What AI Got Wrong | How I Caught It | Severity |
|---|---|---|---|
| 1 | Band data only covers 28–44, crashes on plus-sizes | Tested edge case: `UK 54E → EU` | 🟡 Medium |
| 2 | Missing cup adjustment feature entirely | Domain knowledge: "What if cup doesn't fit but band is fine?" | 🔴 High |
| 3 | AI skipped Phase 3 (Scale), jumped to Polish | Checked against agreed implementation plan | 🟡 Medium |
| 4 | Wrote wrong expected value: `EU 60B` instead of `EU 60A` | Ran tests — assertion failed, verified manually | 🟡 Medium |

→ Full narrative with context: [docs/ai_catches_log.md](docs/ai_catches_log.md)

## Quick Start

```bash
# Clone and install
git clone https://github.com/hieutran-tjtank/brarista-sizing-qa-demo.git
cd brarista-sizing-qa-demo
pip3 install -r requirements.txt

# Run all 99 tests
python3 -m pytest tests/ -v

# Run specific test group
python3 -m pytest tests/test_edge_cases.py -v    # Edge cases & malformed input
python3 -m pytest tests/test_sister_sizing.py -v  # Sister sizing logic
```

**Expected output:** `99 passed in 0.05s`

## Development Process

This project was built in 4 phases, documented step-by-step in [BUILD_LOG.md](docs/BUILD_LOG.md):

1. **Foundation** — 3 systems (US/UK/EU), 10 test cases, data verification
2. **Expand & Harden** — Edge cases, sister sizing, cup adjustment (QA-initiated)
3. **Scale** — Added FR/AU/JP, body measurements, roundtrip tests
4. **Polish & Ship** — README, AI catches narrative, input hardening tests

## Tools & Stack

- **Language:** Python 3.9+
- **Test Framework:** Pytest 8.x with parametrize
- **AI Tool:** Claude Code (Anthropic) — used for code generation
- **QA Approach:** Manual review + automated regression testing

## About the Author

**Hieu Tran** — Manual QC transitioning to QA Engineering. 2 years of domain experience in lingerie sizing (Bình Tây wholesale market). This project demonstrates combining domain knowledge with AI-assisted testing workflows.

---

*Inspired by [Brarista](https://www.brarista.fit) — AI Fit-Assistance for bra sizing.*
