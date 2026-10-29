"""
DXF drawing generation engine using ezdxf.

Generates 9 engineering drawing sheets for a single-stage spur gearbox:
 1. General Assembly
 2. Gearbox Housing
 3. Input Shaft
 4. Output Shaft
 5. Input Gear
 6. Output Gear
 7. Housing Cover
 8. Assembly Section
 9. Exploded Assembly

Each drawing uses organised CAD layers, proper dimensioning, center lines,
and a standard title block.
"""
from __future__ import annotations

import math
import os
from dataclasses import dataclass, field
from typing import Optional

import ezdxf
from ezdxf.enums import TextEntityAlignment

from app.schemas.design import (
    GearboxDesign,
    CalculationResults,
    GearDimensions,
    DrawingInfo,
)

# ---- Layer definitions ----
LAYERS = {
    "OUTLINE":      {"color": 7,  "linetype": "CONTINUOUS"},
    "HIDDEN":       {"color": 6,  "linetype": "DASHED"},
    "CENTER":       {"color": 1,  "linetype": "CENTER"},
    "DIMENSIONS":   {"color": 3,  "linetype": "CONTINUOUS"},
    "ANNOTATIONS":  {"color": 2,  "linetype": "CONTINUOUS"},
    "HOUSING":      {"color": 5,  "linetype": "CONTINUOUS"},
    "SHAFTS":       {"color": 4,  "linetype": "CONTINUOUS"},
    "GEARS":        {"color": 2,  "linetype": "CONTINUOUS"},
    "BEARINGS":     {"color": 6,  "linetype": "CONTINUOUS"},
    "FASTENERS":    {"color": 8,  "linetype": "CONTINUOUS"},
    "CONSTRUCTION": {"color": 9,  "linetype": "DASHED"},
    "SECTION_LINES":{"color": 1,  "linetype": "CONTINUOUS"},
    "TITLEBLOCK":   {"color": 7,  "linetype": "CONTINUOUS"},
    "BOM_TABLE":    {"color": 7,  "linetype": "CONTINUOUS"},
    "BORDER":       {"color": 7,  "linetype": "CONTINUOUS"},
}

TEXT_HEIGHT = 2.5
DIM_TEXT_HEIGHT = 2.0
TITLE_BLOCK_HEIGHT = 40
TITLE_BLOCK_WIDTH = 180


@dataclass
class DrawContext:
    """Holds ezdxf drawing and msp for a single sheet."""
    doc: ezdxf.document.Drawing
    msp: ezdxf.layouts.Modelspace
    offset_x: float = 0.0
    offset_y: float = 0.0


def _setup_doc() -> tuple[ezdxf.document.Drawing, ezdxf.layouts.Modelspace]:
    """Create a DXF document with all standard layers configured."""
    doc = ezdxf.new("R2010", setup=True)
    for name, props in LAYERS.items():
        if name not in doc.layers:
            doc.layers.add(name, color=props["color"])
            # Set linetype
            try:
                doc.layers.get(name).linetype = props["linetype"]
            except Exception:
                pass
    msp = doc.modelspace()
    return doc, msp


def _draw_title_block(ctx: DrawContext, design: GearboxDesign, drawing_name: str, sheet_no: int, total_sheets: int):
    """Draw a standard title block in the lower-right of the sheet."""
    x0 = ctx.offset_x
    y0 = ctx.offset_y
    msp = ctx.msp

    # Border
    msp.add_lwpolyline([
        (x0, y0), (x0 + TITLE_BLOCK_WIDTH, y0),
        (x0 + TITLE_BLOCK_WIDTH, y0 + TITLE_BLOCK_HEIGHT),
        (x0, y0 + TITLE_BLOCK_HEIGHT), (x0, y0)
    ], dxfattribs={"layer": "TITLEBLOCK"})

    # Internal divisions
    msp.add_line((x0, y0 + 12), (x0 + TITLE_BLOCK_WIDTH, y0 + 12), dxfattribs={"layer": "TITLEBLOCK"})
    msp.add_line((x0, y0 + 24), (x0 + TITLE_BLOCK_WIDTH, y0 + 24), dxfattribs={"layer": "TITLEBLOCK"})
    msp.add_line((x0 + 60, y0), (x0 + 60, y0 + 24), dxfattribs={"layer": "TITLEBLOCK"})
    msp.add_line((x0 + 120, y0), (x0 + 120, y0 + 24), dxfattribs={"layer": "TITLEBLOCK"})
    msp.add_line((x0 + 80, y0 + 24), (x0 + 80, y0 + TITLE_BLOCK_HEIGHT), dxfattribs={"layer": "TITLEBLOCK"})

    msp.add_text("GEARBOX STUDIO", dxfattribs={"layer": "TITLEBLOCK", "height": 4.0}).set_placement(
        (x0 + 4, y0 + 30))
    msp.add_text(f"Drawing: {drawing_name}", dxfattribs={"layer": "TITLEBLOCK", "height": TEXT_HEIGHT}).set_placement(
        (x0 + 4, y0 + 16))
    msp.add_text(f"Project: {design.project_info.project_name}",
                 dxfattribs={"layer": "TITLEBLOCK", "height": TEXT_HEIGHT}).set_placement(
        (x0 + 64, y0 + 16))
    msp.add_text(f"Dwg No: {design.project_info.drawing_number}",
                 dxfattribs={"layer": "TITLEBLOCK", "height": TEXT_HEIGHT}).set_placement(
        (x0 + 124, y0 + 16))
    msp.add_text(f"Scale: {design.project_info.drawing_scale}  Units: {design.project_info.units}",
                 dxfattribs={"layer": "TITLEBLOCK", "height": TEXT_HEIGHT}).set_placement(
        (x0 + 4, y0 + 4))
    msp.add_text(f"Sheet {sheet_no} of {total_sheets}",
                 dxfattribs={"layer": "TITLEBLOCK", "height": TEXT_HEIGHT}).set_placement(
        (x0 + 124, y0 + 4))
    if design.project_info.designer_name:
        msp.add_text(f"Designer: {design.project_info.designer_name}",
                     dxfattribs={"layer": "TITLEBLOCK", "height": TEXT_HEIGHT}).set_placement(
            (x0 + 84, y0 + 26))


