#!/usr/bin/env python3
"""Render an EasyEDA Pro ``.esch`` file as a placement overview image.

EasyEDA Pro schematic files are JSON-lines documents.  A standalone ``.esch``
stores component instances and their attributes, while the native symbol artwork
normally lives in separate ``.esym`` library files.  This renderer therefore
draws components as labelled schematic blocks at their recorded coordinates.

Usage::

    python scripts/render_esch.py Sheet_1.esch -o Sheet_1.png

PNG, SVG, and PDF outputs are supported through Matplotlib.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from matplotlib.patches import Circle, Rectangle

SUPPORTED_OUTPUT_SUFFIXES = {".pdf", ".png", ".svg"}
SHEET_PREFIXES = ("A_A0", "A_A1", "A_A2", "A_A3", "A_A4", "A_A5")


@dataclass(frozen=True)
class EschAttribute:
    """One EasyEDA ``ATTR`` record."""

    name: str
    value: str | None
    x: float | None = None
    y: float | None = None
    visible: bool = False


@dataclass
class EschComponent:
    """A placed component and the attributes that refer to it."""

    record_id: str
    library_name: str
    x: float
    y: float
    rotation: float = 0.0
    mirrored: bool = False
    attributes: dict[str, EschAttribute] = field(default_factory=dict)

    def attribute(self, name: str) -> str | None:
        attribute = self.attributes.get(name)
        return attribute.value if attribute else None

    @property
    def designator(self) -> str:
        return self.attribute("Designator") or "?"

    @property
    def part_name(self) -> str:
        return (
            self.attribute("spiceSymbolName")
            or self.attribute("Name")
            or re.sub(r"\.\d+$", "", self.library_name)
        )

    @property
    def is_sheet_frame(self) -> bool:
        name = self.library_name.upper()
        return name.startswith(SHEET_PREFIXES) or "@Project Name" in self.attributes


@dataclass
class EschDocument:
    """Parsed subset of an EasyEDA Pro schematic document."""

    version: str
    origin_x: float
    origin_y: float
    components: list[EschComponent]
    record_counts: dict[str, int]

    @property
    def placed_components(self) -> list[EschComponent]:
        return [component for component in self.components if not component.is_sheet_frame]

    @property
    def sheet_component(self) -> EschComponent | None:
        return next((component for component in self.components if component.is_sheet_frame), None)


def _optional_number(record: list[Any], index: int) -> float | None:
    if index >= len(record):
        return None
    value = record[index]
    if isinstance(value, bool) or not isinstance(value, int | float):
        return None
    return float(value)


def load_esch(path: str | Path) -> EschDocument:
    """Parse the line-delimited JSON records in an EasyEDA Pro schematic."""
    source = Path(path)
    records: list[tuple[int, list[Any]]] = []

    try:
        lines = source.read_text(encoding="utf-8-sig").splitlines()
    except OSError as error:
        raise ValueError(f"Cannot read {source}: {error}") from error

    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(f"{source}:{line_number}: invalid JSON: {error.msg}") from error
        if not isinstance(record, list) or not record or not isinstance(record[0], str):
            raise ValueError(f"{source}:{line_number}: expected a JSON record array")
        records.append((line_number, record))

    if not records or records[0][1][:2] != ["DOCTYPE", "SCH"]:
        raise ValueError(f"{source}: not an EasyEDA Pro schematic (missing DOCTYPE SCH)")

    doctype = records[0][1]
    version = str(doctype[2]) if len(doctype) > 2 else "unknown"
    origin_x = 0.0
    origin_y = 806.0
    components_by_id: dict[str, EschComponent] = {}
    pending_attributes: list[tuple[str, EschAttribute]] = []
    record_counts: dict[str, int] = {}

    for line_number, record in records:
        record_type = record[0]
        record_counts[record_type] = record_counts.get(record_type, 0) + 1

        if record_type == "HEAD" and len(record) > 1 and isinstance(record[1], dict):
            head = record[1]
            origin_x = float(head.get("originX", origin_x))
            origin_y = float(head.get("originY", origin_y))
        elif record_type == "COMPONENT":
            if len(record) < 5:
                raise ValueError(f"{source}:{line_number}: truncated COMPONENT record")
            try:
                component = EschComponent(
                    record_id=str(record[1]),
                    library_name=str(record[2]),
                    x=float(record[3]),
                    y=float(record[4]),
                    rotation=float(record[5]) if len(record) > 5 else 0.0,
                    mirrored=bool(record[6]) if len(record) > 6 else False,
                )
            except (TypeError, ValueError) as error:
                raise ValueError(
                    f"{source}:{line_number}: invalid COMPONENT coordinates"
                ) from error
            components_by_id[component.record_id] = component
        elif record_type == "ATTR":
            if len(record) < 5:
                raise ValueError(f"{source}:{line_number}: truncated ATTR record")
            value = None if record[4] is None else str(record[4])
            pending_attributes.append(
                (
                    str(record[2]),
                    EschAttribute(
                        name=str(record[3]),
                        value=value,
                        x=_optional_number(record, 7),
                        y=_optional_number(record, 8),
                        visible=bool(record[6]) if len(record) > 6 else False,
                    ),
                )
            )

    for parent_id, attribute in pending_attributes:
        component = components_by_id.get(parent_id)
        if component is not None:
            component.attributes[attribute.name] = attribute

    return EschDocument(
        version=version,
        origin_x=origin_x,
        origin_y=origin_y,
        components=list(components_by_id.values()),
        record_counts=record_counts,
    )


# Designator prefixes → typical pin counts for schematic rendering.
# These take priority over the footprint-name regex for well-known passives
# and discretes, avoiding false matches like "0402" → 4 or "SOT-23" → 23.
_DESIGNATOR_PIN_HINTS: dict[str, int] = {
    "C": 2, "R": 2, "L": 2, "D": 2, "F": 2, "TP": 1,
    "Q": 3, "Y": 4, "SW": 2, "AE": 2,
}


def _footprint_pin_count(component: EschComponent) -> int:
    """Estimate pin count for component sizing.

    Checks the designator prefix first for well-known passives and discretes,
    then falls back to extracting a count from the Origin Footprint attribute
    (e.g. "-49N" → 49, "-32-" → 32).
    """
    # 1. Designator-prefix heuristic: passives/discretes don't encode pin
    #    count reliably in their footprint name (e.g. "C_0402" → 4 is wrong).
    prefix_match = re.match(r"^([A-Za-z]+)", component.designator)
    if prefix_match:
        prefix = prefix_match.group(1).upper()
        if prefix in _DESIGNATOR_PIN_HINTS:
            return _DESIGNATOR_PIN_HINTS[prefix]

    # 2. For ICs and other multi-pin parts, extract count from footprint name.
    footprint = component.attribute("Origin Footprint") or ""
    match = re.search(r"(?:^|[-_])(\d{1,3})(?:[^0-9]|$)", footprint)
    if match:
        return max(2, min(int(match.group(1)), 64))

    return 8


def _component_size(component: EschComponent) -> tuple[float, float]:
    pin_count = _footprint_pin_count(component)
    width = min(165.0, 76.0 + pin_count * 1.6)
    height = min(120.0, 48.0 + pin_count * 1.05)
    return width, height


def _draw_pins(axis: Any, x: float, y: float, width: float, height: float, count: int) -> None:
    count = min(count, 48)
    side_counts = [count // 4] * 4
    for index in range(count % 4):
        side_counts[index] += 1

    color = "#A63D40"
    length = 7.0
    for side, side_count in enumerate(side_counts):
        for index in range(side_count):
            fraction = (index + 1) / (side_count + 1)
            if side == 0:
                px, py = x - width / 2, y - height / 2 + fraction * height
                axis.plot([px - length, px], [py, py], color=color, linewidth=0.65)
            elif side == 1:
                px, py = x + width / 2, y - height / 2 + fraction * height
                axis.plot([px, px + length], [py, py], color=color, linewidth=0.65)
            elif side == 2:
                px, py = x - width / 2 + fraction * width, y + height / 2
                axis.plot([px, px], [py, py + length], color=color, linewidth=0.65)
            else:
                px, py = x - width / 2 + fraction * width, y - height / 2
                axis.plot([px, px], [py - length, py], color=color, linewidth=0.65)
            axis.add_patch(Circle((px, py), radius=0.8, color=color, linewidth=0))


def _sheet_dimensions(document: EschDocument) -> tuple[float, float]:
    page_height = max(document.origin_y, 200.0)
    coordinate_values = [
        coordinate
        for component in document.components
        for attribute in component.attributes.values()
        for coordinate in (attribute.x,)
        if coordinate is not None
    ]
    component_x = [component.x for component in document.components]
    rightmost = max([*coordinate_values, *component_x], default=0.0)
    page_width = max(page_height * math.sqrt(2), rightmost + 20.0)
    return page_width, page_height


def _draw_title_block(axis: Any, document: EschDocument, width: float) -> None:
    sheet = document.sheet_component
    attributes = sheet.attributes if sheet else {}

    def value(name: str, default: str = "") -> str:
        attribute = attributes.get(name)
        return attribute.value if attribute and attribute.value is not None else default

    block_width = min(390.0, width * 0.36)
    block_height = 62.0
    left = width - block_width - 10.0
    bottom = 10.0
    axis.add_patch(
        Rectangle(
            (left, bottom),
            block_width,
            block_height,
            fill=False,
            edgecolor="#23262B",
            linewidth=0.8,
        )
    )
    axis.plot(
        [left, width - 10.0],
        [bottom + 28.0, bottom + 28.0],
        color="#23262B",
        linewidth=0.55,
    )
    axis.plot(
        [left + block_width * 0.68, left + block_width * 0.68],
        [bottom, bottom + 28.0],
        color="#23262B",
        linewidth=0.55,
    )
    axis.text(
        left + 7.0,
        bottom + 43.0,
        value("@Project Name", value("@Schematic Name", "EasyEDA schematic")),
        fontsize=7.2,
        fontweight="bold",
        color="#17191C",
        va="center",
    )
    axis.text(
        left + 7.0,
        bottom + 14.0,
        f"Sheet: {value('@Page Name', '1')}   Rev: {value('REV', '-')}   "
        f"Date: {value('Date', '-')}",
        fontsize=5.2,
        color="#34383D",
        va="center",
    )
    axis.text(
        left + block_width * 0.70,
        bottom + 14.0,
        f"Drawn by\n{value('Draw By', '-')}",
        fontsize=5.0,
        color="#34383D",
        va="center",
    )


def render_esch(
    document: EschDocument,
    output_path: str | Path,
    *,
    dpi: int = 180,
    background: str = "#FBFAF7",
) -> Path:
    """Render a parsed schematic to PNG, SVG, or PDF and return its path."""
    output = Path(output_path)
    suffix = output.suffix.lower()
    if suffix not in SUPPORTED_OUTPUT_SUFFIXES:
        choices = ", ".join(sorted(SUPPORTED_OUTPUT_SUFFIXES))
        raise ValueError(f"Unsupported output format {suffix!r}; choose one of: {choices}")
    if dpi <= 0:
        raise ValueError("dpi must be positive")

    width, height = _sheet_dimensions(document)
    pixel_width = 2000
    pixel_height = max(900, round(pixel_width * height / width))
    figure = Figure(
        figsize=(pixel_width / dpi, pixel_height / dpi),
        dpi=dpi,
        facecolor=background,
    )
    FigureCanvasAgg(figure)
    axis = figure.add_axes((0.015, 0.02, 0.97, 0.96))
    axis.set_xlim(0.0, width)
    axis.set_ylim(0.0, height)
    axis.set_aspect("equal", adjustable="box")
    axis.axis("off")
    axis.add_patch(
        Rectangle(
            (10.0, 10.0),
            width - 20.0,
            height - 20.0,
            fill=False,
            edgecolor="#34383D",
            linewidth=0.85,
        )
    )

    for component in document.placed_components:
        component_width, component_height = _component_size(component)
        axis.add_patch(
            Rectangle(
                (component.x - component_width / 2, component.y - component_height / 2),
                component_width,
                component_height,
                facecolor="#FFFDF6",
                edgecolor="#2D5F73",
                linewidth=1.05,
                zorder=2,
            )
        )
        _draw_pins(
            axis,
            component.x,
            component.y,
            component_width,
            component_height,
            _footprint_pin_count(component),
        )
        axis.text(
            component.x,
            component.y + 7.0,
            component.designator,
            ha="center",
            va="center",
            fontsize=7.2,
            fontweight="bold",
            color="#183642",
            zorder=3,
        )
        axis.text(
            component.x,
            component.y - 9.0,
            component.part_name,
            ha="center",
            va="center",
            fontsize=5.5,
            color="#34383D",
            zorder=3,
        )

    _draw_title_block(axis, document, width)
    axis.text(
        18.0,
        20.0,
        "Placement overview — external .esym artwork is not embedded in this .esch file",
        fontsize=4.7,
        color="#6E747A",
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=dpi, facecolor=background, format=suffix[1:])
    return output


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Render an EasyEDA Pro .esch schematic as a labelled placement image."
    )
    parser.add_argument("input", type=Path, help="input .esch file")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="output .png, .svg, or .pdf path (default: INPUT.png)",
    )
    parser.add_argument("--dpi", type=int, default=180, help="raster output DPI (default: 180)")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    output = args.output or args.input.with_suffix(".png")
    try:
        document = load_esch(args.input)
        render_esch(document, output, dpi=args.dpi)
    except ValueError as error:
        raise SystemExit(str(error)) from error

    supported_records = {"ATTR", "COMPONENT", "DOCTYPE", "FONTSTYLE", "HEAD"}
    unsupported = sorted(set(document.record_counts) - supported_records)
    print(f"Rendered {len(document.placed_components)} components to {output}")
    if unsupported:
        print(f"Note: unsupported records were ignored: {', '.join(unsupported)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
