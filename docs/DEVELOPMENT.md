# Development setup

## Current repo state

The repository is currently a documentation and early validation scaffold. It is ready to receive:

- KiCad hardware files.
- BOM files.
- Firmware source.
- Test scripts.
- Measurement logs.

## Python environment

Use Python 3.11 or newer if practical.

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements-dev.txt
```

Run the current validation script:

```bash
python scripts/generate_pdn_spice.py
```

Generated outputs go into:

```text
build/pdn/
```

## Hardware CAD tools

Recommended:

- KiCad 8 or newer.
- KiCad official libraries plus any committed project libraries.
- FreeCAD or a mechanical CAD tool for enclosure/fit checks.
- Graphviz for generated diagrams if future scripts use it.
- ngspice for direct SPICE simulation of exported netlists.

## Firmware tools

Expected future setup:

- Nordic nRF Connect SDK.
- Zephyr/west.
- CMake/Ninja.
- ARM embedded toolchain from the Nordic/Zephyr setup.
- J-Link or compatible SWD probe.
- Nordic command-line tools or nRF Connect Programmer.

No firmware tree exists yet, so the exact setup will be documented when the first firmware commit is added.

## Suggested workflow

1. Create a branch for every meaningful change.
2. Keep hardware, firmware, and docs changes separated when possible.
3. Commit generated PDFs/images only when they help review.
4. Do not commit large raw measurement dumps unless they are curated.
5. Link measurements to board revision, firmware commit, and test setup.

## Naming conventions

Suggested board revisions:

```text
ULP-WM-V1A
ULP-WM-V1B
ULP-WM-V2A
```

Suggested population variants:

```text
CORE
BIOSENSE
PROXIMITY
FULL_EXPERIMENTAL
```

Suggested log/test IDs:

```text
YYYYMMDD_boardrev_variant_testname
```

Example:

```text
20260704_ULP-WM-V1A_CORE_sleep-current
```

## Generated files

Generated build files should not normally be committed:

- `build/`
- `.venv/`
- Python caches
- KiCad backups
- simulator raw output

See `.gitignore`.

## Pre-PR checklist

Before opening a PR:

- Update docs if architecture changed.
- Run relevant scripts.
- Include generated plots/reports only if useful for review.
- Mention assumptions.
- Mention what was not tested.
- For hardware changes, include screenshots or PDFs if possible.

## Pre-PCB-order checklist

Before ordering hardware:

- ERC clean or every warning explained.
- DRC clean or every warning explained.
- Footprint review complete.
- Pin 1/orientation review complete.
- Power budget updated.
- BOM availability checked.
- Assembly process realistic.
- Antenna/reference layout reviewed.
- Human-contact and battery risks reviewed.