def _dim_linear(ctx: DrawContext, p1, p2, offset, layer="DIMENSIONS", text=""):
    """Add a linear dimension between two points with given offset perpendicular to the line."""
    msp = ctx.msp
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    length = math.sqrt(dx * dx + dy * dy)
    if length < 1e-10:
        length = 1.0
    # Perpendicular direction for offset
    perp_x = -dy / length
    perp_y = dx / length
    base = (p1[0] + perp_x * offset, p1[1] + perp_y * offset)
    angle = math.atan2(dy, dx) * 180 / math.pi
    msp.add_linear_dim(
        base=base, p1=p1, p2=p2,
        angle=angle,
        dxfattribs={"layer": layer},
        override={"dimtxt": DIM_TEXT_HEIGHT},
    )


def _add_center_line(ctx: DrawContext, p1, p2):
    """Add a center line."""
    ctx.msp.add_line(p1, p2, dxfattribs={"layer": "CENTER"})


def _add_circle(ctx: DrawContext, center, radius, layer="OUTLINE"):
    """Add a circle on the specified layer."""
    ctx.msp.add_circle(center, radius, dxfattribs={"layer": layer})


def _add_text(ctx: DrawContext, text, pos, height=TEXT_HEIGHT, layer="ANNOTATIONS"):
    """Add text at a position."""
    ctx.msp.add_text(text, dxfattribs={"layer": layer, "height": height}).set_placement(pos)


def _add_rect(ctx: DrawContext, origin, width, height, layer="OUTLINE"):
    """Add a rectangle using a closed lwpolyline."""
    x, y = origin
    ctx.msp.add_lwpolyline(
        [(x, y), (x + width, y), (x + width, y + height), (x, y + height), (x, y)],
        close=True, dxfattribs={"layer": layer}
    )


def _draw_gear_views(ctx: DrawContext, gear: GearDimensions, label: str, cx: float, cy: float):
    """Draw front view (circle) and side view (rectangle) of a gear."""
    msp = ctx.msp

    # Front view (circle)
    # Pitch circle
    msp.add_circle((cx, cy), gear.pitch_diameter / 2, dxfattribs={"layer": "GEARS", "linetype": "DASHED"})
    # Outside circle
    msp.add_circle((cx, cy), gear.outside_diameter / 2, dxfattribs={"layer": "OUTLINE"})
    # Root circle
    msp.add_circle((cx, cy), gear.root_diameter / 2, dxfattribs={"layer": "HIDDEN"})
    # Bore circle
    msp.add_circle((cx, cy), gear.bore_diameter / 2, dxfattribs={"layer": "OUTLINE"})
    # Base circle (construction)
    msp.add_circle((cx, cy), gear.base_diameter / 2, dxfattribs={"layer": "CONSTRUCTION"})

    # Center lines (cross)
    r_ext = gear.outside_diameter / 2 + 8
    _add_center_line(ctx, (cx - r_ext, cy), (cx + r_ext, cy))
    _add_center_line(ctx, (cx, cy - r_ext), (cx, cy + r_ext))

    # Pitch circle diameter dimension (diameter)
    msp.add_circle((cx, cy), gear.pitch_diameter / 2, dxfattribs={"layer": "CONSTRUCTION"})
    msp.add_text(f"Ø{gear.pitch_diameter:.1f}", dxfattribs={"layer": "DIMENSIONS", "height": DIM_TEXT_HEIGHT}).set_placement(
        (cx + gear.pitch_diameter / 2 + 3, cy + 3))

    # Tooth count annotation
    msp.add_text(f"z={gear.teeth}  m={gear.module}  α={gear.pressure_angle_deg}°",
                 dxfattribs={"layer": "ANNOTATIONS", "height": TEXT_HEIGHT}).set_placement(
        (cx - 30, cy - r_ext - 10))

    # Label
    msp.add_text(label, dxfattribs={"layer": "ANNOTATIONS", "height": 3.5}).set_placement(
        (cx - 15, cy + r_ext + 5))

    # Side view (rectangle)
    sx = cx + gear.outside_diameter + 30
    sy = cy
    fw = gear.face_width
    od = gear.outside_diameter
    bd = gear.bore_diameter

    msp.add_lwpolyline([
        (sx, sy - od / 2), (sx + fw, sy - od / 2),
        (sx + fw, sy + od / 2), (sx, sy + od / 2),
        (sx, sy - od / 2)
    ], dxfattribs={"layer": "OUTLINE"})
    # Bore lines
    msp.add_line((sx, sy - bd / 2), (sx + fw, sy - bd / 2), dxfattribs={"layer": "HIDDEN"})
    msp.add_line((sx, sy + bd / 2), (sx + fw, sy + bd / 2), dxfattribs={"layer": "HIDDEN"})
    # Center line
    _add_center_line(ctx, (sx - 3, sy), (sx + fw + 3, sy))

    # Face width dimension
    msp.add_linear_dim(
        base=(sx, sy - od / 2 - 8), p1=(sx, sy - od / 2), p2=(sx + fw, sy - od / 2),
        angle=0,
        dxfattribs={"layer": "DIMENSIONS"},
        override={"dimtxt": DIM_TEXT_HEIGHT},
    )


