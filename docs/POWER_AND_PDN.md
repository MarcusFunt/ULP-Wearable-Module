# Power and PDN plan

## Purpose

This document captures the current power-tree assumptions and the early SPICE/SKiDL validation approach.

The model is deliberately simplified. It is useful for catching architecture mistakes and current-budget problems. It is not a substitute for final datasheet simulations, PCB extraction, oscilloscope measurements, or regulator stability validation.

## Current rail concept

| Rail | Intended load | Source | Notes |
|---|---|---|---|
| VBAT | PMIC input | Li-ion/LiPo cell | Include ESR and input capacitance in models |
| 1.8 V | main SoC / digital low-power rail | PMIC buck | Exact voltage depends on final SoC/reference design |
| 3.3 V AFE | biosensor, optical LED/AFE support | PMIC buck or regulated load switch | Do not mix with unrelated RF pulse loads blindly |
| 3.3 V optional RF/UWB | optional high-current ranging block | separate regulator/load switch if needed | Keep separately budgeted from biosensor LED pulses |

## Early current-budget rule

Do not size rails from average current alone.

For each rail, track:

```text
base current
+ radio burst current
+ LED pulse current
+ haptic current
+ sensor conversion current
+ startup/inrush current
+ margin
```

A rail is suspicious if simultaneous plausible peaks exceed about 70–80% of its rated output during early design. V1 should be conservative because layout parasitics and firmware mistakes are expected.

## Important iteration already captured

A previous first-pass model effectively clamped rails with ideal voltage sources in a way that made source resistance meaningless. The corrected model treats each regulator output as a Thévenin source:

```text
ideal voltage source -> source impedance -> output rail -> decoupling + loads
```

That model is still simple, but it exposes droop from load steps and makes rail separation visible.

## SPICE/SKiDL validation script

Run:

```bash
python scripts/generate_pdn_spice.py
```

Outputs:

```text
build/pdn/wearable_pdn_final.cir
build/pdn/wearable_pdn_summary.md
build/pdn/wearable_pdn_transient.png
```

The script:

- Builds a SKiDL circuit using SPICE primitives.
- Runs SKiDL ERC.
- Exports an ngspice-style netlist.
- Runs a simple Python transient equivalent for rail droop.
- Writes a summary report.

## Current example assumptions in the script

| Rail | Nominal | Source impedance | Current limit | Example peak load |
|---|---:|---:|---:|---:|
| VDD_1V8 | 1.8 V | 0.08 ohm | 200 mA | 35 mA |
| VDD_3V3_AFE | 3.3 V | 0.12 ohm | 200 mA | 98 mA |
| VDD_3V3_UWB_OPT | 3.3 V | 0.08 ohm | 300 mA | 175 mA |

These numbers are placeholders for architecture checking. Replace them with datasheet-based and measured values as soon as the components are finalized.

## Layout rules

- Put local decoupling close to each IC power pin group.
- Keep LED/haptic pulse currents away from analog and RF returns.
- Use a sane ground strategy; do not create fragile skinny shared returns.
- Add test points for every rail.
- Add current-measurement options for optional blocks.
- Keep PMIC thermal behavior in mind, even if the average current looks low.
- Avoid charging while connected to any unsafe human-contact electrode path unless the isolation/safety design is explicitly solved.

## What still needs real validation

- PMIC regulator stability with selected output capacitors.
- Inductor selection and saturation current.
- Battery ESR and cold/low-voltage behavior.
- Charger thermal behavior in enclosure.
- Inrush and startup sequencing.
- LED pulse effect on analog measurements.
- RF TX burst effect on rails and sensor data.
- Sleep current with all optional blocks disabled.
- Real oscilloscope measurements on V1 hardware.
