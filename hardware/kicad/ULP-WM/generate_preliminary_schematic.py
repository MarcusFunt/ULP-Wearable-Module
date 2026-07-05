"""Generate the preliminary ULP Wearable Module KiCad schematic.

The supplied vendor symbols and footprints are used, but the net assignment and support
circuitry remain provisional. Verify them against current reference designs before layout.
"""

# ruff: noqa: E402, I001 -- KiCad environment variables must precede the SKiDL import.

from __future__ import annotations

import os
import hashlib
import shutil
import zipfile
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_DIR.parents[2]
SCHEMATIC_NAME = "ULP_Wearable_Module_Preliminary"
VENDOR_ROOT = REPO_ROOT / "build/vendor-kicad"
VENDOR_SYMBOL_DIR = VENDOR_ROOT / "symbols"
VENDOR_FOOTPRINT_DIR = VENDOR_ROOT / "footprints/SamacSys.pretty"
VENDOR_ARCHIVE_DIR = Path(
    os.environ.get("ULP_WM_VENDOR_ZIP_DIR", str(Path.home() / "Downloads"))
)

VENDOR_ARCHIVES = {
    "LIB_UJC-H-G1-SMT-P6-TR-67.zip": {
        "sha256": "E2B7C1C33A3E60AAA7666B7AA324FAE742C9A43A331DE3EB597D26A1DA434721",
        "symbol": "UJC-H-G1-SMT-P6-TR-67/KiCad/UJC-H-G1-SMT-P6-TR-67.kicad_sym",
        "footprint": "UJC-H-G1-SMT-P6-TR-67/KiCad/UJCHG1SMTP6TR67.kicad_mod",
    },
    "LIB_MLX90632SLD-DCB-100-RE.zip": {
        "sha256": "E0EA195D3085423984735ACB724B1046E9585A2379FE1C68D5A71ECD5EC40090",
        "symbol": "MLX90632SLD-DCB-100-RE/KiCad/MLX90632SLD-DCB-100-RE.kicad_sym",
        "footprint": "MLX90632SLD-DCB-100-RE/KiCad/MLX90632SLDDCB100RE.kicad_mod",
    },
    "LIB_MCP9808T-E_MC.zip": {
        "sha256": "EF34EE04DC89EFD11B45E2DDF92632424553B519BC2EDB2580B97CC61E4AF05A",
        "symbol": "MCP9808T-E_MC/KiCad/MCP9808T-E_MC.kicad_sym",
        "footprint": "MCP9808T-E_MC/KiCad/SON50P300X200X100-9N-D.kicad_mod",
    },
    "LIB_BMI270.zip": {
        "sha256": "88A7EFCD94960F7CE617077D59E55EC07F1AA084000CA81B65BD14C5C8AA26A0",
        "symbol": "BMI270/KiCad/BMI270.kicad_sym",
        "footprint": "BMI270/KiCad/BMI270.kicad_mod",
    },
    "LIB_226276-0202.zip": {
        "sha256": "BE87D61B466030152CB3AD3D95AAA9AAB9E29CD880030C9009F121B7DC14ED8E",
        "symbol": "226276-0202/KiCad/226276-0202.kicad_sym",
        "footprint": "226276-0202/KiCad/2262760202.kicad_mod",
    },
    "LIB_nPM1300-CAAA-R7.zip": {
        "sha256": "697EE4FB946809C0B584721CFDDAEB99AFBB1901FB022E0AB0B2DA34DC735768",
        "symbol": "nPM1300-CAAA-R7/KiCad/nPM1300-CAAA-R7.kicad_sym",
        "footprint": "nPM1300-CAAA-R7/KiCad/BGA35C44P7X5_308X238X51.kicad_mod",
    },
    "LIB_NRF54L15-QFAA-R7.zip": {
        "sha256": "09B00885EE15A264A36332F7F46CB8D14660B7D18674068F9D9717FC4071B6AD",
        "symbol": "NRF54L15-QFAA-R7/KiCad/NRF54L15-QFAA-R7.kicad_sym",
        "footprint": "NRF54L15-QFAA-R7/KiCad/QFN40P600X600X90-49N-D.kicad_mod",
    },
}

STANDARD_FOOTPRINTS = [
    "RF_Antenna.pretty/Johanson_2450AT18x100.kicad_mod",
    "Button_Switch_SMD.pretty/SW_Push_1P1T_NO_CK_KMR2.kicad_mod",
    "Connector_JST.pretty/JST_PH_S3B-PH-K_1x03_P2.00mm_Horizontal.kicad_mod",
    "Connector_JST.pretty/JST_SH_SM02B-SRSS-TB_1x02-1MP_P1.00mm_Horizontal.kicad_mod",
    "Connector_PinHeader_1.27mm.pretty/PinHeader_1x04_P1.27mm_Vertical_SMD_Pin1Left.kicad_mod",
    "Connector_PinHeader_1.27mm.pretty/PinHeader_2x05_P1.27mm_Vertical_SMD.kicad_mod",
    "Crystal.pretty/Crystal_SMD_2012-2Pin_2.0x1.2mm.kicad_mod",
    "Crystal.pretty/Crystal_SMD_2016-4Pin_2.0x1.6mm.kicad_mod",
    "Inductor_SMD.pretty/L_0201_0603Metric.kicad_mod",
    "Inductor_SMD.pretty/L_0603_1608Metric.kicad_mod",
    "Inductor_SMD.pretty/L_Murata_DFE201610P.kicad_mod",
    "Package_DFN_QFN.pretty/VQFN-32-1EP_5x5mm_P0.5mm_EP3.5x3.5mm.kicad_mod",
    "Package_SO.pretty/TSSOP-10_3x3mm_P0.5mm.kicad_mod",
]


