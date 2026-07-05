from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import render_esch as renderer


def write_records(path: Path, records: list[list[object]]) -> None:
    path.write_text("\n".join(json.dumps(record) for record in records) + "\n", encoding="utf-8")


def sample_records() -> list[list[object]]:
    return [
        ["DOCTYPE", "SCH", "1.1"],
        ["HEAD", {"originX": 0, "originY": 806, "version": "2"}],
        ["COMPONENT", "page", "A_A4.1", 0, 806, 0, 0, {}, 0],
        ["ATTR", "a1", "page", "@Project Name", "Test Project", None, 1, 700, 40],
        ["ATTR", "a2", "page", "Date", "2026-07-05", None, 1, 850, 15],
        ["COMPONENT", "u1", "TEST-IC.1", 300, 400, 0, 0, {}, 0],
        ["ATTR", "a3", "u1", "Designator", "U1", None, 1, 300, 450],
        ["ATTR", "a4", "u1", "spiceSymbolName", "TEST-IC", 0, 0, 300, 400],
        ["ATTR", "a5", "u1", "Origin Footprint", "QFN-32", 0, 0, 300, 400],
        ["FONTSTYLE", "st1", None],
    ]


def test_load_esch_parses_components_and_attributes(tmp_path: Path) -> None:
    source = tmp_path / "test.esch"
    write_records(source, sample_records())

    document = renderer.load_esch(source)

    assert document.version == "1.1"
    assert document.origin_y == 806
    assert len(document.components) == 2
    assert len(document.placed_components) == 1
    assert document.sheet_component is not None
    assert document.sheet_component.attribute("@Project Name") == "Test Project"
    assert document.placed_components[0].designator == "U1"
    assert document.placed_components[0].part_name == "TEST-IC"
    assert document.record_counts["ATTR"] == 5


def test_load_esch_reports_invalid_json_with_line_number(tmp_path: Path) -> None:
    source = tmp_path / "broken.esch"
    source.write_text('["DOCTYPE","SCH","1.1"]\nnot-json\n', encoding="utf-8")

    with pytest.raises(ValueError, match=r"broken\.esch:2: invalid JSON"):
        renderer.load_esch(source)


def test_load_esch_rejects_non_schematic_documents(tmp_path: Path) -> None:
    source = tmp_path / "board.esch"
    write_records(source, [["DOCTYPE", "PCB", "1.1"]])

    with pytest.raises(ValueError, match="missing DOCTYPE SCH"):
        renderer.load_esch(source)


def test_render_esch_writes_png_and_svg(tmp_path: Path) -> None:
    source = tmp_path / "test.esch"
    write_records(source, sample_records())
    document = renderer.load_esch(source)

    png = renderer.render_esch(document, tmp_path / "test.png", dpi=100)
    svg = renderer.render_esch(document, tmp_path / "test.svg")

    assert png.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
    assert png.stat().st_size > 5_000
    assert "<svg" in svg.read_text(encoding="utf-8")[:1_000]


def test_render_esch_rejects_unknown_output_format(tmp_path: Path) -> None:
    source = tmp_path / "test.esch"
    write_records(source, sample_records())
    document = renderer.load_esch(source)

    with pytest.raises(ValueError, match="Unsupported output format"):
        renderer.render_esch(document, tmp_path / "test.jpg")


def test_main_uses_png_next_to_input_by_default(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    source = tmp_path / "test.esch"
    write_records(source, sample_records())

    assert renderer.main([str(source), "--dpi", "100"]) == 0
    assert source.with_suffix(".png").exists()
    assert "Rendered 1 components" in capsys.readouterr().out