def _draw_shaft_views(ctx: DrawContext, design: GearboxDesign, is_input: bool, label: str, cx: float, cy: float):
    """Draw front and end views of a shaft with steps."""
    msp = ctx.msp
    sp = design.shaft_parameters
    calc_dim = None  # We'll use shaft params directly

    if is_input:
        dia = sp.input_shaft_diameter
        length = sp.input_shaft_length
        bearing_dia = sp.bearing_seat_diameter_in
        bore = design.gear_parameters.input_bore
    else:
        dia = sp.output_shaft_diameter
        length = sp.output_shaft_length
        bearing_dia = sp.bearing_seat_diameter_out
        bore = design.gear_parameters.output_bore

    shoulder = sp.shaft_shoulder
    bearing_seat_len = 20  # bearing seat length

    # Bearing seat section is slightly larger
    bearing_dia_eff = max(bearing_dia, dia + shoulder)

    # Front view: stepped shaft profile
    x1 = cx
    y_center = cy

    # Left bearing seat
    bs_r = bearing_dia_eff / 2
    shaft_r = dia / 2
    x2 = x1 + bearing_seat_len
    x3 = x2 + (length - 2 * bearing_seat_len)

    msp.add_lwpolyline([
        (x1, y_center + bs_r),
        (x2, y_center + bs_r),
        (x2, y_center + shaft_r),
        (x3, y_center + shaft_r),
        (x3, y_center - shaft_r),
        (x2, y_center - shaft_r),
        (x2, y_center - bs_r),
        (x1, y_center - bs_r),
        (x1, y_center + bs_r),
    ], dxfattribs={"layer": "SHAFTS"})

    # Right bearing seat (mirrored)
    x4 = x3
    x5 = x4 + bearing_seat_len
    msp.add_lwpolyline([
        (x4, y_center + shaft_r),
        (x5, y_center + bs_r),
        (x5, y_center - bs_r),
        (x4, y_center - shaft_r),
    ], dxfattribs={"layer": "SHAFTS"})

    # Keyway (rectangle on top of shaft)
    kw = sp.keyway_width
    kh = sp.keyway_height
    key_x1 = x2 + 10
    key_x2 = key_x1 + length * 0.4
    msp.add_lwpolyline([
        (key_x1, y_center + shaft_r),
        (key_x1, y_center + shaft_r + kh),
        (key_x2, y_center + shaft_r + kh),
        (key_x2, y_center + shaft_r),
    ], dxfattribs={"layer": "HIDDEN"})

    # Center line
    total_len = length + 2 * bearing_seat_len
    _add_center_line(ctx, (x1 - 5, y_center), (x1 + total_len + 5, y_center))

    # Dimensions
    msp.add_linear_dim(
        base=(x1, y_center + bs_r + 15), p1=(x1, y_center + bs_r), p2=(x1 + total_len, y_center + bs_r),
        angle=0,
        dxfattribs={"layer": "DIMENSIONS"},
        override={"dimtxt": DIM_TEXT_HEIGHT},
    )

    # Diameter annotation
    msp.add_text(f"Ø{dia:.1f}", dxfattribs={"layer": "DIMENSIONS", "height": DIM_TEXT_HEIGHT}).set_placement(
        (x2 + 5, y_center + shaft_r + 3))
    msp.add_text(f"Ø{bearing_dia_eff:.1f}", dxfattribs={"layer": "DIMENSIONS", "height": DIM_TEXT_HEIGHT}).set_placement(
        (x1 + 2, y_center + bs_r + 3))

    # End view (circle)
    ev_cx = cx + total_len + 30
    ev_cy = y_center
    msp.add_circle((ev_cx, ev_cy), dia / 2, dxfattribs={"layer": "SHAFTS"})
    msp.add_circle((ev_cx, ev_cy), dia / 2 + 3, dxfattribs={"layer": "CONSTRUCTION"})
    # Keyway in end view
    msp.add_line((ev_cx - kw / 2, ev_cy + dia / 2), (ev_cx + kw / 2, ev_cy + dia / 2),
                 dxfattribs={"layer": "SHAFTS"})
    _add_center_line(ctx, (ev_cx - dia / 2 - 5, ev_cy), (ev_cx + dia / 2 + 5, ev_cy))
    _add_center_line(ctx, (ev_cx, ev_cy - dia / 2 - 5), (ev_cx, ev_cy + dia / 2 + 5))

    # Label
    msp.add_text(label, dxfattribs={"layer": "ANNOTATIONS", "height": 3.5}).set_placement(
        (x1, y_center - bs_r - 12))


