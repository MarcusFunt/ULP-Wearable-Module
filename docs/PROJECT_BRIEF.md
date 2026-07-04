# Project brief

## One-line description

ULP Wearable Module is a small experimental biomedical/wearable electronics platform built around a low-power wireless SoC, battery PMIC, modular biosensors, and optional short-range social-proximity/ranging features.

## Why this exists

The project is meant to become a compact board that can support several related wearable experiments without redesigning the whole PCB every time. The central idea is to keep a stable low-power compute/power core and expose optional population areas for sensors and radios.

Example prototype modes:

- Basic wearable beacon/logger.
- Optical biosensing module.
- Haptic alert / “electronic shoulder-prick” notifier.
- “Find my mates at a party” proximity/direction tag.
- Hybrid biomedical + proximity module.

## Design priorities

1. **Small and wearable** — the board should be physically compact enough to mount in a small enclosure, strap, pendant, badge, or clothing module.
2. **Low power first** — sleep modes, ship mode, event-driven sensing, and careful radio duty-cycling matter more than maximum compute.
3. **Modular population** — optional footprints should make it possible to build cheap/simple and expensive/featureful variants from the same design family.
4. **Debuggable** — use visible test points, SWD, UART logs, measurement pads, and avoid packages that cannot be reworked during early prototypes unless there is no sane alternative.
5. **Honest signal quality** — biomedical sensing should be treated as an analog/mechanical/layout problem, not just a firmware problem.
6. **Cheap-enough direction sensing** — UWB is useful but expensive; the repo should track lower-cost BLE/RSSI/antenna-switching/channel-sounding options honestly.

## Non-goals for V1

- Certified medical device behavior.
- Miniaturized production enclosure.
- Waterproofing.
- Full consumer-product RF certification.
- Perfect direction finding in crowded RF environments.
- One board that supports every possible sensor at once without compromises.

## V1 success criteria

A V1 prototype is successful if it can:

- Boot reliably from a Li-ion/LiPo cell.
- Charge safely from USB or a defined charge connector.
- Enter and wake from low-power states.
- Advertise/log over BLE.
- Read at least one populated biosensor path.
- Drive at least one simple haptic/alert output.
- Expose enough test points to debug rails, I2C/SPI, SWD, and key interrupts.
- Demonstrate one ranging/proximity topology, even if crude.
- Produce logs that make failures diagnosable.