def install_vendor_libraries() -> None:
    """Extract the supplied, checksum-pinned KiCad files into ignored build output."""
    VENDOR_SYMBOL_DIR.mkdir(parents=True, exist_ok=True)
    VENDOR_FOOTPRINT_DIR.mkdir(parents=True, exist_ok=True)

    for archive_name, metadata in VENDOR_ARCHIVES.items():
        archive_path = VENDOR_ARCHIVE_DIR / archive_name
        if not archive_path.is_file():
            raise FileNotFoundError(
                f"Missing {archive_path}; set ULP_WM_VENDOR_ZIP_DIR if the archives moved"
            )
        digest = hashlib.sha256(archive_path.read_bytes()).hexdigest().upper()
        if digest != metadata["sha256"]:
            raise ValueError(f"Checksum mismatch for {archive_name}")

        with zipfile.ZipFile(archive_path) as archive:
            symbol_member = metadata["symbol"]
            footprint_member = metadata["footprint"]
            (VENDOR_SYMBOL_DIR / Path(symbol_member).name).write_bytes(
                archive.read(symbol_member)
            )
            (VENDOR_FOOTPRINT_DIR / Path(footprint_member).name).write_bytes(
                archive.read(footprint_member)
            )


def configure_kicad_environment() -> None:
    """Point SKiDL's KiCad 9 backend at an installed KiCad 10 library tree."""
    local_app_data = Path(os.environ.get("LOCALAPPDATA", ""))
    symbol_candidates = [
        local_app_data / "Programs/KiCad/10.0/share/kicad/symbols",
        Path("C:/Program Files/KiCad/10.0/share/kicad/symbols"),
        Path("/usr/share/kicad/symbols"),
    ]
    footprint_candidates = [
        local_app_data / "Programs/KiCad/10.0/share/kicad/footprints",
        Path("C:/Program Files/KiCad/10.0/share/kicad/footprints"),
        Path("/usr/share/kicad/footprints"),
    ]

    if configured_symbols := os.environ.get("KICAD10_SYMBOL_DIR"):
        symbol_candidates.insert(0, Path(configured_symbols))
    if configured_footprints := os.environ.get("KICAD10_FOOTPRINT_DIR"):
        footprint_candidates.insert(0, Path(configured_footprints))

    symbol_dir = next((path for path in symbol_candidates if path.is_dir()), None)
    footprint_dir = next((path for path in footprint_candidates if path.is_dir()), None)
    if symbol_dir is None:
        raise FileNotFoundError("KiCad 10 symbol libraries were not found")

    # SKiDL 2.2 writes KiCad 9 syntax, which KiCad 10 upgrades losslessly.
    os.environ["KICAD_SYMBOL_DIR"] = str(symbol_dir)
    for version in range(6, 10):
        os.environ[f"KICAD{version}_SYMBOL_DIR"] = str(symbol_dir)
    if footprint_dir is not None:
        for version in range(6, 10):
                os.environ[f"KICAD{version}_FOOTPRINT_DIR"] = str(footprint_dir)


def install_standard_footprints() -> None:
    """Copy used KiCad standard footprints into the existing project-local library."""
    footprint_root = Path(os.environ["KICAD9_FOOTPRINT_DIR"])
    for relative_path in STANDARD_FOOTPRINTS:
        source = footprint_root / relative_path
        if not source.is_file():
            raise FileNotFoundError(f"Required KiCad footprint not found: {source}")
        destination = VENDOR_FOOTPRINT_DIR / source.name
        if destination.exists():
            destination.chmod(0o666)
        shutil.copyfile(source, destination)
        destination.chmod(0o666)


install_vendor_libraries()
configure_kicad_environment()
install_standard_footprints()
os.chdir(PROJECT_DIR)

from skidl import (  # noqa: E402
    KICAD9,
    TEMPLATE,
    Net,
    Part,
    generate_schematic,
    lib_search_paths,
    set_default_tool,
    subcircuit,
)


set_default_tool(KICAD9)
lib_search_paths[KICAD9].insert(0, str(VENDOR_SYMBOL_DIR))

R_0402 = "Resistor_SMD:R_0402_1005Metric"
R_0201 = "Resistor_SMD:R_0201_0603Metric"
C_0402 = "Capacitor_SMD:C_0402_1005Metric"
C_0201 = "Capacitor_SMD:C_0201_0603Metric"
C_0603 = "Capacitor_SMD:C_0603_1608Metric"
L_0201 = "SamacSys:L_0201_0603Metric"
L_0603 = "SamacSys:L_0603_1608Metric"
L_0806 = "SamacSys:L_Murata_DFE201610P"
_PART_TEMPLATES: dict[tuple[str, str], Part] = {}
_NPM1300_QEAA_TEMPLATE: Part | None = None


