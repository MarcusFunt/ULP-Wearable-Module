# Firmware and data plan

## Firmware status

No firmware project is committed yet. This document defines the intended boundaries so the first firmware tree does not become a random prototype sketch.

## Intended firmware stack

Likely direction:

- **RTOS/SDK:** Zephyr via Nordic nRF Connect SDK.
- **Language:** C for low-level drivers/configuration, optional C++ only if the project structure stays clean.
- **Build:** west/CMake once firmware is added.
- **Logging:** RTT/UART during bring-up, compact binary event logs later.
- **Transport:** BLE first, UART/SWD for development.

## Firmware responsibilities

### Boot and power

- Initialize clocks, GPIO states, PMIC control, and boot reason.
- Keep high-current optional blocks disabled until explicitly needed.
- Support sleep, wake, hibernate/ship mode, and safe brownout behavior.
- Log reset causes and PMIC faults.

### Sensor scheduling

- Keep sensors off unless needed.
- Use data-ready interrupts where possible.
- Timestamp sensor events close to the interrupt edge.
- Keep biosensor sampling policies explicit and versioned.

### Radio/proximity

- Start with BLE advertisement/scan experiments.
- Keep RSSI/channel/raw observations in logs; do not only emit smoothed distance guesses.
- Treat direction/ranging algorithms as experimental until measured.

### Haptics/alerts

- Enforce maximum duty cycle.
- Avoid haptic activity during sensitive biosensor sampling windows unless testing interaction/noise.
- Make alerts fail-safe: firmware crash should not leave a motor driven indefinitely.

### Data logging

Recommended initial log format:

```text
magic/version
boot_id
device_id or test_id
timestamp_ticks
event_type
payload_length
payload_crc
payload
```

Keep logs machine-readable from day one. Even crude logs are better than screenshots and vibes.

## Suggested firmware modules

```text
firmware/
├── app/
│   ├── main.c
│   ├── board_state.c
│   └── app_config.c
├── drivers/
│   ├── pmic_npm1300.c
│   ├── biosensor.c
│   ├── haptics.c
│   └── ranging.c
├── include/
│   ├── app_config.h
│   ├── event_log.h
│   └── board_pins.h
├── protocols/
│   ├── event_log_format.md
│   └── ble_gatt.md
└── tests/
```

## Data products

The project should eventually produce:

- Raw sensor logs.
- Power-state logs.
- BLE/RSSI/ranging logs.
- Calibration metadata.
- Board revision and population variant metadata.
- Test notes linked to exact hardware/firmware revisions.

## Data integrity rules

- Every log should include firmware version and board revision.
- Every measurement should include sensor configuration.
- Every derived signal should be reproducible from raw-ish data.
- Do not overwrite raw data with filtered data.
- Keep medical interpretation out of firmware. Firmware can measure; it should not diagnose.

## Firmware bring-up sequence

1. Boot with all optional loads disabled.
2. Confirm GPIO safe states.
3. Confirm PMIC I2C and rail telemetry.
4. Add basic log output.
5. Add BLE identity/advertising.
6. Add sleep/wake loop and current measurements.
7. Add one sensor block.
8. Add haptics.
9. Add RF/ranging experiments.
10. Add compact log storage/streaming.

## Open firmware questions

- Exact nRF54L15 package and board definition.
- Exact PMIC rail allocation.
- Whether biosensor bus is I2C or SPI.
- How much nonvolatile storage is needed.
- Whether logs stream live, store locally, or both.
- Whether there is a phone app, laptop script, or BLE gateway.
