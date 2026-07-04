# Limitations

This file is intentionally blunt. It is better to name the weak points now than to hide them until hardware is already ordered.

## Technical limitations

### The design is not finalized

The repository currently contains an architecture scaffold and early validation tooling. It does not yet contain a finalized schematic, PCB, BOM, or firmware tree.

### Component choices are provisional

The nRF54L15/nPM1300/MAX86176-class architecture is the current direction, not a locked design. Final choices still depend on:

- Package availability.
- Distributor stock and price.
- Reference designs.
- Layout difficulty.
- Power numbers.
- Firmware support.
- Assembly/rework feasibility.

### SPICE model is simplified

The current PDN script models regulator rails as Thévenin sources with output capacitance and current sinks. It does not model:

- Real buck control loops.
- Inductor saturation.
- ESR/ESL of every capacitor.
- PCB plane impedance.
- RF burst spectral effects.
- AFE internal current profiles.
- Battery chemistry accurately.

Use it to catch bad architecture, not to sign off hardware.

### BLE RSSI is not real direction finding

BLE RSSI can support proximity experiments, but two tiny wearable tags cannot magically infer reliable bearing from basic RSSI alone. Direction requires additional information: antenna diversity, phase/angle support, movement, IMU context, anchors, or a different ranging technology.

### UWB is not free

UWB can solve a lot of ranging problems, but it adds cost, layout complexity, power budget pressure, and package/assembly difficulty. It should be optional unless the project goal shifts toward accurate ranging above all else.

### Wearable biosensing is mechanically hard

Good PPG/ECG-style data depends on:

- Skin contact.
- Pressure.
- Motion artifacts.
- Ambient light control.
- Electrode/optical geometry.
- Analog front-end layout.
- Filtering and calibration.

A good IC alone does not make a good biosensor.

## Safety limitations

### Not a medical device

This project is not certified or validated for diagnosis, monitoring, treatment, or safety-critical health decisions.

### Human contact requires extra care

Any circuit touching the body needs careful handling of:

- Leakage current.
- Charger isolation.
- ESD.
- Fault states.
- Skin irritation/biocompatibility.
- Enclosure design.
- Moisture/sweat ingress.

### Battery risk

Small Li-ion/LiPo systems can still fail dangerously. Charging, enclosure, strain relief, and thermal behavior must be tested.

### RF/regulatory risk

Any transmitting wearable may require regulatory testing/certification before real-world distribution. Prototype experiments are not the same as a sellable device.

## Project-management limitations

- The repo is early and documentation-heavy by design.
- Requirements may change after real part selection.
- BOM cost is not yet locked.
- Board size is not yet locked.
- Power budget is not yet measured.
- Feature creep is a serious risk.

## Most dangerous assumptions

1. Assuming BLE RSSI can provide clean direction between two tiny tags.
2. Assuming optical biosensing works without mechanical/optical enclosure design.
3. Assuming the PMIC rails can absorb all pulse loads because average current looks fine.
4. Assuming the first PCB should be tiny instead of debuggable.
5. Assuming a human-worn charging/data-connected prototype is automatically safe.

## What to do about these limitations

- Build a core-only bring-up board if needed.
- Add measurement pads and current shunts.
- Validate power rails with dummy pulse loads before expensive sensors.
- Test RF/ranging algorithms with dev boards before locking PCB antenna geometry.
- Treat sensor logs as experimental data, not health output.
- Keep V1 ugly enough to debug.
