# System architecture

## High-level block diagram

```text
                  ┌────────────────────────────┐
                  │      Li-ion / LiPo cell     │
                  └──────────────┬─────────────┘
                                 │
                                 ▼
                  ┌────────────────────────────┐
                  │ nPM1300-class PMIC          │
                  │ charger, bucks, ship mode,  │
                  │ fuel-gauge support, I2C     │
                  └───────┬───────────┬────────┘
                          │           │
          ┌───────────────▼───┐   ┌───▼──────────────────┐
          │ 1.8 V / MCU rail   │   │ 3.3 V sensor rail     │
          └──────────┬────────┘   └───────────┬──────────┘
                     │                        │
                     ▼                        ▼
          ┌────────────────────┐   ┌──────────────────────┐
          │ nRF54L15-class SoC  │   │ Biosensor / AFE area  │
          │ BLE, control, logs  │   │ optical/ECG/PPG/etc.  │
          └─────┬─────┬─────┬──┘   └───────────┬──────────┘
                │     │     │                  │
        SWD/UART│     │I2C/SPI/GPIO            │analog/mech/layout
                │     │     │                  │
                ▼     ▼     ▼                  ▼
          Debug pads  Haptic  Optional RF/ranging daughter/footprint
```

## Core modules

### 1. Power core

The power core should provide:

- Battery charging.
- Regulated MCU rail.
- Regulated sensor rail.
- Load switching for optional high-current blocks.
- Ship/hibernate mode.
- Fuel-gauge or battery-state support.
- Measurement points for current and voltage during development.

The current reference direction is an nPM1300-class PMIC. The exact rail allocation still needs final datasheet/BOM review.

### 2. Main SoC

The main SoC is responsible for:

- Boot, sleep, wake, and power-state control.
- BLE advertising/connection.
- Sensor scheduling.
- Data buffering.
- Basic filtering/compression.
- Haptic/alert control.
- Factory test mode.
- Debug logs.

The current reference direction is an nRF54L15-class Nordic SoC, because it fits the low-power BLE/wearable control role and has a strong Zephyr/Nordic ecosystem.

### 3. Biosensing area

The biosensing area is intentionally not treated as “just another I2C chip.” It needs:

- Clean power.
- Good return paths.
- Mechanical stability.
- Optical isolation from ambient light where relevant.
- Electrode/skin-contact safety if any biopotential path is populated.
- Clear separation between experimental logging and any medical claims.

MAX86176-class parts are under consideration for a combined optical/biopotential sensing path, but final device selection must be confirmed against package, availability, layout difficulty, power, and cost.

### 4. Ranging/proximity area

The project should support more than one topology over time:

- BLE RSSI baseline for cheap proximity.
- BLE direction finding / antenna switching where feasible.
- BLE channel sounding research path for future-compatible ranging.
- Custom analog/RSSI ideas for tag-to-tag bearing experiments.
- Optional UWB only if the cost, size, and assembly penalty are justified.

UWB should not be treated as the only direction-capable answer. It is technically strong but may be too expensive for the small/cheap tag concept.

### 5. Debug/test infrastructure

Early prototypes should include:

- SWD pads.
- UART/log pads.
- I2C/SPI breakout pads where space allows.
- Battery and rail measurement pads.
- Current-measurement jumpers or shunts.
- Boot/reset access.
- Clear silkscreen for prototype variants.

## Suggested board variants

| Variant | Purpose | Populate |
|---|---|---|
| Core-only | Bring-up and power validation | SoC, PMIC, debug, LEDs/test loads |
| Biosense | Biomedical sensing experiments | Core + AFE + optical/mechanical sensor stack |
| Proximity | Party/friend-finder experiments | Core + BLE/RSSI/direction/ranging path |
| Full experimental | Integration stress test | Core + biosensing + haptics + optional RF |

## Architecture rules for V1

- Do not place every high-current pulse load on one PMIC buck without budgeting simultaneous peaks.
- Do not rely on firmware to fix bad analog layout.
- Do not remove debug access to save a few square millimeters on V1.
- Do not make a human-worn prototype charge from USB while attached to skin-contact electrodes unless the safety architecture is explicitly designed for it.
- Do not make medical claims from raw experimental signals.