def component(
    library: str,
    name: str,
    *,
    ref: str,
    value: str,
    footprint: str = ":",
) -> Part:
    """Create a component with an explicit reference and value."""
    key = (library, name)
    if key not in _PART_TEMPLATES:
        _PART_TEMPLATES[key] = Part(library, name, dest=TEMPLATE)
    return _PART_TEMPLATES[key](ref=ref, value=value, footprint=footprint)


def connect_pins(part: Part, mapping: dict[str, Net]) -> None:
    """Connect a symbol's numbered pins to named nets."""
    for pin_number, net in mapping.items():
        net += part[pin_number]


def npm1300_qeaa(*, ref: str = "U2") -> Part:
    """Create the QFN32 nPM1300 variant used by the supplied EasyEDA sheet."""
    global _NPM1300_QEAA_TEMPLATE
    if _NPM1300_QEAA_TEMPLATE is None:
        pin_names = {
            "1": "VOUT1",
            "2": "PVSS1",
            "3": "SW1",
            "4": "PVDD",
            "5": "SW2",
            "6": "PVSS2",
            "7": "GPIO0",
            "8": "GPIO1",
            "9": "GPIO2",
            "10": "GPIO3",
            "11": "GPIO4",
            "12": "VDDIO",
            "13": "SDA",
            "14": "SCL",
            "15": "SHPHLD",
            "16": "VSET2",
            "17": "VSET1",
            "18": "NTC",
            "19": "VBAT",
            "20": "VSYS",
            "21": "VBUS",
            "22": "VBUSOUT",
            "23": "CC1",
            "24": "CC2",
            "25": "LED0",
            "26": "LED1",
            "27": "LED2",
            "28": "LSIN1/VINLDO1",
            "29": "LSOUT1/VOUTLDO1",
            "30": "LSIN2/VINLDO2",
            "31": "LSOUT2/VOUTLDO2",
            "32": "VOUT2",
            "33": "AVSS",
        }
        _NPM1300_QEAA_TEMPLATE = Part(
            "Connector_Generic", "Conn_02x17_Odd_Even", dest=TEMPLATE
        )
        _NPM1300_QEAA_TEMPLATE.name = "nPM1300-QEAA-R7"
        _NPM1300_QEAA_TEMPLATE.ref_prefix = "U"
        for number, name in pin_names.items():
            _NPM1300_QEAA_TEMPLATE[number].name = name
        _NPM1300_QEAA_TEMPLATE["34"].name = "NC"
        _NPM1300_QEAA_TEMPLATE["34"].do_erc = False
    return _NPM1300_QEAA_TEMPLATE(
        ref=ref,
        value="nPM1300-QEAA-R7",
        footprint="SamacSys:VQFN-32-1EP_5x5mm_P0.5mm_EP3.5x3.5mm",
    )


def decouple(ref: str, rail: Net, ground: Net, value: str, footprint: str = C_0402) -> Part:
    """Add a local rail-to-ground bypass capacitor."""
    capacitor = component("Device", "C", ref=ref, value=value, footprint=footprint)
    rail += capacitor[1]
    ground += capacitor[2]
    return capacitor


