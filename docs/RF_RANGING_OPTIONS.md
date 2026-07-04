# RF and ranging options

## Goal

The project wants a cheap wearable/tag-like system that can help find nearby people or tags and ideally provide some direction between two tags. UWB is the clean technical answer for accurate ranging, but it is expensive and may not fit the low-cost wearable goal.

## Topology summary

| Topology | Cost | Direction support | Range quality | Power | Main problem |
|---|---:|---:|---:|---:|---|
| BLE RSSI | low | poor | rough proximity only | low | RSSI is unstable around bodies/crowds |
| BLE 5.1 AoA/AoD | medium | good with antenna arrays | moderate/good | medium | needs antenna array, calibration, and supported stack |
| BLE channel sounding | medium | ranging-focused | better than RSSI | medium | ecosystem/support maturity must be verified |
| UWB | high | good with multi-antenna/phase or multi-node geometry | best | medium/high | cost, footprint, RF/layout complexity |
| Custom analog RSSI array | low/medium | experimental | unknown | low/medium | calibration and multipath will be ugly |
| Magnetics/ultrasonic/IR | low/medium | situational | short-range only | variable | line-of-sight/orientation/environment issues |

## BLE RSSI baseline

Pros:

- Cheapest path.
- Already available on BLE SoC.
- Good enough for “near/far” and crowd-level proximity experiments.
- Low BOM cost.

Cons:

- Bad absolute distance estimate.
- Body shadowing is huge.
- Multipath at parties/indoors is brutal.
- Direction from two normal BLE tags is not realistic without extra antennas/movement/modeling.

Use RSSI as a baseline, not as the final direction solution.

## BLE AoA/AoD

BLE angle-of-arrival/angle-of-departure uses antenna switching and phase information. It can give direction, but the hardware is not just “one bare chip.”

Needs:

- Antenna array or switched antenna network.
- RF switch.
- Careful layout and antenna spacing.
- Calibration.
- Stack/tooling support.
- Mechanical orientation awareness if worn on the body.

Good for:

- A fixed receiver finding a moving tag.
- A larger wearable/badge that can fit multiple antennas.

Hard for:

- Two tiny identical tags estimating direction to each other with no antenna baseline.

## BLE channel sounding

Potentially important future path for BLE distance/ranging. Track it, but do not assume it is ready until the chosen SoC, SDK, examples, and phone/tag ecosystem are confirmed.

Questions to resolve:

- Does the selected SoC and SDK expose the needed feature set?
- Is the feature production-ready or demo-only?
- Can it run with the required power budget?
- Can it coexist with biosensing and logging duty cycles?

## UWB

Pros:

- Best normal technology for accurate short-range ranging.
- Better time-of-flight behavior than BLE RSSI.
- Realistic for “where is this tag?” systems.

Cons:

- More expensive.
- More layout-sensitive.
- More power-hungry.
- Often comes in modules or packages that may not match the desired cheap/bare-chip workflow.
- Direction requires either multiple antennas/phase support, multiple anchors, or motion/geometry tricks.

Recommendation:

- Keep UWB as an optional experiment path, not the only architecture.
- Do not put UWB peak current on the same small PMIC rail as optical LED pulses without a proper current budget.

## Custom low-cost direction experiments

Ideas worth testing:

1. **Dual/tri antenna RSSI switching**
   - Switch between small antennas and compare RSSI.
   - Very cheap, but multipath and body effects may dominate.

2. **Body-shadow direction heuristic**
   - Use the wearer’s body as a lossy obstacle.
   - Could produce crude left/right/back/front hints when combined with motion.
   - Highly user/orientation dependent.

3. **Motion-assisted bearing**
   - If the user walks/rotates, RSSI changes over time can provide a weak gradient.
   - Needs IMU and filtering.

4. **Two-tag cooperative measurements**
   - Exchange RSSI/channel data both ways.
   - Combine with IMU orientation and movement.
   - Direction still weak, but better than one-sided RSSI.

5. **Hybrid haptic search**
   - Do not try to show exact bearing.
   - Give haptic feedback when the user’s movement increases/decreases signal quality.
   - This may be much more achievable for a party/friend-finder use case.

## Practical recommendation for V1

V1 should implement:

- BLE advertisement/scan logging.
- Raw RSSI logging by channel if available.
- IMU orientation/motion logging if populated.
- Optional RF switch/antenna experiment footprint only if it does not ruin the main board.
- A clear connector/footprint plan for later UWB or external ranging module.

Do not promise absolute bearing from two tiny BLE tags in V1. Aim for measured data first.