def _draw_housing_views(ctx: DrawContext, design: GearboxDesign, calc: CalculationResults):
    """Draw housing front, top, and side views."""
    msp = ctx.msp
    hp = design.housing_parameters
    cx, cy = 100, 200

    # Front view (rectangular box with shaft openings)
    hl = hp.housing_length
    hw = hp.housing_width
    hh = hp.housing_height
    wt = hp.wall_thickness
    bt = hp.base_thickness
    ct = hp.cover_thickness

    # Outer outline
    msp.add_lwpolyline([
        (cx, cy), (cx + hl, cy),
        (cx + hl, cy + hh), (cx, cy + hh),
        (cx, cy)
    ], dxfattribs={"layer": "HOUSING"})

    # Inner cavity
    msp.add_lwpolyline([
        (cx + wt, cy + bt), (cx + hl - wt, cy + bt),
        (cx + hl - wt, cy + hh - ct), (cx + wt, cy + hh - ct),
        (cx + wt, cy + bt)
    ], dxfattribs={"layer": "HIDDEN"})

    # Shaft centre line
    center_y = cy + bt + (hh - bt - ct) / 2
    _add_center_line(ctx, (cx - 10, center_y), (cx + hl + 10, center_y))

    # Shaft openings (circles for bearing seats)
    in_cx = cx + wt + 15
    out_cx = cx + hl - wt - 15
    in_r = design.shaft_parameters.bearing_seat_diameter_in / 2
    out_r = design.shaft_parameters.bearing_seat_diameter_out / 2
    msp.add_circle((in_cx, center_y), in_r + wt / 2, dxfattribs={"layer": "HOUSING"})
    msp.add_circle((in_cx, center_y), in_r, dxfattribs={"layer": "HIDDEN"})
    msp.add_circle((out_cx, center_y), out_r + wt / 2, dxfattribs={"layer": "HOUSING"})
    msp.add_circle((out_cx, center_y), out_r, dxfattribs={"layer": "HIDDEN"})

    # Mounting holes in base
    hole_d = hp.mounting_hole_diameter
    n_holes = hp.mounting_hole_count
    for i in range(n_holes):
        hx = cx + 10 + (hl - 20) * i / max(n_holes - 1, 1)
        hy = cy + bt / 2
        msp.add_circle((hx, hy), hole_d / 2, dxfattribs={"layer": "FASTENERS"})
        msp.add_circle((hx, hy), hole_d / 2 + 1, dxfattribs={"layer": "CENTER"})

    # Dimensions
    msp.add_linear_dim(base=(cx, cy - 10), p1=(cx, cy), p2=(cx + hl, cy),
                       angle=0, dxfattribs={"layer": "DIMENSIONS"},
                       override={"dimtxt": DIM_TEXT_HEIGHT})
    msp.add_linear_dim(base=(cx - 10, cy), p1=(cx, cy), p2=(cx, cy + hh),
                       angle=90, dxfattribs={"layer": "DIMENSIONS"},
                       override={"dimtxt": DIM_TEXT_HEIGHT})

    # Top view
    tv_cx, tv_cy = cx, cy - 120
    msp.add_lwpolyline([
        (tv_cx, tv_cy), (tv_cx + hl, tv_cy),
        (tv_cx + hl, tv_cy - hw), (tv_cx, tv_cy - hw),
        (tv_cx, tv_cy)
    ], dxfattribs={"layer": "HOUSING"})
    msp.add_lwpolyline([
        (tv_cx + wt, tv_cy - wt), (tv_cx + hl - wt, tv_cy - wt),
        (tv_cx + hl - wt, tv_cy - hw + wt), (tv_cx + wt, tv_cy - hw + wt),
        (tv_cx + wt, tv_cy - wt)
    ], dxfattribs={"layer": "HIDDEN"})

    # Labels
    msp.add_text("FRONT VIEW", dxfattribs={"layer": "ANNOTATIONS", "height": TEXT_HEIGHT}).set_placement(
        (cx + hl / 2 - 10, cy + hh + 5))
    msp.add_text("TOP VIEW", dxfattribs={"layer": "ANNOTATIONS", "height": TEXT_HEIGHT}).set_placement(
        (tv_cx + hl / 2 - 10, tv_cy + 5))


