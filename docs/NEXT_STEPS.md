# Next steps

## Immediate next steps

### 1. Freeze V1 scope

Choose one primary V1 build target:

- **Core-only bring-up:** fastest path to validate PMIC/SoC/power/sleep.
- **Biosense-first:** validate optical/biopotential path early.
- **Proximity-first:** validate BLE/RSSI/ranging experiments early.
- **Full experimental board:** most exciting, highest risk.

Recommended: core + one major risky feature, not everything at once.

### 2. Choose exact parts

Lock exact manufacturer part numbers for:

- SoC package.
- PMIC package.
- Inductors.
- Battery connector.
- USB/charging connector if used.
- Biosensor/AFE.
- Optical parts/electrodes.
- Haptic driver/load.
- ESD/protection parts.
- Optional RF/ranging path.

Each selected part should get a short note:

```text
why selected
package
supply voltage
interface
peak current
layout concerns
availability
fallback part
```

### 3. Build a real power budget

Make a table with:

- Sleep current.
- Idle current.
- BLE advertising/scanning current.
- Sensor sampling current.
- LED pulse current.
- Haptic current.
- Optional RF TX/RX current.
- Charger/PMIC quiescent current.
- Worst-case simultaneous current.

Update `scripts/generate_pdn_spice.py` with the real values.

### 4. Draw the schematic

Start with sheets:

1. Power/input/charging.
2. Main SoC.
3. Biosensor/AFE.
4. RF/ranging optional block.
5. Haptics/output.
6. Debug/test pads.
7. Connectors/mechanical.

### 5. Define board variants

Do not let optional features become ambiguity. Define population variants explicitly:

- `V1_CORE`
- `V1_BIOSENSE`
- `V1_PROXIMITY`
- `V1_FULL_EXPERIMENTAL`

### 6. Add firmware skeleton

Add only enough firmware structure to bring up hardware:

- Board definition.
- GPIO safe-state init.
- PMIC I2C read.
- BLE advertising.
- UART/RTT logging.
- Sleep/wake current test.

### 7. Build test plan before ordering PCBs

Minimum pre-order checks:

- Schematic ERC.
- PCB DRC.
- Pinout review.
- Power rail review.
- Antenna/reference layout review.
- Footprint/pin-1 review.
- BOM availability review.
- Assembly feasibility review.
- Human-contact safety review.

## V1 milestone plan

### Milestone A — repository and architecture

- [x] README scaffold.
- [x] Project brief.
- [x] Hardware architecture notes.
- [x] RF/ranging tradeoff notes.
- [x] PDN/SPICE validation script.
- [x] Limitations and safety docs.
- [ ] Exact part selection.
- [ ] Initial BOM.

### Milestone B — schematic

- [ ] Create KiCad project.
- [ ] Add symbols/footprints.
- [ ] Draw power tree.
- [ ] Draw SoC sheet.
- [ ] Draw debug/test pads.
- [ ] Draw one sensor path.
- [ ] Draw optional ranging path or connector.
- [ ] Run ERC and review warnings.

### Milestone C — PCB

- [ ] Place power and SoC blocks.
- [ ] Place antenna/RF region.
- [ ] Place biosensor region.
- [ ] Add test pads.
- [ ] Route power/ground carefully.
- [ ] Run DRC.
- [ ] Export fabrication files.
- [ ] Create assembly notes.

### Milestone D — bring-up

- [ ] Inspect bare PCBs.
- [ ] Power from bench supply.
- [ ] Verify rails.
- [ ] Verify SWD.
- [ ] Flash blink/log firmware.
- [ ] Measure sleep current.
- [ ] Bring up PMIC I2C.
- [ ] Bring up BLE.
- [ ] Bring up one optional block at a time.

### Milestone E — experiment data

- [ ] Record power logs.
- [ ] Record BLE/RSSI logs.
- [ ] Record sensor logs.
- [ ] Record haptic interference/noise logs.
- [ ] Compare expected vs measured current.
- [ ] Decide V2 fixes.

## V2 candidate improvements

- Smaller board after V1 debug lessons.
- Better antenna layout or antenna diversity.
- Dedicated sensor mechanical stack.
- Better haptic driver.
- External flash for logs.
- Improved charger safety/enclosure.
- UWB or BLE channel-sounding variant if justified by V1 data.