@subcircuit
def power_and_charging(
    vbus_usb: Net,
    vbat: Net,
    vdd_1v8: Net,
    vdd_3v3: Net,
    vdd_3v3_rf: Net,
    ground: Net,
    i2c_sda: Net,
    i2c_scl: Net,
    pmic_int: Net,
    pmic_ship: Net,
    rf_enable: Net,
    batt_ntc: Net,
) -> None:
    """USB power, battery input, current link, and nPM1300 power tree."""
    vbus_protected = Net("VBUS_PROTECTED")
    battery_connector = Net("BATTERY_CONNECTOR_POS")
    vsys = Net("VSYS")
    vbus_out = Net("VBUSOUT")
    buck1_sw = Net("BUCK1_SW")
    buck2_sw = Net("BUCK2_SW")
    pmic_vset1 = Net("PMIC_VSET1")
    pmic_vset2 = Net("PMIC_VSET2")
    pmic_led0 = Net("PMIC_LED0")
    pmic_led1 = Net("PMIC_LED1")
    pmic_led2 = Net("PMIC_LED2")
    pmic_gpio2 = Net("PMIC_GPIO2")
    pmic_gpio3 = Net("PMIC_GPIO3")
    pmic_gpio4 = Net("PMIC_GPIO4")
    vdd_aux = Net("VDD_AUX")
    npm_nc = Net("NPM1300_PIN34_NC")
    usb_cc1 = Net("USB_CC1")
    usb_cc2 = Net("USB_CC2")

    usb = component(
        "UJC-H-G1-SMT-P6-TR-67",
        "UJC-H-G1-SMT-P6-TR-67",
        ref="J1",
        value="UJC-H-G1-SMT-P6-TR-67",
        footprint="SamacSys:UJCHG1SMTP6TR67",
    )
    connect_pins(
        usb,
        {
            "A5": usb_cc1,
            "A9": vbus_usb,
            "A12": ground,
            "B5": usb_cc2,
            "B9": vbus_usb,
            "B12": ground,
            "MH1": ground,
            "MH2": ground,
        },
    )

    fuse = component(
        "Device",
        "Fuse",
        ref="F1",
        value="500mA PTC - TBD",
        footprint="Fuse:Fuse_1206_3216Metric",
    )
    vbus_usb += fuse[1]
    vbus_protected += fuse[2]

    tvs = component(
        "Device",
        "D_TVS",
        ref="D1",
        value="5V low-leakage TVS - TBD",
        footprint="Diode_SMD:D_SOD-323",
    )
    vbus_protected += tvs[1]
    ground += tvs[2]
    decouple("C2", vbus_protected, ground, "10u 25V X5R", C_0603)

    battery = component(
        "Connector_Generic",
        "Conn_01x03",
        ref="J2",
        value="1S LiPo: BAT+, GND, NTC",
        footprint="SamacSys:JST_PH_S3B-PH-K_1x03_P2.00mm_Horizontal",
    )
    battery_connector += battery[1]
    ground += battery[2]
    batt_ntc += battery[3]

    current_link = component(
        "Device",
        "R",
        ref="R3",
        value="0R CURRENT MEASURE LINK",
        footprint="Resistor_SMD:R_0603_1608Metric",
    )
    battery_connector += current_link[1]
    vbat += current_link[2]
    decouple("C4", vbat, ground, "10u 25V X5R", C_0603)

    pmic = npm1300_qeaa(ref="U2")
    connect_pins(
        pmic,
        {
            "1": vdd_1v8,
            "2": ground,
            "3": buck1_sw,
            "4": vsys,
            "5": buck2_sw,
            "6": ground,
            "7": pmic_int,
            "8": rf_enable,
            "9": pmic_gpio2,
            "10": pmic_gpio3,
            "11": pmic_gpio4,
            "12": vdd_3v3,
            "13": i2c_sda,
            "14": i2c_scl,
            "15": pmic_ship,
            "16": pmic_vset2,
            "17": pmic_vset1,
            "18": batt_ntc,
            "19": vbat,
            "20": vsys,
            "21": vbus_protected,
            "22": vbus_out,
            "23": usb_cc1,
            "24": usb_cc2,
            "25": pmic_led0,
            "26": pmic_led1,
            "27": pmic_led2,
            "28": vsys,
            "29": vdd_3v3_rf,
            "30": vsys,
            "31": vdd_aux,
            "32": vdd_3v3,
            "33": ground,
            "34": npm_nc,
        },
    )

    buck1 = component("Device", "L", ref="L1", value="2.2u", footprint=L_0806)
    buck1_sw += buck1[1]
    vdd_1v8 += buck1[2]
    buck2 = component("Device", "L", ref="L2", value="2.2u", footprint=L_0806)
    buck2_sw += buck2[1]
    vdd_3v3 += buck2[2]

    r_vset1 = component("Device", "R", ref="R1", value="47k 1%", footprint=R_0201)
    r_vset2 = component("Device", "R", ref="R2", value="330k 1%", footprint=R_0201)
    pmic_vset1 += r_vset1[1]
    pmic_vset2 += r_vset2[1]
    ground += r_vset1[2], r_vset2[2]

    decouple("C1", vbus_out, ground, "1u 10V X5R", C_0603)
    decouple("C3", vsys, ground, "10u 25V X5R", C_0603)
    decouple("C5", vdd_3v3, ground, "1u 10V X5R", C_0603)
    decouple("C6", vsys, ground, "2.2u 16V X7R", C_0603)
    decouple("C7", vdd_1v8, ground, "10u 25V X5R", C_0603)
    decouple("C8", vdd_3v3, ground, "10u 25V X5R", C_0603)
    decouple("C9", vdd_3v3_rf, ground, "10u 25V X5R", C_0603)
    decouple("C10", vdd_aux, ground, "10u 25V X5R", C_0603)
    decouple("C31", vsys, ground, "100n 10V X7R", C_0201)

    sda_pullup = component("Device", "R", ref="R5", value="4.7k 1%", footprint=R_0201)
    scl_pullup = component("Device", "R", ref="R6", value="4.7k 1%", footprint=R_0201)
    vdd_3v3 += sda_pullup[1], scl_pullup[1]
    i2c_sda += sda_pullup[2]
    i2c_scl += scl_pullup[2]

    for ref, net in [("#FLG01", ground), ("#FLG02", vbus_usb), ("#FLG03", vbat)]:
        flag = component("power", "PWR_FLAG", ref=ref, value="PWR_FLAG")
        net += flag[1]