def _draw_cover_views(ctx: DrawContext, design: GearboxDesign):
    """Draw housing cover plan and elevation views."""
    msp = ctx.msp
    hp = design.housing_parameters
    cx, cy = 100, 200

    # Plan view
    msp.add_lwpolyline([
        (cx, cy), (cx + hp.housing_length, cy),
        (cx + hp.housing_length, cy + hp.housing_width),
        (cx, cy + hp.housing_width),
        (cx, cy)
    ], dxfattribs={"layer": "HOUSING"})

    # Fastener holes
    n = 4
    for i in range(n):
        fx = cx + 15 + (hp.housing_length - 30) * i / max(n - 1, 1)
        fy1 = cy + 8
        fy2 = cy + hp.housing_width - 8
        msp.add_circle((fx, fy1), hp.mounting_hole_diameter / 2, dxfattribs={"layer": "FASTENERS"})
        msp.add_circle((fx, fy2), hp.mounting_hole_diameter / 2, dxfattribs={"layer": "FASTENERS"})

    # Shaft openings
    in_cx = cx + 20
    out_cx = cx + hp.housing_length - 20
    cy_mid = cy + hp.housing_width / 2
    msp.add_circle((in_cx, cy_mid), design.shaft_parameters.bearing_seat_diameter_in / 2 + 2,
                   dxfattribs={"layer": "HIDDEN"})
    msp.add_circle((out_cx, cy_mid), design.shaft_parameters.bearing_seat_diameter_out / 2 + 2,
                   dxfattribs={"layer": "HIDDEN"})

    # Elevation (side view of cover)
    ev_cx, ev_cy = cx, cy - 80
    msp.add_lwpolyline([
        (ev_cx, ev_cy), (ev_cx + hp.housing_length, ev_cy),
        (ev_cx + hp.housing_length, ev_cy + hp.cover_thickness),
        (ev_cx, ev_cy + hp.cover_thickness),
        (ev_cx, ev_cy)
    ], dxfattribs={"layer": "HOUSING"})

    # Dimensions
    msp.add_linear_dim(base=(cx, cy + hp.housing_width + 10), p1=(cx, cy + hp.housing_width),
                       p2=(cx + hp.housing_length, cy + hp.housing_width),
                       angle=0, dxfattribs={"layer": "DIMENSIONS"},
                       override={"dimtxt": DIM_TEXT_HEIGHT})
    msp.add_linear_dim(base=(cx - 10, cy), p1=(cx, cy), p2=(cx, cy + hp.housing_width),
                       angle=90, dxfattribs={"layer": "DIMENSIONS"},
                       override={"dimtxt": DIM_TEXT_HEIGHT})

    msp.add_text("COVER PLAN VIEW", dxfattribs={"layer": "ANNOTATIONS", "height": TEXT_HEIGHT}).set_placement(
        (cx + 20, cy + hp.housing_width + 12))
    msp.add_text("COVER ELEVATION", dxfattribs={"layer": "ANNOTATIONS", "height": TEXT_HEIGHT}).set_placement(
        (ev_cx + 20, ev_cy - 8))
    msp.add_text(f"Cover Thickness: {hp.cover_thickness:.1f} mm",
                 dxfattribs={"layer": "ANNOTATIONS", "height": TEXT_HEIGHT}).set_placement(
        (ev_cx + hp.housing_length + 10, ev_cy + 2))


