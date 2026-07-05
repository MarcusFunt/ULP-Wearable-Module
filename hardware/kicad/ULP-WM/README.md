# Preliminary KiCad schematic

Open `ULP_Wearable_Module_Preliminary.kicad_pro` in KiCad 10 or newer. The generated
`ULP_Wearable_Module_Preliminary.net` is the corresponding KiCad S-expression netlist.

The schematic is a connected architecture and bring-up draft. It contains six hierarchical sheets:

1. USB-C/battery input, protection, nPM1300-QEAA, 1.8 V and 3.3 V buck rails.
2. nRF54L15-QFAA, reference decoupling, crystals, RF network, and status LED.
3. BMI270 and two independently addressed MCP9808 sensors on the 3.3 V I2C bus.
4. DRV2605L closed-loop ERM/LRA haptic driver and actuator connector.
5. Molex 226276-0202 expansion connector with power, I2C, SPI, UART, SWD, and GPIO nets.
6. SWD, UART, reset, and rail/bus test points.

## Critical limitations

- Every populated symbol has a footprint and all six ICs have named pin-level nets, so KiCad
  can transfer the design into PCB Editor. The generated netlist is still preliminary hardware.
- Verify every connection against current manufacturer datasheets and reference layouts before
  routing or ordering a PCB.
- Copy the complete Nordic QFN48 RF reference layout; the present matching network and antenna
  are not a production-qualified RF design.
- Select the protected battery pack and NTC, charge/thermal limits, TVS/fuse parts, crystals,
  and haptic actuator before PCB release.
- The footprint-aware BOM workbook records specified MPNs, generic selections, and release gates.

## Supplied vendor libraries

The generator reads the checksum-pinned `LIB_*.zip` archives from the user's `Downloads` directory,
verifies their SHA-256 hashes, and extracts only the KiCad symbol/footprint files under the
gitignored `build/vendor-kicad/` directory. The source archive license prohibits redistributing
the standalone library models, so they are deliberately not copied into the tracked project.

Required standard KiCad footprints are also copied into that project-local build library so the
generated schematic resolves every BOM footprint without adding global library-table entries.

If the archives move, set `ULP_WM_VENDOR_ZIP_DIR` to their containing directory before running
the generator.

## Regeneration

From the repository root:

```powershell
python hardware/kicad/ULP-WM/generate_preliminary_schematic.py
```

Regeneration replaces the generated schematic. Treat the Python source as authoritative until
the preliminary net assignment has been reviewed and the design moves to manual KiCad
maintenance. KiCad 10 reads the generated sheets directly; save the project from the editor to
upgrade every sheet to the current on-disk format.