@subcircuit
def main_soc_and_ble(
    vdd_3v3: Net,
    ground: Net,
    i2c_sda: Net,
    i2c_scl: Net,
    pmic_int: Net,
    pmic_ship: Net,
    swdio: Net,
    swclk: Net,
    reset_n: Net,
    uart_tx: Net,
    uart_rx: Net,
    temp_alert: Net,
    bmi_int1: Net,
    bmi_int2: Net,
    sensor_enable: Net,
    haptic_pwm: Net,
    haptic_enable: Net,
    status_led: Net,
    rf_enable: Net,
    rf_irq: Net,
    rf_sck: Net,
    rf_mosi: Net,
    rf_miso: Net,
    rf_cs: Net,
) -> None:
    """nRF54L15-QFAA, clocks, RF tuning network, and assigned peripheral nets."""
    xtal_32m_p = Net("XTAL_32M_P")
    xtal_32m_n = Net("XTAL_32M_N")
    xtal_32k_p = Net("XTAL_32K_P")
    xtal_32k_n = Net("XTAL_32K_N")
    soc_ant = Net("SOC_ANT")
    ant_feed = Net("ANT_FEED")
    nfc1 = Net("NFC1")
    nfc2 = Net("NFC2")
    clk32k_out = Net("CLK32K_OUT")
    decrf = Net("DECRF")
    deca = Net("DECA")
    decd = Net("DECD")
    dcc = Net("DCC")
    spare_gpio = [Net(f"GPIO_SPARE_{index}") for index in range(7)]

    soc = component(
        "NRF54L15-QFAA-R7",
        "NRF54L15-QFAA-R7",
        ref="U1",
        value="NRF54L15-QFAA-R7",
        footprint="SamacSys:QFN40P600X600X90-49N-D",
    )
    connect_pins(
        soc,
        {
            "1": xtal_32k_p,
            "2": xtal_32k_n,
            "3": nfc1,
            "4": nfc2,
            "5": i2c_sda,
            "6": i2c_scl,
            "7": temp_alert,
            "8": sensor_enable,
            "9": bmi_int1,
            "10": vdd_3v3,
            "11": haptic_pwm,
            "12": rf_sck,
            "13": rf_mosi,
            "14": status_led,
            "15": rf_miso,
            "16": rf_cs,
            "17": uart_tx,
            "18": uart_rx,
            "19": rf_irq,
            "20": rf_enable,
            "21": haptic_enable,
            "22": vdd_3v3,
            "23": pmic_int,
            "24": pmic_ship,
            "25": swdio,
            "26": swclk,
            "27": bmi_int2,
            "28": spare_gpio[0],
            "29": clk32k_out,
            "30": reset_n,
            "31": soc_ant,
            "32": ground,
            "33": decrf,
            "34": xtal_32m_p,
            "35": xtal_32m_n,
            "36": vdd_3v3,
            "37": spare_gpio[1],
            "38": spare_gpio[2],
            "39": spare_gpio[3],
            "40": spare_gpio[4],
            "41": spare_gpio[5],
            "42": spare_gpio[6],
            "43": deca,
            "44": ground,
            "45": decd,
            "46": dcc,
            "47": vdd_3v3,
            "48": vdd_3v3,
            "49": ground,
        },
    )
    decouple("C11", vdd_3v3, ground, "10u 6.3V X6S", C_0402)
    decouple("C12", vdd_3v3, ground, "100n 10V X7R", C_0201)
    decouple("C13", vdd_3v3, ground, "100n 10V X7R", C_0201)
    decouple("C33", decrf, ground, "2.2u 2.5V X6T", C_0201)
    decouple("C34", deca, ground, "2.2u 2.5V X6T", C_0201)
    decouple("C35", decd, ground, "100n 10V X7R", C_0201)

    dcc_inductor = component("Device", "L", ref="L3", value="4.7u 120mA", footprint=L_0603)
    dcc += dcc_inductor[1]
    vdd_3v3 += dcc_inductor[2]

    crystal_32m = component(
        "Device",
        "Crystal_GND24",
        ref="Y1",
        value="32MHz CL=8pF +/-40ppm",
        footprint="SamacSys:Crystal_SMD_2016-4Pin_2.0x1.6mm",
    )
    xtal_32m_p += crystal_32m[1]
    ground += crystal_32m[2], crystal_32m[4]
    xtal_32m_n += crystal_32m[3]

    crystal_32k = component(
        "Device",
        "Crystal",
        ref="Y2",
        value="32.768kHz CL=9pF +/-20ppm",
        footprint="SamacSys:Crystal_SMD_2012-2Pin_2.0x1.2mm",
    )
    xtal_32k_p += crystal_32k[1]
    xtal_32k_n += crystal_32k[2]

    rf_series = component("Device", "L", ref="L4", value="3.5n RF reference", footprint=L_0201)
    soc_ant += rf_series[1]
    ant_feed += rf_series[2]
    decouple("C18", soc_ant, ground, "1.5p C0G high-Q", C_0201)
    decouple("C19", ant_feed, ground, "2.0p C0G high-Q", C_0201)
    antenna = component(
        "Device",
        "Antenna_Chip",
        ref="AE1",
        value="2.4GHz antenna - select with layout",
        footprint="SamacSys:Johanson_2450AT18x100",
    )
    ant_feed += antenna[1]
    ground += antenna[2]

    led_resistor = component("Device", "R", ref="R4", value="1k", footprint=R_0402)
    led = component(
        "Device",
        "LED",
        ref="D2",
        value="STATUS",
        footprint="LED_SMD:LED_0402_1005Metric",
    )
    status_led += led_resistor[1]
    led_resistor[2] += led[1]
    ground += led[2]