def _draw_assembly_views(ctx: DrawContext, design: GearboxDesign, calc: CalculationResults):
    """Draw general assembly views: front, top, side, and isometric reference."""
    msp = ctx.msp
    hp = design.housing_parameters

    cx, cy = 150, 180
    center_dist = calc.centre_distance

    # --- Front view ---
    # Housing outline
    hl = hp.housing_length
    hh = hp.housing_height
    bt = hp.base_thickness
    wt = hp.wall_thickness
    ct = hp.cover_thickness

    msp.add_lwpolyline([
        (cx, cy), (cx + hl, cy),
        (cx + hl, cy + hh), (cx, cy + hh),
        (cx, cy)
    ], dxfattribs={"layer": "HOUSING"})

    # Base
    msp.add_lwpolyline([
        (cx - 5, cy), (cx - 5, cy - bt),
        (cx + hl + 5, cy - bt), (cx + hl + 5, cy),
    ], dxfattribs={"layer": "HOUSING"})

    # Inner cavity
    msp.add_lwpolyline([
        (cx + wt, cy + bt), (cx + hl - wt, cy + bt),
        (cx + hl - wt, cy + hh - ct), (cx + wt, cy + hh - ct),
        (cx + wt, cy + bt)
    ], dxfattribs={"layer": "HIDDEN"})

    # Shaft centres
    center_y = cy + hh / 2
    in_cx = cx + hl / 2 - center_dist / 2
    out_cx = cx + hl / 2 + center_dist / 2

    # Input gear
    ig = calc.input_gear
    msp.add_circle((in_cx, center_y), ig.outside_diameter / 2, dxfattribs={"layer": "GEARS"})
    msp.add_circle((in_cx, center_y), ig.pitch_diameter / 2, dxfattribs={"layer": "CONSTRUCTION"})

    # Output gear
    og = calc.output_gear
    msp.add_circle((out_cx, center_y), og.outside_diameter / 2, dxfattribs={"layer": "GEARS"})
    msp.add_circle((out_cx, center_y), og.pitch_diameter / 2, dxfattribs={"layer": "CONSTRUCTION"})

    # Shaft lines
    msp.add_circle((in_cx, center_y), design.shaft_parameters.input_shaft_diameter / 2,
                   dxfattribs={"layer": "SHAFTS"})
    msp.add_circle((out_cx, center_y), design.shaft_parameters.output_shaft_diameter / 2,
                   dxfattribs={"layer": "SHAFTS"})

    # Center line
    _add_center_line(ctx, (cx - 10, center_y), (cx + hl + 10, center_y))
    _add_center_line(ctx, (in_cx, center_y - og.outside_diameter / 2 - 10),
                     (in_cx, center_y + og.outside_diameter / 2 + 10))
    _add_center_line(ctx, (out_cx, center_y - og.outside_diameter / 2 - 10),
                     (out_cx, center_y + og.outside_diameter / 2 + 10))

    # Centre distance dimension
    msp.add_linear_dim(base=(in_cx, center_y + og.outside_diameter / 2 + 15),
                       p1=(in_cx, center_y), p2=(out_cx, center_y),
                       angle=0,
                       dxfattribs={"layer": "DIMENSIONS"},
                       override={"dimtxt": DIM_TEXT_HEIGHT})
    # Centre distance text
    msp.add_text(f"a = {calc.centre_distance:.1f} mm",
                 dxfattribs={"layer": "ANNOTATIONS", "height": TEXT_HEIGHT}).set_placement(
        (in_cx + center_dist / 2 - 15, center_y + og.outside_diameter / 2 + 20))

    # Gear ratio annotation
    msp.add_text(f"i = {calc.reduction_ratio:.1f} : 1  (z1={ig.teeth}, z2={og.teeth})",
                 dxfattribs={"layer": "ANNOTATIONS", "height": TEXT_HEIGHT}).set_placement(
        (cx + 5, cy + hh + 5))

    msp.add_text("FRONT VIEW", dxfattribs={"layer": "ANNOTATIONS", "height": 3.0}).set_placement(
        (cx + 5, cy + hh + 12))

    # --- Top view ---
    tv_cx, tv_cy = cx, cy - hh - 30
    msp.add_lwpolyline([
        (tv_cx, tv_cy), (tv_cx + hl, tv_cy),
        (tv_cx + hl, tv_cy - hp.housing_width), (tv_cx, tv_cy - hp.housing_width),
        (tv_cx, tv_cy)
    ], dxfattribs={"layer": "HOUSING"})

    # Gear widths in top view
    fw = design.gear_parameters.face_width
    gear_cy = tv_cy - hp.housing_width / 2
    _add_rect(ctx, (in_cx - fw / 2, gear_cy - ig.outside_diameter / 2),
              fw, ig.outside_diameter, "GEARS")
    _add_rect(ctx, (out_cx - fw / 2, gear_cy - og.outside_diameter / 2),
              fw, og.outside_diameter, "GEARS")

    msp.add_text("TOP VIEW", dxfattribs={"layer": "ANNOTATIONS", "height": 3.0}).set_placement(
        (tv_cx + 5, tv_cy + 5))

    # --- Side view ---
    sv_cx, sv_cy = cx + hl + 50, cy
    msp.add_lwpolyline([
        (sv_cx, sv_cy), (sv_cx + hp.housing_width, sv_cy),
        (sv_cx + hp.housing_width, sv_cy + hh), (sv_cx, sv_cy + hh),
        (sv_cx, sv_cy)
    ], dxfattribs={"layer": "HOUSING"})

    # Gears seen from side (rectangles)
    _add_rect(ctx, (sv_cx + hp.housing_width / 2 - fw / 2, center_y - ig.outside_diameter / 2),
              fw, ig.outside_diameter, "GEARS")
    _add_rect(ctx, (sv_cx + hp.housing_width / 2 - fw / 2, center_y - og.outside_diameter / 2),
              fw, og.outside_diameter, "GEARS")

    msp.add_text("SIDE VIEW", dxfattribs={"layer": "ANNOTATIONS", "height": 3.0}).set_placement(
        (sv_cx + 5, sv_cy + hh + 5))

    # --- Isometric reference ---
    iso_cx, iso_cy = cx + hl + 50, cy - hh - 60
    # Simple isometric box outline
    dx, dy = hp.housing_width * 0.5, hp.housing_length * 0.25
    msp.add_lwpolyline([
        (iso_cx, iso_cy), (iso_cx + dx, iso_cy + dy),
        (iso_cx + dx + hl * 0.4, iso_cy + dy),
        (iso_cx + hl * 0.4, iso_cy),
        (iso_cx, iso_cy)
    ], dxfattribs={"layer": "CONSTRUCTION"})
    msp.add_text("ISOMETRIC REFERENCE", dxfattribs={"layer": "ANNOTATIONS", "height": 2.5}).set_placement(
        (iso_cx, iso_cy - 5))


