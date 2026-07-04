# Hardware plan

## Current baseline

This repository is tracking an early wearable board architecture, not a finished schematic. The working baseline is:

- **Main SoC:** Nordic nRF54L15-class low-power BLE SoC.
- **PMIC:** Nordic nPM1300-class PMIC.
- **Biosensing:** MAX86176-class optical/biopotential front end under consideration.
- **Ranging:** BLE-first, with optional footprints/experiments for direction/ranging.
- **Haptics:** small vibration or tactile alert output, not finalized.
- **Battery:** single-cell Li-ion/LiPo.
- **Debug:** SWD, UART, rail test pads, reset/boot access.

## Package and assembly preferences

Early prototypes should prefer packages that can be inspected and reworked:

- Prefer QFN/WLCSP only when the layout and assembly path are realistic.
- Avoid BGA unless the benefit is overwhelming.
- Keep test pads around all hard-to-debug interfaces.
- Add probeable current/voltage points even if the final product would remove them.
- Leave room for bodge wires on V1.

This is not production optimization. V1 should be built to learn fast.

## Suggested hardware blocks

### Power and battery

Required:

- Battery connector or solder pads.
- Reverse/ESD protection appropriate to connector choice.
- Charger input protection.
- PMIC with charge status and power-fail awareness.
- Buck rails for MCU/sensors.
- Load switch or separate regulator for optional pulse-heavy RF blocks.
- Ship/hibernate mode access.

Recommended debug features:

- Rail test points.
- PMIC interrupt test point.
- I2C test pads.
- Current-measurement jumper for whole-board current.
- Optional shunts or 0-ohm links for per-block current measurement.

### Main SoC

Required:

- Stable main rail.
- Required crystals/clocks according to final datasheet/reference design.
- RF matching network and antenna keepout.
- SWD.
- Reset and boot access.
- GPIO allocation table.

Notes:

- Do not finalize antenna layout from intuition. Use the reference layout and leave tuning options.
- Avoid routing noisy LED/haptic currents through the RF/analog return path.

### Biosensing

Possible populated paths:

- PPG LED + photodiode/AFE path.
- ECG/biopotential electrode path if the selected AFE and safety design support it.
- Temperature sensor.
- IMU/activity sensor.
- Skin contact / wear-state detection.

Hardware concerns:

- Optical path geometry matters as much as the IC.
- Ambient light shielding matters.
- Electrode input protection and leakage matter.
- Human-contact safety must be treated as a first-class design constraint.
- The board should be electrically safe even when firmware crashes.

### Haptics / alert output

Options:

- ERM motor.
- LRA driver.
- Piezo buzzer.
- LED indicator.
- Small tactile solenoid only if power budget allows.

V1 should start simple. Haptic load must be isolated from sensitive analog/radio rails.

### Ranging/proximity

Options are documented in [`RF_RANGING_OPTIONS.md`](RF_RANGING_OPTIONS.md). Hardware should keep these possibilities open:

- BLE-only baseline.
- Antenna diversity / switched antenna experiments.
- Optional RF frontend/daughterboard connector.
- Optional UWB footprint only if the cost and package are acceptable.

## Early pin-planning table

| Function | Direction | Notes |
|---|---|---|
| SWDIO/SWCLK | debug | Never omit on V1 |
| PMIC I2C | bidirectional | Shared with low-speed sensors if acceptable |
| PMIC INT | input | Wake/event line |
| Biosensor I2C/SPI | bidirectional | Final bus depends on selected part |
| Biosensor INT | input | Timestamped wake/data-ready line |
| Haptic enable/PWM | output | Keep away from analog routing |
| RF/ranging IRQ | input | Optional population |
| RF/ranging SPI/UART | bidirectional | Depends on topology |
| Battery measure/fuel gauge | bidirectional/input | PMIC-integrated if possible |

## Minimum V1 bring-up checklist

- Verify no shorts before inserting battery.
- Power from current-limited supply first.
- Confirm PMIC rails with no SoC populated if possible.
- Confirm reset behavior.
- Confirm SWD attach.
- Blink/log from SoC.
- Confirm PMIC I2C.
- Measure sleep current with optional blocks unpopulated.
- Populate one sensor block at a time.
- Measure sensor active current.
- Measure RF active current.
- Test charging thermals and termination behavior.

## Files still missing

These should be added once the electrical choices settle:

- KiCad project.
- Schematic PDF exports.
- PCB layout.
- Symbol/footprint libraries or library references.
- BOM with distributor links.
- Assembly notes.
- Test fixture notes.
- Measured power logs.