@subcircuit
def biosensor_front_end(
    vdd_3v3: Net,
    ground: Net,
    i2c_sda: Net,
    i2c_scl: Net,
    temp_alert: Net,
    bmi_int1: Net,
    bmi_int2: Net,
) -> None:
    """BMI270 and two uniquely addressed MCP9808 sensors on a 3.3 V I2C bus."""
    bmi_aux_sda = Net("BMI270_AUX_SDA_NC")
    bmi_aux_scl = Net("BMI270_AUX_SCL_NC")
    bmi_ois_sdo = Net("BMI270_OIS_SDO_NC")

    bmi = component(
        "BMI270",
        "BMI270",
        ref="U3",
        value="BMI270",
        footprint="SamacSys:BMI270",
    )
    connect_pins(
        bmi,
        {
            "1": ground,
            "2": bmi_aux_sda,
            "3": bmi_aux_scl,
            "4": bmi_int1,
            "5": vdd_3v3,
            "6": ground,
            "7": ground,
            "8": vdd_3v3,
            "9": bmi_int2,
            "10": vdd_3v3,
            "11": bmi_ois_sdo,
            "12": vdd_3v3,
            "13": i2c_scl,
            "14": i2c_sda,
        },
    )
    decouple("C20", vdd_3v3, ground, "100n 10V X7R", C_0201)
    decouple("C21", vdd_3v3, ground, "100n 10V X7R", C_0201)

    mcp_0 = component(
        "MCP9808T-E_MC",
        "MCP9808T-E_MC",
        ref="U4",
        value="MCP9808T-E/MC (0x18)",
        footprint="SamacSys:SON50P300X200X100-9N-D",
    )
    connect_pins(
        mcp_0,
        {
            "1": i2c_sda,
            "2": i2c_scl,
            "3": temp_alert,
            "4": ground,
            "5": ground,
            "6": ground,
            "7": ground,
            "8": vdd_3v3,
            "9": ground,
        },
    )
    decouple("C22", vdd_3v3, ground, "100n 10V X7R", C_0201)

    mcp_1 = component(
        "MCP9808T-E_MC",
        "MCP9808T-E_MC",
        ref="U5",
        value="MCP9808T-E/MC (0x19)",
        footprint="SamacSys:SON50P300X200X100-9N-D",
    )
    connect_pins(
        mcp_1,
        {
            "1": i2c_sda,
            "2": i2c_scl,
            "3": temp_alert,
            "4": ground,
            "5": ground,
            "6": ground,
            "7": vdd_3v3,
            "8": vdd_3v3,
            "9": ground,
        },
    )
    decouple("C23", vdd_3v3, ground, "100n 10V X7R", C_0201)

    alert_pullup = component("Device", "R", ref="R7", value="10k 1%", footprint=R_0201)
    vdd_3v3 += alert_pullup[1]
    temp_alert += alert_pullup[2]

    sensor_bulk = component(
        "Device",
        "C",
        ref="C24",
        value="4.7u 6.3V X5R",
        footprint=C_0402,
    )
    vdd_3v3 += sensor_bulk[1]
    ground += sensor_bulk[2]


@subcircuit
def haptic_output(
    vbat: Net,
    ground: Net,
    i2c_sda: Net,
    i2c_scl: Net,
    haptic_trigger: Net,
    haptic_enable: Net,
) -> None:
    """DRV2605L I2C haptic driver with a differential actuator connector."""
    haptic_reg = Net("HAPTIC_REG")
    haptic_out_p = Net("HAPTIC_OUT+")
    haptic_out_n = Net("HAPTIC_OUT-")

    driver = component(
        "Driver",
        "DRV2605LDGS",
        ref="U6",
        value="DRV2605LDGSR",
        footprint="SamacSys:TSSOP-10_3x3mm_P0.5mm",
    )
    connect_pins(
        driver,
        {
            "1": haptic_reg,
            "2": i2c_scl,
            "3": i2c_sda,
            "4": haptic_trigger,
            "5": haptic_enable,
            "6": vbat,
            "7": haptic_out_p,
            "8": ground,
            "9": haptic_out_n,
            "10": vbat,
        },
    )

    enable_pulldown = component("Device", "R", ref="R8", value="100k 1%", footprint=R_0402)
    trigger_pulldown = component(
        "Device", "R", ref="R10", value="100k 1%", footprint=R_0402
    )
    haptic_enable += enable_pulldown[1]
    haptic_trigger += trigger_pulldown[1]
    ground += enable_pulldown[2], trigger_pulldown[2]

    decouple("C27", haptic_reg, ground, "1u 10V X5R", C_0402)
    decouple("C28", vbat, ground, "1u 10V X5R", C_0402)
    decouple("C36", vbat, ground, "47u 6.3V low-ESR", "Capacitor_SMD:C_1206_3216Metric")

    actuator = component(
        "Connector_Generic",
        "Conn_01x02",
        ref="J8",
        value="LRA/ERM HAPTIC ACTUATOR",
        footprint="SamacSys:JST_SH_SM02B-SRSS-TB_1x02-1MP_P1.00mm_Horizontal",
    )
    haptic_out_p += actuator[1]
    haptic_out_n += actuator[2]