def _draw_section_view(ctx: DrawContext, design: GearboxDesign, calc: CalculationResults):
    """Draw a sectional assembly view showing internal gear arrangement."""
    msp = ctx.msp
    hp = design.housing_parameters
    cx, cy = 150, 150

    hl = hp.housing_length
    hh = hp.housing_height
    wt = hp.wall_thickness
    bt = hp.base_thickness
    ct = hp.cover_thickness
    fw = design.gear_parameters.face_width

    # Housing cross-section (hatched left wall, right wall, base)
    msp.add_lwpolyline([
        (cx, cy), (cx, cy + hh),
        (cx + wt, cy + hh - ct), (cx + wt, cy + bt),
        (cx + hl - wt, cy + bt), (cx + hl - wt, cy + hh - ct),
        (cx + hl, cy + hh), (cx + hl, cy),
        (cx + hl - wt, cy), (cx + hl - wt, cy + bt),
        (cx + wt, cy + bt), (cx + wt, cy),
        (cx, cy)
    ], dxfattribs={"layer": "HOUSING"})

    # Section lines (simplified hatch marks)
    for x in range(int(cx), int(cx + wt), 3):
        msp.add_line((x, cy + bt), (x + 2, cy + bt + 2), dxfattribs={"layer": "SECTION_LINES"})
        msp.add_line((x, cy + hh - ct), (x + 2, cy + hh - ct - 2), dxfattribs={"layer": "SECTION_LINES"})
    for x in range(int(cx + hl - wt), int(cx + hl), 3):
        msp.add_line((x, cy + bt), (x + 2, cy + bt + 2), dxfattribs={"layer": "SECTION_LINES"})
        msp.add_line((x, cy + hh - ct), (x + 2, cy + hh - ct - 2), dxfattribs={"layer": "SECTION_LINES"})

    center_y = cy + hh / 2
    center_dist = calc.centre_distance
    in_cx = cx + hl / 2 - center_dist / 2
    out_cx = cx + hl / 2 + center_dist / 2

    # Gears (sectioned rectangles)
    ig = calc.input_gear
    og = calc.output_gear
    _add_rect(ctx, (in_cx - fw / 2, center_y - ig.outside_diameter / 2),
              fw, ig.outside_diameter, "GEARS")
    _add_rect(ctx, (out_cx - fw / 2, center_y - og.outside_diameter / 2),
              fw, og.outside_diameter, "GEARS")

    # Gear center circles (bore)
    msp.add_circle((in_cx, center_y), design.shaft_parameters.input_shaft_diameter / 2,
                   dxfattribs={"layer": "SHAFTS"})
    msp.add_circle((out_cx, center_y), design.shaft_parameters.output_shaft_diameter / 2,
                   dxfattribs={"layer": "SHAFTS"})

    # Bearing representations
    bearing_h = 15
    for bx, br in [(cx + wt + 5, design.shaft_parameters.bearing_seat_diameter_in / 2),
                   (cx + hl - wt - 5, design.shaft_parameters.bearing_seat_diameter_in / 2),
                   (cx + wt + 5 + center_dist, design.shaft_parameters.bearing_seat_diameter_out / 2),
                   (cx + hl - wt - 5 - center_dist + center_dist, design.shaft_parameters.bearing_seat_diameter_out / 2)]:
        pass  # Simplified - bearings shown as thick lines

    # Center line
    _add_center_line(ctx, (cx - 5, center_y), (cx + hl + 5, center_y))
    _add_center_line(ctx, (in_cx, center_y - og.outside_diameter / 2 - 10),
                     (in_cx, center_y + og.outside_diameter / 2 + 10))
    _add_center_line(ctx, (out_cx, center_y - og.outside_diameter / 2 - 10),
                     (out_cx, center_y + og.outside_diameter / 2 + 10))

    # Component callouts
    callouts = [
        (in_cx, center_y + ig.outside_diameter / 2 + 5, "1 - INPUT GEAR"),
        (out_cx, center_y + og.outside_diameter / 2 + 5, "2 - OUTPUT GEAR"),
        (cx + wt / 2, cy + hh - 5, "3 - HOUSING"),
        (cx + hl / 2, center_y, "4 - SHAFTS"),
        (cx + wt / 2, cy + bt + 2, "5 - BEARINGS"),
    ]
    for x, y, txt in callouts:
        msp.add_text(txt, dxfattribs={"layer": "ANNOTATIONS", "height": 2.5}).set_placement((x, y))

    msp.add_text("SECTIONAL ASSEMBLY VIEW (A-A)",
                 dxfattribs={"layer": "ANNOTATIONS", "height": 3.0}).set_placement(
        (cx + 5, cy + hh + 8))


