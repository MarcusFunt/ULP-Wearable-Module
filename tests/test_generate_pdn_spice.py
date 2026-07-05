from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from scripts import generate_pdn_spice as pdn


def make_rail(**overrides: object) -> pdn.Rail:
    values: dict[str, object] = {
        "name": "TEST_RAIL",
        "nominal_v": 3.3,
        "source_r_ohm": 1.0,
        "source_limit_a": 2.0,
        "min_ok_v": 2.0,
        "caps_f": [1.0],
        "base_load_a": 0.0,
    }
    values.update(overrides)
    return pdn.Rail(**values)


def test_pulse_load_current_models_each_phase_and_repeats() -> None:
    pulse = pdn.PulseLoad(
        "TEST_LOAD",
        low_a=0.1,
        high_a=0.5,
        delay_s=1.0,
        rise_s=1.0,
        fall_s=1.0,
        width_s=1.0,
        period_s=5.0,
    )
    times = np.array([0.0, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 6.0, 6.5])

    currents = pulse.current(times)

    np.testing.assert_allclose(currents, [0.1, 0.1, 0.3, 0.5, 0.5, 0.5, 0.3, 0.1, 0.1, 0.3])


def test_pulse_load_spice_uses_ngspice_time_suffixes() -> None:
    pulse = pdn.PulseLoad("LOAD", 0.0, 0.1, 2e-3, 20e-6, 30e-6, 1e-3, 8e-3)

    assert pulse.spice() == "PULSE(0 0.1 2m 20u 30u 1m 8m)"


@pytest.mark.parametrize(("value_f", "expected"), [(47e-6, "47u"), (100e-9, "100n")])
def test_cap_string(value_f: float, expected: str) -> None:
    assert pdn.cap_string(value_f) == expected


def test_export_clean_spice_contains_every_rail_and_terminates() -> None:
    netlist = pdn.export_clean_spice()

    for rail in pdn.RAILS:
        assert f"VREG_{rail.name}" in netlist
        assert f"RSRC_{rail.name}" in netlist
    assert ".tran 1u 20m 0 1u" in netlist
    assert netlist.endswith(".end\n")


def test_build_skidl_netlist_does_not_write_implicit_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    netlist = pdn.build_skidl_netlist()

    assert "VREG_VDD_1V8" in netlist
    assert list(tmp_path.iterdir()) == []


def test_simulate_rail_uses_stable_rc_solution_for_coarse_steps() -> None:
    pulse = pdn.PulseLoad("LOAD", 0.0, 1.0, 1.0, 0.0, 0.0, 20.0, 100.0)
    rail = make_rail(pulse_loads=[pulse])

    _, voltage, _ = pdn.simulate_rail(rail, t_end_s=6.0, dt_s=3.0)

    # With the off-by-one fix (load[idx] not load[idx-1]), the step at idx=1
    # already uses the active load so both steps use v_ss=2.3.  After two
    # RC-decay steps of dt=3 s with RC=1 s: 2.3 + exp(-3)*exp(-3) = 2.3+exp(-6).
    expected_after_three_seconds = 2.3 + np.exp(-6.0)
    assert voltage[-1] == pytest.approx(expected_after_three_seconds)
    assert voltage.min() >= 2.3


@pytest.mark.parametrize(
    ("rail", "t_end_s", "dt_s", "message"),
    [
        (make_rail(), 1.0, 0.0, "dt_s must be positive"),
        (make_rail(), -1.0, 1.0, "t_end_s must be non-negative"),
        (make_rail(source_r_ohm=0.0), 1.0, 1.0, "source resistance must be positive"),
        (make_rail(caps_f=[]), 1.0, 1.0, "output capacitance must be positive"),
    ],
)
def test_simulate_rail_rejects_invalid_inputs(
    rail: pdn.Rail, t_end_s: float, dt_s: float, message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        pdn.simulate_rail(rail, t_end_s=t_end_s, dt_s=dt_s)


def test_validate_reports_overload_and_missing_capacitance(monkeypatch: pytest.MonkeyPatch) -> None:
    invalid = make_rail(source_limit_a=0.5, base_load_a=0.6, caps_f=[])
    monkeypatch.setattr(pdn, "RAILS", [invalid])

    assert pdn.validate() == [
        "TEST_RAIL: peak load 600.0 mA exceeds limit 500.0 mA",
        "TEST_RAIL: no output capacitance",
    ]


def test_write_summary_records_failures(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(pdn, "OUT", tmp_path)
    results = {
        "TEST_RAIL": {
            "peak_load_ma": 600.0,
            "limit_ma": 500.0,
            "min_v": 1.9,
            "max_droop_mv": 1400.0,
            "pass": False,
        }
    }

    pdn.write_summary(results, ["TEST_RAIL: overloaded"])

    summary = (tmp_path / "wearable_pdn_summary.md").read_text(encoding="utf-8")
    assert "| TEST_RAIL | 600.0 mA | 500 mA | 1.9000 V | 1400.00 mV | FAIL |" in summary
    assert "- ERROR: TEST_RAIL: overloaded" in summary


def test_main_returns_failure_when_a_simulated_rail_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(pdn, "OUT", tmp_path)
    monkeypatch.setattr(pdn, "build_skidl_netlist", lambda: "generated")
    monkeypatch.setattr(pdn, "export_clean_spice", lambda: "clean")
    monkeypatch.setattr(pdn, "validate", lambda: [])
    monkeypatch.setattr(
        pdn,
        "write_plot",
        lambda: {
            "TEST_RAIL": {
                "peak_load_ma": 100.0,
                "limit_ma": 200.0,
                "min_v": 1.5,
                "max_droop_mv": 300.0,
                "pass": False,
            }
        },
    )

    assert pdn.main() == 1
    assert "Failed rails: TEST_RAIL" in capsys.readouterr().out


def test_main_writes_outputs_and_returns_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(pdn, "OUT", tmp_path)
    monkeypatch.setattr(pdn, "build_skidl_netlist", lambda: "generated")
    monkeypatch.setattr(pdn, "export_clean_spice", lambda: "clean")
    monkeypatch.setattr(pdn, "validate", lambda: [])
    monkeypatch.setattr(
        pdn,
        "write_plot",
        lambda: {
            "TEST_RAIL": {
                "peak_load_ma": 100.0,
                "limit_ma": 200.0,
                "min_v": 3.2,
                "max_droop_mv": 100.0,
                "pass": True,
            }
        },
    )

    assert pdn.main() == 0
    assert (tmp_path / "wearable_pdn_skidl_generated.cir").read_text() == "generated"
    assert (tmp_path / "wearable_pdn_final.cir").read_text() == "clean"
