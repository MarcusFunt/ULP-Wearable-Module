# Repository structure

This is the intended structure as the project grows.

```text
.
├── README.md
├── docs/
│   ├── PROJECT_BRIEF.md
│   ├── ARCHITECTURE.md
│   ├── HARDWARE.md
│   ├── POWER_AND_PDN.md
│   ├── RF_RANGING_OPTIONS.md
│   ├── FIRMWARE_AND_DATA.md
│   ├── SAFETY_AND_COMPLIANCE.md
│   ├── LIMITATIONS.md
│   ├── NEXT_STEPS.md
│   └── DEVELOPMENT.md
├── hardware/
│   ├── kicad/
│   ├── bom/
│   ├── fabrication/
│   └── assembly/
├── firmware/
│   ├── app/
│   ├── drivers/
│   ├── include/
│   ├── boards/
│   └── tests/
├── scripts/
│   └── generate_pdn_spice.py
├── measurements/
│   ├── power/
│   ├── rf/
│   └── biosensing/
└── mechanical/
    ├── enclosure/
    └── fixtures/
```

## `docs/`

Project planning, architecture, limitations, and review notes. Docs should stay close to the real design; if hardware changes, update the docs.

## `hardware/`

Future location for KiCad and manufacturing files.

Suggested subdirectories:

```text
hardware/kicad/ULP-WM/
hardware/bom/
hardware/fabrication/rev_v1a/
hardware/assembly/rev_v1a/
```

## `firmware/`

Future location for Zephyr/Nordic firmware.

Do not add a giant firmware scaffold before the hardware pinout exists. Start small and bring up rails/debug/BLE first.

## `scripts/`

Small reproducible engineering scripts. Scripts should:

- Run from repo root.
- Write generated outputs to `build/`.
- Avoid hardcoded absolute paths.
- Print a useful summary.
- Be safe to rerun.

## `measurements/`

Curated measurement outputs only. Do not dump every raw file forever.

Every measurement should state:

- Board revision.
- Population variant.
- Firmware commit.
- Test setup.
- Instrumentation.
- Environment.
- Known caveats.

## `mechanical/`

Enclosure, optical stack, test fixtures, battery holders, and wearable mounts. Mechanical design is especially important for biosensing and battery safety.
