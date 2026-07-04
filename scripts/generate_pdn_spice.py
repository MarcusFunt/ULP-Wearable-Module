#!/usr/bin/env python3
"""Generate an early SPICE-style PDN model for the ULP Wearable Module.

This script is intentionally simple. It checks the current architecture for obvious
rail-budget and topology mistakes. It is not a final regulator stability model.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from skidl.pyspice import C, GND, I, R, V, ERC, Net, generate_netlist, reset

OUT = Path("build/pdn")


@dataclass(frozen=True)
class PulseLoad:
    name: str
    low_a: float
    high_a: float
    delay_s: float
    rise_s: float
    fall_s: float
    width_s: float
    period_s: float

    def current(self, t: np.ndarray) -> np.ndarray:
        cur = np.full_like(t, self.low_a, dtype=float)
        active = t >= self.delay_s
        x = (t[active] - self.delay_s) % self.period_s
        y = np.full_like(x, self.low_a, dtype=float)

        rising = (x >= 0) & (x < self.rise_s)
        if self.rise_s > 0:
            y[rising] = self.low_a + (self.high_a - self.low_a) * x[rising] / self.rise_s

        high = (x >= self.rise_s) & (x < self.rise_s + self.width_s)
        y[high] = self.high_a

        falling = (
            (x >= self.rise_s + self.width_s)
            & (x < self.rise_s + self.width_s + self.fall_s)
        )
        if self.fall_s > 0:
            y[falling] = self.high_a - (self.high_a - self.low_a) * (
                x[falling] - self.rise_s - self.width_s
            ) / self.fall_s

        cur[active] = y
        return cur

    def spice(self) -> str:
        def ts(value: float) -> str:
            if value >= 1e-3:
                return f"{value * 1e3:g}m"
            if value >= 1e-6:
                return f"{value * 1e6:g}u"
            return f"{value:g}"

        return (
            f"PULSE({self.low_a:g} {self.high_a:g} {ts(self.delay_s)} "
            f"{ts(self.rise_s)} {ts(self.fall_s)} {ts(self.width_s)} {ts(self.period_s)})"
        )


@dataclass(frozen=True)
class Rail:
    name: str
    nominal_v: float
    source_r_ohm: float
    source_limit_a: float
    min_ok_v: float
    caps_f: list[float]
    base_load_a: float
    pulse_loads: list[PulseLoad] = field(default_factory=list)
    note: str = ""

    @property
    def cap_total_f(self) -> float:
        return sum(self.caps_f)

    @property
    def peak_load_a(self) -> float:
        return self.base_load_a + sum(max(p.low_a, p.high_a) for p in self.pulse_loads)


RAILS = [
    Rail(
        name="VDD_1V8",
        nominal_v=1.8,
        source_r_ohm=0.08,
        source_limit_a=0.200,
        min_ok_v=1.70,
        caps_f=[22e-6, 100e-9],
        base_load_a=0.010,
        pulse_loads=[PulseLoad("I_NRF_RADIO", 0.0, 0.025, 2e-3, 20e-6, 20e-6, 1.5e-3, 8e-3)],
        note="nRF54L15-class SoC rail placeholder.",
    ),
    Rail(
        name="VDD_3V3_AFE",
        nominal_v=3.3,
        source_r_ohm=0.12,
        source_limit_a=0.200,
        min_ok_v=3.00,
        caps_f=[47e-6, 100e-9],
        base_load_a=0.008,
        pulse_loads=[PulseLoad("I_PPG_LED", 0.0, 0.090, 1e-3, 50e-6, 50e-6, 2e-3, 10e-3)],
        note="Biosensor/optical pulse rail placeholder.",
    ),
    Rail(
        name="VDD_3V3_UWB_OPT",
        nominal_v=3.3,
        source_r_ohm=0.08,
        source_limit_a=0.300,
        min_ok_v=3.00,
        caps_f=[47e-6, 100e-9],
        base_load_a=0.025,
        pulse_loads=[PulseLoad("I_UWB_TX_OPT", 0.0, 0.150, 4e-3, 100e-6, 100e-6, 3e-3, 12e-3)],
        note="Optional UWB/ranging rail placeholder; intentionally separate from AFE rail.",
    ),
]


def build_skidl_netlist() -> str:
    """Build a SKiDL circuit and return its generated SPICE-like netlist."""
    reset()
    gnd = GND

    bat_cell = Net("BAT_CELL")
    vbat_in = Net("VBAT_IN")
    V(ref="VBAT", dc_value=3.7)["p", "n"] += bat_cell, gnd
    R(ref="RBAT_ESR", value="0.15")["p", "n"] += bat_cell, vbat_in
    C(ref="CIN_PMID", value="10u")["p", "n"] += vbat_in, gnd
    I(ref="IPMIC_IN_STUB", dc_value=0.080)["p", "n"] += vbat_in, gnd

    for rail in RAILS:
        ideal = Net(f"{rail.name}_IDEAL")
        out = Net(rail.name)
        V(ref=f"VREG_{rail.name}", dc_value=rail.nominal_v)["p", "n"] += ideal, gnd
        R(ref=f"RSRC_{rail.name}", value=str(rail.source_r_ohm))["p", "n"] += ideal, out
        I(ref=f"IBASE_{rail.name}", dc_value=rail.base_load_a)["p", "n"] += out, gnd
        for i, cap in enumerate(rail.caps_f, start=1):
            C(ref=f"C{i}_{rail.name}", value=f"{cap:g}")["p", "n"] += out, gnd
        for pulse in rail.pulse_loads:
            # Represent pulse loads as DC high-current stubs for SKiDL ERC connectivity.
            # The exported hand-cleaned SPICE netlist below uses the actual PULSE() form.
            I(ref=pulse.name, dc_value=pulse.high_a)["p", "n"] += out, gnd

    ERC()
    return str(generate_netlist())


def cap_string(value_f: float) -> str:
    if value_f >= 1e-6:
        return f"{value_f * 1e6:g}u"
    return f"{value_f * 1e9:g}n"


def export_clean_spice() -> str:
    lines = [
        "* ULP Wearable Module early PDN model",
        "* Regulator outputs are simplified Thevenin equivalents.",
        "* Replace placeholder values with datasheet/measured values before PCB signoff.",
        "",
        "VBAT BAT_CELL 0 DC 3.7",
        "RBAT_ESR BAT_CELL VBAT_IN 0.15",
        "CIN_PMID VBAT_IN 0 10u",
        "IPMIC_IN_STUB VBAT_IN 0 DC 80m",
        "",
    ]

    for rail in RAILS:
        lines.extend(
            [
                f"* {rail.name}: {rail.note}",
                f"VREG_{rail.name} {rail.name}_IDEAL 0 DC {rail.nominal_v:g}",
                f"RSRC_{rail.name} {rail.name}_IDEAL {rail.name} {rail.source_r_ohm:g}",
                f"IBASE_{rail.name} {rail.name} 0 DC {rail.base_load_a:g}",
            ]
        )
        for i, cap in enumerate(rail.caps_f, start=1):
            lines.append(f"C{i}_{rail.name} {rail.name} 0 {cap_string(cap)}")
        for pulse in rail.pulse_loads:
            lines.append(f"{pulse.name} {rail.name} 0 {pulse.spice()}")
        lines.append("")

    lines.extend(
        [
            ".tran 1u 20m 0 1u",
            ".control",
            "run",
            "plot v(VDD_1V8) v(VDD_3V3_AFE) v(VDD_3V3_UWB_OPT)",
            ".endc",
            ".end",
            "",
        ]
    )
    return "\n".join(lines)


def simulate_rail(rail: Rail, t_end_s: float = 20e-3, dt_s: float = 1e-6) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    t = np.arange(0, t_end_s + dt_s, dt_s)
    load = np.full_like(t, rail.base_load_a, dtype=float)
    for pulse in rail.pulse_loads:
        load += pulse.current(t)

    v = np.empty_like(t)
    v[0] = rail.nominal_v - rail.source_r_ohm * load[0]
    for idx in range(1, len(t)):
        dvdt = ((rail.nominal_v - v[idx - 1]) / rail.source_r_ohm - load[idx - 1]) / rail.cap_total_f
        v[idx] = v[idx - 1] + dvdt * dt_s
    return t, v, load


def validate() -> list[str]:
    errors: list[str] = []
    for rail in RAILS:
        if rail.peak_load_a > rail.source_limit_a:
            errors.append(
                f"{rail.name}: peak load {rail.peak_load_a * 1e3:.1f} mA exceeds "
                f"limit {rail.source_limit_a * 1e3:.1f} mA"
            )
        if rail.cap_total_f <= 0:
            errors.append(f"{rail.name}: no output capacitance")
    return errors


def write_plot() -> dict[str, dict[str, float | bool]]:
    results: dict[str, dict[str, float | bool]] = {}
    plt.figure(figsize=(10, 5.5), dpi=150)
    for rail in RAILS:
        t, v, load = simulate_rail(rail)
        droop_mv = (rail.nominal_v - v) * 1e3
        plt.plot(t * 1e3, droop_mv, label=rail.name)
        results[rail.name] = {
            "peak_load_ma": float(load.max() * 1e3),
            "limit_ma": float(rail.source_limit_a * 1e3),
            "min_v": float(v.min()),
            "max_droop_mv": float(droop_mv.max()),
            "pass": bool(v.min() >= rail.min_ok_v and load.max() <= rail.source_limit_a),
        }

    plt.title("Early PDN droop estimate")
    plt.xlabel("Time (ms)")
    plt.ylabel("Droop from nominal (mV)")
    plt.grid(True, alpha=0.35)
    plt.legend(loc="best")
    plt.tight_layout()
    plt.savefig(OUT / "wearable_pdn_transient.png")
    plt.close()
    return results


def write_summary(results: dict[str, dict[str, float | bool]], errors: list[str]) -> None:
    lines = [
        "# PDN generation summary",
        "",
        "This is an early architecture model, not final regulator signoff.",
        "",
        "## Rail results",
        "",
        "| Rail | Peak load | Limit | Min V | Max droop | Result |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for rail, result in results.items():
        lines.append(
            f"| {rail} | {result['peak_load_ma']:.1f} mA | {result['limit_ma']:.0f} mA | "
            f"{result['min_v']:.4f} V | {result['max_droop_mv']:.2f} mV | "
            f"{'PASS' if result['pass'] else 'FAIL'} |"
        )

    lines.extend(["", "## Validation", ""])
    if errors:
        lines.extend(f"- ERROR: {error}" for error in errors)
    else:
        lines.append("- No blocking current-budget errors in the placeholder model.")

    lines.extend(
        [
            "",
            "## Important caveats",
            "",
            "- Real PMIC control-loop behavior is not modelled.",
            "- Inductor saturation is not modelled.",
            "- PCB parasitics are not modelled.",
            "- Replace placeholder currents with real datasheet/measured values.",
        ]
    )
    (OUT / "wearable_pdn_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    skidl_netlist = build_skidl_netlist()
    (OUT / "wearable_pdn_skidl_generated.cir").write_text(skidl_netlist, encoding="utf-8")
    (OUT / "wearable_pdn_final.cir").write_text(export_clean_spice(), encoding="utf-8")
    errors = validate()
    results = write_plot()
    write_summary(results, errors)

    print(f"Wrote outputs to {OUT}")
    for rail, result in results.items():
        print(
            f"{rail}: peak={result['peak_load_ma']:.1f} mA, "
            f"min={result['min_v']:.4f} V, droop={result['max_droop_mv']:.2f} mV, "
            f"result={'PASS' if result['pass'] else 'FAIL'}"
        )
    if errors:
        print("Errors:")
        for error in errors:
            print(f"- {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
