# ULP Wearable Module

A small, ultra-low-power biomedical/wearable module platform for experimenting with biosensing, short-range social proximity/ranging, haptics, and modular sensor daughterboards.

The current working architecture is centered around a Nordic low-power wireless SoC plus PMIC, with optional solder-on sensing and ranging blocks so the same PCB concept can be built in different feature configurations.

> Status: early V1 architecture and repository scaffold. This is not a validated medical device design.

## Project goals

- Build a compact wearable module suitable for biomedical and social-proximity experiments.
- Keep the board modular: populate different chips/sensors depending on the prototype goal.
- Use a low-power BLE-capable MCU as the always-on controller.
- Support optical biosensing, simple haptic/alert behavior, and optional angle/direction-capable ranging.
- Make the design understandable enough to iterate quickly: clear architecture docs, power-tree notes, SPICE/SKiDL validation scripts, firmware boundaries, and explicit limitations.

## Current reference architecture

| Area | Current direction |
|---|---|
| Main SoC | Nordic nRF54L15-class low-power BLE SoC |
| PMIC | Nordic nPM1300-class PMIC for battery charging, buck rails, fuel-gauge support, ship/hibernate modes, and I2C control |
| Biosensing | MAX86176-class optical/biopotential front end under consideration for PPG/ECG-style experiments |
| Ranging | BLE RSSI baseline, BLE channel sounding / direction-finding research path, optional cheaper-than-UWB direction experiments, optional UWB footprint only if budget/size allows |
| Haptics | Small vibration/LRA/ERM or low-power alert output, still to be defined |
| Host/debug | SWD, UART/logging, test pads, power rail measurement points |
| PCB strategy | Small custom board, avoid hard-to-debug BGA where possible, use footprints that can be hand-reworked when practical |

## Repository map

```text
.
├── README.md
├── docs/
│   ├── ARCHITECTURE.md
│   ├── DEVELOPMENT.md
│   ├── FIRMWARE_AND_DATA.md
│   ├── HARDWARE.md
│   ├── LIMITATIONS.md
│   ├── NEXT_STEPS.md
│   ├── POWER_AND_PDN.md
│   ├── PROJECT_BRIEF.md
│   ├── REPOSITORY_STRUCTURE.md
│   ├── RF_RANGING_OPTIONS.md
│   └── SAFETY_AND_COMPLIANCE.md
├── scripts/
│   └── generate_pdn_spice.py
├── requirements-dev.txt
├── pyproject.toml
└── .github/
    ├── ISSUE_TEMPLATE/
    │   └── hardware-task.md
    └── pull_request_template.md
```

## Local setup

This repository currently contains documentation and early validation tooling, not finished firmware or PCB source files.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
python scripts/generate_pdn_spice.py
```

Optional external tools:

- KiCad 8 or newer for schematic/PCB work.
- ngspice for running exported SPICE netlists directly.
- nRF Connect SDK / Zephyr for eventual firmware.
- Nordic command-line/debug tooling for flashing and power profiling.
- Graphviz if you want richer generated diagrams from future scripts.

## What is already captured

- Project brief and intended module variants.
- Proposed hardware architecture around nRF54L15 + nPM1300.
- Power-tree and PDN modelling approach.
- Firmware/data partitioning proposal.
- RF/ranging topology tradeoffs.
- Known limitations and safety boundaries.
- Concrete next steps toward a V1 board.

## What is not done yet

- No KiCad schematic has been committed yet.
- No PCB layout has been committed yet.
- No firmware project has been committed yet.
- No BOM has been validated against current distributor stock/pricing.
- No electrical design has been checked against final datasheets.
- No biomedical measurement path has been validated on humans.

## Safety and intended use

This is an experimental electronics and biosensing project. It is not a medical device, not a diagnostic tool, and not suitable for unsupervised use on people until the hardware, firmware, isolation, charging, enclosure, biocompatibility, and regulatory issues are solved.

Read [`docs/SAFETY_AND_COMPLIANCE.md`](docs/SAFETY_AND_COMPLIANCE.md) before building or wearing prototypes.