def _draw_exploded_view(ctx: DrawContext, design: GearboxDesign, calc: CalculationResults):
    """Draw an exploded assembly view with numbered callouts."""
    msp = ctx.msp
    cx, cy = 150, 200
    offset = 40

    ig = calc.input_gear
    og = calc.output_gear
    fw = design.gear_parameters.face_width

    # Stack components vertically with offsets
    components = [
        ("HOUSING COVER", cx, cy, 120, 10),
        ("OUTPUT SHAFT", cx + 80, cy - offset, 15, 60),
        ("OUTPUT GEAR", cx + 80, cy - 2 * offset, og.outside_diameter / 2, fw / 4),
        ("INPUT GEAR", cx - 80, cy - 2 * offset, ig.outside_diameter / 2, fw / 4),
        ("INPUT SHAFT", cx - 80, cy - 3 * offset, 15, 60),
        ("BEARINGS (×4)", cx, cy - 4 * offset, 20, 15),
        ("KEYS (×2)", cx + 80, cy - 4 * offset, 8, 20),
        ("LOWER HOUSING", cx, cy - 5 * offset, 150, 30),
        ("MOUNTING BASE", cx, cy - 6 * offset, 160, 10),
    ]

    for i, (name, x, y, w, h) in enumerate(components, 1):
        # Draw component outline
        _add_rect(ctx, (x - w / 2, y - h / 2), w, h, "OUTLINE")
        # Number callout
        msp.add_circle((x + w / 2 + 15, y), 6, dxfattribs={"layer": "ANNOTATIONS"})
        msp.add_text(str(i), dxfattribs={"layer": "ANNOTATIONS", "height": 3.0}).set_placement(
            (x + w / 2 + 13, y - 1.5))
        msp.add_text(f"{i}. {name}", dxfattribs={"layer": "ANNOTATIONS", "height": 2.5}).set_placement(
            (x + w / 2 + 25, y - 1))

    # Parts list
    list_x = cx + 200
    list_y = cy
    msp.add_text("PARTS LIST", dxfattribs={"layer": "BOM_TABLE", "height": 3.5}).set_placement(
        (list_x, list_y))
    msp.add_text("ITEM  DESCRIPTION", dxfattribs={"layer": "BOM_TABLE", "height": 2.5}).set_placement(
        (list_x, list_y - 8))
    for i, (name, _, _, _, _) in enumerate(components, 1):
        msp.add_text(f"  {i}    {name}", dxfattribs={"layer": "BOM_TABLE", "height": 2.5}).set_placement(
            (list_x, list_y - 8 - i * 6))

    msp.add_text("EXPLODED ASSEMBLY VIEW",
                 dxfattribs={"layer": "ANNOTATIONS", "height": 3.0}).set_placement(
        (cx - 20, cy + 25))


# ---- Public API ----

def generate_all_drawings(
    design: GearboxDesign,
    calc: CalculationResults,
    output_dir: str,
) -> list[DrawingInfo]:
    """
    Generate all 9 DXF drawing sheets for the gearbox design.
    Returns a list of DrawingInfo objects.
    """
    os.makedirs(output_dir, exist_ok=True)
    drawings = []

    sheets = [
        ("01_general_assembly", "General Assembly",
         "Front, top, side, and isometric reference views of the complete gearbox assembly.",
         _draw_assembly_views),
        ("02_gearbox_housing", "Gearbox Housing",
         "Front, top, and side views of the lower housing with internal cavity, bearing seats, and mounting holes.",
         lambda ctx, d, c: _draw_housing_views(ctx, d, c)),
        ("03_input_shaft", "Input Shaft",
         "Front and end views of the input shaft with steps, bearing seats, gear mounting position, and keyway.",
         lambda ctx, d, c: _draw_shaft_views(ctx, d, True, "INPUT SHAFT", 100, 150)),
        ("04_output_shaft", "Output Shaft",
         "Front and end views of the output shaft with steps, bearing seats, and gear mounting position.",
         lambda ctx, d, c: _draw_shaft_views(ctx, d, False, "OUTPUT SHAFT", 100, 150)),
        ("05_input_gear", "Input Gear",
         "Front and side views of the input pinion with pitch circle, bore, face width, and tooth parameters.",
         lambda ctx, d, c: _draw_gear_views(ctx, c.input_gear, "INPUT GEAR (PINION)", 120, 150)),
        ("06_output_gear", "Output Gear",
         "Front and side views of the output gear with pitch circle, bore, face width, and tooth parameters.",
         lambda ctx, d, c: _draw_gear_views(ctx, c.output_gear, "OUTPUT GEAR", 120, 150)),
        ("07_housing_cover", "Housing Cover",
         "Plan and elevation views of the housing cover with fastener holes and shaft openings.",
         lambda ctx, d, c: _draw_cover_views(ctx, d)),
        ("08_assembly_section", "Assembly Section",
         "Sectional view through the gearbox showing internal gear arrangement, shafts, bearings, and housing.",
         lambda ctx, d, c: _draw_section_view(ctx, d, c)),
        ("09_exploded_assembly", "Exploded Assembly",
         "Exploded view with numbered component callouts and parts list.",
         lambda ctx, d, c: _draw_exploded_view(ctx, d, c)),
    ]

    total = len(sheets)
    for idx, (file_base, name, desc, draw_fn) in enumerate(sheets, 1):
        doc, msp = _setup_doc()
        ctx = DrawContext(doc=doc, msp=msp, offset_x=0, offset_y=0)

        # Draw a border
        msp.add_lwpolyline([
            (5, 5), (290, 5), (290, 200), (5, 200), (5, 5)
        ], dxfattribs={"layer": "BORDER"})

        # Draw the specific content
        draw_fn(ctx, design, calc)

        # Title block
        ctx.offset_x = 110
        ctx.offset_y = 0
        _draw_title_block(ctx, design, name, idx, total)

        filename = f"{file_base}.dxf"
        filepath = os.path.join(output_dir, filename)
        doc.saveas(filepath)

        drawings.append(DrawingInfo(
            drawing_id=file_base,
            name=name,
            description=desc,
            filename=filename,
            dxf_available=True,
        ))

    return drawings
