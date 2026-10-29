"""
Engineering calculation engine for spur gear pair design.

All formulas follow ISO 53 / DIN 3960 conventions for standard spur gears
with the simplified assumptions documented in docs/engineering_assumptions.md.

Key formulas:
    Pitch diameter:     d = m × z
    Centre distance:    a = (d1 + d2) / 2
    Reduction ratio:    i = z2 / z1
    Output speed:       n2 = n1 / i
    Base circle:        db = d × cos(α)
    Addendum:           ha = m            (standard full-depth)
    Dedendum:           hf = 1.25 × m     (standard clearance)
    Outside diameter:   da = d + 2·ha
    Root diameter:      df = d - 2·hf
    Circular pitch:     p = π × m
    Tooth thickness:    s = p / 2
"""
from __future__ import annotations

import math
from app.schemas.design import (
    GearboxDesign,
    CalculationResults,
    GearDimensions,
    GearParameters,
    PressureAngle,
)


def _pa_deg(pa: PressureAngle) -> float:
    return float(pa.value)


def compute_gear_dimensions(
    teeth: int,
    module: float,
    pressure_angle_deg: float,
    face_width: float,
    bore_diameter: float,
) -> GearDimensions:
    """Compute all theoretical gear dimensions for a single spur gear."""
    d = module * teeth                              # pitch diameter
    db = d * math.cos(math.radians(pressure_angle_deg))  # base circle
    ha = module                                      # addendum (standard)
    hf = 1.25 * module                                # dedendum (standard + clearance)
    da = d + 2 * ha                                   # outside (tip) diameter
    df = d - 2 * hf                                   # root diameter
    p = math.pi * module                              # circular pitch
    s = p / 2.0                                       # tooth thickness on pitch circle

    return GearDimensions(
        teeth=teeth,
        module=module,
        pressure_angle_deg=pressure_angle_deg,
        pitch_diameter=round(d, 4),
        base_diameter=round(db, 4),
        addendum=round(ha, 4),
        dedendum=round(hf, 4),
        outside_diameter=round(da, 4),
        root_diameter=round(df, 4),
        face_width=round(face_width, 4),
        bore_diameter=round(bore_diameter, 4),
        circular_pitch=round(p, 4),
        tooth_thickness=round(s, 4),
    )


def calculate_design(design: GearboxDesign) -> CalculationResults:
    """
    Run the full calculation for a single-stage spur gear pair.

    Returns CalculationResults containing dimensions for both gears,
    centre distance, ratio, and speeds.
    """
    gp = design.gear_parameters
    pa = _pa_deg(gp.pressure_angle)

    input_gear = compute_gear_dimensions(
        teeth=gp.input_teeth,
        module=gp.module,
        pressure_angle_deg=pa,
        face_width=gp.face_width,
        bore_diameter=gp.input_bore,
    )

    output_gear = compute_gear_dimensions(
        teeth=gp.output_teeth,
        module=gp.module,
        pressure_angle_deg=pa,
        face_width=gp.face_width,
        bore_diameter=gp.output_bore,
    )

    centre_distance = (input_gear.pitch_diameter + output_gear.pitch_diameter) / 2.0
    reduction_ratio = output_gear.teeth / input_gear.teeth
    output_speed = design.input_speed_rpm / reduction_ratio

    return CalculationResults(
        input_gear=input_gear,
        output_gear=output_gear,
        centre_distance=round(centre_distance, 4),
        reduction_ratio=round(reduction_ratio, 6),
        input_pitch_diameter=input_gear.pitch_diameter,
        output_pitch_diameter=output_gear.pitch_diameter,
        output_speed_rpm=round(output_speed, 2),
        pressure_angle_deg=pa,
        module=gp.module,
        circular_pitch=round(math.pi * gp.module, 4),
        base_circle_input=input_gear.base_diameter,
        base_circle_output=output_gear.base_diameter,
    )


def format_calculation_summary(calc: CalculationResults) -> list[dict[str, str]]:
    """Return a list of label/value/formula triples for display."""
    rows = [
        ("Pitch Diameter (Pinion)", f"{calc.input_pitch_diameter:.3f} mm", "d₁ = m × z₁"),
        ("Pitch Diameter (Gear)", f"{calc.output_pitch_diameter:.3f} mm", "d₂ = m × z₂"),
        ("Centre Distance", f"{calc.centre_distance:.3f} mm", "a = (d₁ + d₂) / 2"),
        ("Reduction Ratio", f"{calc.reduction_ratio:.3f} : 1", "i = z₂ / z₁"),
        ("Input Speed", f"{calc.input_speed_rpm if hasattr(calc, 'input_speed_rpm') else '—'} rpm", "n₁ (given)"),
        ("Output Speed", f"{calc.output_speed_rpm:.1f} rpm", "n₂ = n₁ / i"),
        ("Pressure Angle", f"{calc.pressure_angle_deg}°", "α (given)"),
        ("Module", f"{calc.module:.3f} mm", "m (given)"),
        ("Circular Pitch", f"{calc.circular_pitch:.3f} mm", "p = π × m"),
        ("Base Circle (Pinion)", f"{calc.base_circle_input:.3f} mm", "d_b1 = d₁ × cos(α)"),
        ("Base Circle (Gear)", f"{calc.base_circle_output:.3f} mm", "d_b2 = d₂ × cos(α)"),
    ]
    return [{"parameter": r[0], "value": r[1], "formula": r[2]} for r in rows]