@subcircuit
def optional_ranging_connector(
    vdd_1v8: Net,
    vdd_3v3_rf: Net,
    ground: Net,
    i2c_sda: Net,
    i2c_scl: Net,
    rf_enable: Net,
    rf_irq: Net,
    rf_sck: Net,
    rf_mosi: Net,
    rf_miso: Net,
    rf_cs: Net,
    uart_tx: Net,
    uart_rx: Net,
    swdio: Net,
    swclk: Net,
    reset_n: Net,
    pmic_int: Net,
    temp_alert: Net,
    bmi_int1: Net,
    bmi_int2: Net,
    sensor_enable: Net,
) -> None:
    """Molex 226276-0202 board-to-board expansion connector."""
    expansion_gpio0 = Net("EXP_GPIO0")
    expansion_gpio1 = Net("EXP_GPIO1")
    mechanical_nets = [Net(f"J5_MECH_{index}") for index in range(1, 7)]

    expansion = component(
        "226276-0202",
        "226276-0202",
        ref="J5",
        value="226276-0202 EXPANSION",
        footprint="SamacSys:2262760202",
    )
    connect_pins(
        expansion,
        {
            "1": i2c_sda,
            "2": i2c_scl,
            "3": rf_sck,
            "4": rf_mosi,
            "5": rf_miso,
            "6": rf_cs,
            "7": uart_tx,
            "8": uart_rx,
            "9": swdio,
            "10": swclk,
            "11": reset_n,
            "12": pmic_int,
            "13": temp_alert,
            "14": bmi_int1,
            "15": bmi_int2,
            "16": sensor_enable,
            "17": rf_irq,
            "18": rf_enable,
            "19": expansion_gpio0,
            "20": expansion_gpio1,
            "21": vdd_1v8,
            "22": vdd_1v8,
            "23": vdd_3v3_rf,
            "24": vdd_3v3_rf,
            "25": ground,
            "26": ground,
            "27": ground,
            "28": ground,
            "29": mechanical_nets[0],
            "30": mechanical_nets[1],
            "31": mechanical_nets[2],
            "32": mechanical_nets[3],
            "33": mechanical_nets[4],
            "34": mechanical_nets[5],
        },
    )
    decouple("C29", vdd_3v3_rf, ground, "10u", C_0603)
    decouple("C30", vdd_3v3_rf, ground, "100n")


@subcircuit
def debug_and_test(
    vdd_3v3: Net,
    vdd_1v8: Net,
    vdd_3v3_rf: Net,
    vbat: Net,
    ground: Net,
    swdio: Net,
    swclk: Net,
    reset_n: Net,
    uart_tx: Net,
    uart_rx: Net,
    i2c_sda: Net,
    i2c_scl: Net,
    pmic_int: Net,
) -> None:
    """SWD, UART, reset, and rail/bus test points for V1 bring-up."""
    swd_key = Net("SWD_KEY_NC")
    swd_spare = Net("SWD_SPARE_NC")
    swd = component(
        "Connector_Generic",
        "Conn_02x05_Odd_Even",
        ref="J6",
        value="ARM CORTEX 10-PIN SWD",
        footprint="SamacSys:PinHeader_2x05_P1.27mm_Vertical_SMD",
    )
    for pin, net in zip(
        swd,
        [
            vdd_3v3,
            swdio,
            ground,
            swclk,
            ground,
            uart_tx,
            swd_key,
            swd_spare,
            ground,
            reset_n,
        ],
        strict=True,
    ):
        net += pin

    uart = component(
        "Connector_Generic",
        "Conn_01x04",
        ref="J7",
        value="UART: VREF, GND, TX, RX",
        footprint="SamacSys:PinHeader_1x04_P1.27mm_Vertical_SMD_Pin1Left",
    )
    for pin, net in zip(uart, [vdd_3v3, ground, uart_tx, uart_rx], strict=True):
        net += pin

    reset_pullup = component("Device", "R", ref="R9", value="10k", footprint=R_0402)
    vdd_3v3 += reset_pullup[1]
    reset_n += reset_pullup[2]
    reset_switch = component(
        "Switch",
        "SW_Push",
        ref="SW1",
        value="RESET",
        footprint="SamacSys:SW_Push_1P1T_NO_CK_KMR2",
    )
    reset_n += reset_switch[1]
    ground += reset_switch[2]

    test_nets = [
        ("TP1", vbat),
        ("TP2", vdd_3v3),
        ("TP3", vdd_1v8),
        ("TP4", vdd_3v3_rf),
        ("TP5", ground),
        ("TP6", i2c_sda),
        ("TP7", i2c_scl),
        ("TP8", pmic_int),
        ("TP9", swdio),
        ("TP10", swclk),
    ]
    for ref, net in test_nets:
        testpoint = component(
            "Connector",
            "TestPoint",
            ref=ref,
            value=net.name,
            footprint="TestPoint:TestPoint_THTPad_D1.0mm_Drill0.5mm",
        )
        net += testpoint[1]


