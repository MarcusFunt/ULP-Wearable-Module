# Safety and compliance

## Scope

This project is experimental. It may involve batteries, RF transmitters, optical sensors, and potentially body-contact electrodes or wearable enclosures. That combination deserves a serious safety boundary even at prototype stage.

## Hard rule

Do not represent this project as a medical device, diagnostic device, treatment device, or safety-critical monitor.

## Human-contact safety

If any part of the circuit touches skin or electrodes, review:

- Leakage current.
- Fault current.
- ESD protection.
- Input protection.
- Charger isolation.
- USB connection while worn.
- Moisture/sweat ingress.
- Skin irritation and material compatibility.
- Adhesives, gels, electrodes, and enclosure materials.

A prototype that is safe on a bench is not automatically safe on a person.

## Battery safety

For Li-ion/LiPo prototypes:

- Use a suitable charger IC/PMIC configuration.
- Respect battery charge voltage/current limits.
- Use current-limited supply during bring-up.
- Do not leave first-charge tests unattended.
- Confirm thermals in the actual enclosure.
- Provide strain relief for battery wires.
- Avoid sharp PCB/enclosure edges near pouch cells.
- Add a safe way to disconnect the battery.

## Optical safety

For LEDs/optical biosensing:

- Confirm LED current limits.
- Confirm optical exposure assumptions.
- Avoid direct eye exposure during debug.
- Keep LED duty cycle under firmware and hardware control.
- Consider failure modes where firmware gets stuck.

## RF safety and compliance

Prototype RF experiments should still respect:

- Local radio regulations.
- Antenna/reference-layout requirements.
- Output power limits.
- Duty-cycle requirements where relevant.
- Certification requirements before any distribution/sale.

## Data/privacy safety

Wearable data can be sensitive even if it is “just experimental.”

- Avoid collecting more personal data than needed.
- Mark logs with test IDs instead of names when possible.
- Keep raw biosensor data private.
- Do not publish datasets from people without explicit consent.
- Do not infer health conclusions from prototype signals.

## Firmware fail-safe expectations

Firmware should never be the only safety barrier for:

- Battery charging.
- Maximum LED current.
- Maximum haptic current.
- Human-contact leakage/fault conditions.
- Overtemperature.

Use hardware limits where practical.

## Before wearing a prototype

Minimum checklist:

- No exposed sharp conductors.
- No overheating during worst-case operation.
- Battery secured and protected.
- Charger behavior tested off-body.
- Human-contact path reviewed.
- No unsafe connection to USB/bench equipment while electrodes touch skin.
- Firmware can disable haptics/LEDs/radios.
- Enclosure protects against sweat and accidental shorts.

## Before sharing a prototype with another person

- Explain that it is experimental.
- Do not claim it measures health accurately.
- Do not use it on minors or vulnerable people.
- Do not use it for medical decisions.
- Log consent if collecting biosensor data.
- Have a safe removal/power-off method.