def build_schematic() -> None:
    """Instantiate all sheets and write the native KiCad schematic."""
    nets = {
        name: Net(name)
        for name in [
            "VBUS_USB",
            "VBAT",
            "VDD_1V8",
            "VDD_3V3",
            "VDD_3V3_RF_OPT",
            "GND",
            "I2C_SDA",
            "I2C_SCL",
            "PMIC_INT",
            "PMIC_SHIP",
            "BATT_NTC",
            "SWDIO",
            "SWCLK",
            "RESET_N",
            "UART_TX",
            "UART_RX",
            "TEMP_ALERT",
            "BMI270_INT1",
            "BMI270_INT2",
            "SENSOR_ENABLE",
            "HAPTIC_PWM",
            "HAPTIC_ENABLE",
            "STATUS_LED",
            "RF_ENABLE",
            "RF_IRQ",
            "RF_SPI_SCK",
            "RF_SPI_MOSI",
            "RF_SPI_MISO",
            "RF_SPI_CS",
        ]
    }

    power_and_charging(
        nets["VBUS_USB"],
        nets["VBAT"],
        nets["VDD_1V8"],
        nets["VDD_3V3"],
        nets["VDD_3V3_RF_OPT"],
        nets["GND"],
        nets["I2C_SDA"],
        nets["I2C_SCL"],
        nets["PMIC_INT"],
        nets["PMIC_SHIP"],
        nets["RF_ENABLE"],
        nets["BATT_NTC"],
    )
    main_soc_and_ble(
        nets["VDD_3V3"],
        nets["GND"],
        nets["I2C_SDA"],
        nets["I2C_SCL"],
        nets["PMIC_INT"],
        nets["PMIC_SHIP"],
        nets["SWDIO"],
        nets["SWCLK"],
        nets["RESET_N"],
        nets["UART_TX"],
        nets["UART_RX"],
        nets["TEMP_ALERT"],
        nets["BMI270_INT1"],
        nets["BMI270_INT2"],
        nets["SENSOR_ENABLE"],
        nets["HAPTIC_PWM"],
        nets["HAPTIC_ENABLE"],
        nets["STATUS_LED"],
        nets["RF_ENABLE"],
        nets["RF_IRQ"],
        nets["RF_SPI_SCK"],
        nets["RF_SPI_MOSI"],
        nets["RF_SPI_MISO"],
        nets["RF_SPI_CS"],
    )
    biosensor_front_end(
        nets["VDD_3V3"],
        nets["GND"],
        nets["I2C_SDA"],
        nets["I2C_SCL"],
        nets["TEMP_ALERT"],
        nets["BMI270_INT1"],
        nets["BMI270_INT2"],
    )
    haptic_output(
        nets["VBAT"],
        nets["GND"],
        nets["I2C_SDA"],
        nets["I2C_SCL"],
        nets["HAPTIC_PWM"],
        nets["HAPTIC_ENABLE"],
    )
    optional_ranging_connector(
        nets["VDD_1V8"],
        nets["VDD_3V3_RF_OPT"],
        nets["GND"],
        nets["I2C_SDA"],
        nets["I2C_SCL"],
        nets["RF_ENABLE"],
        nets["RF_IRQ"],
        nets["RF_SPI_SCK"],
        nets["RF_SPI_MOSI"],
        nets["RF_SPI_MISO"],
        nets["RF_SPI_CS"],
        nets["UART_TX"],
        nets["UART_RX"],
        nets["SWDIO"],
        nets["SWCLK"],
        nets["RESET_N"],
        nets["PMIC_INT"],
        nets["TEMP_ALERT"],
        nets["BMI270_INT1"],
        nets["BMI270_INT2"],
        nets["SENSOR_ENABLE"],
    )
    debug_and_test(
        nets["VDD_3V3"],
        nets["VDD_1V8"],
        nets["VDD_3V3_RF_OPT"],
        nets["VBAT"],
        nets["GND"],
        nets["SWDIO"],
        nets["SWCLK"],
        nets["RESET_N"],
        nets["UART_TX"],
        nets["UART_RX"],
        nets["I2C_SDA"],
        nets["I2C_SCL"],
        nets["PMIC_INT"],
    )

    generate_schematic(
        filepath=str(PROJECT_DIR),
        top_name=SCHEMATIC_NAME,
        title="ULP Wearable Module - Preliminary Architecture",
        flatness=0.0,
        auto_stub=True,
        # Stub nets with 4+ connections as labels (power buses, I2C, SPI).
        # 2–3-pin local nets remain as wires, giving readable local topology.
        # (The old value of 2 converted *everything* to labels.)
        auto_stub_fanout=4,
        # Post-placement: only route 2-pin nets as wires; stub anything longer
        # than 1500 mils so distant pairs don't block the router.
        auto_stub_max_wire_pins=2,
        auto_stub_max_wire_dist=1500,
        # Split placement groups more aggressively (default is 20).
        # Smaller groups are easier for the wire router; this was the main
        # reason routing failed after all retries — groups stayed at 23–35 parts.
        auto_stub_max_group=10,
        # More retry attempts with area expansion (was 1, which gave no recovery
        # path after the first routing failure).
        retries=4,
    )


if __name__ == "__main__":
    build_schematic()
