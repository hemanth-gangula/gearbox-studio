"""
Design validation engine.

Checks engineering constraints on the gearbox design configuration.
Each check produces a ValidationIssue with severity:
  - "error":   design cannot proceed
  - "warning": design can proceed but has a concern
  - "info":    informational note about assumptions
"""
from __future__ import annotations

import math
from app.schemas.design import (
    GearboxDesign,
    CalculationResults,
    ValidationResult,
    ValidationIssue,
)


def validate_design(design: GearboxDesign, calc: CalculationResults | None = None) -> ValidationResult:
    issues: list[ValidationIssue] = []
    checks = 0

    gp = design.gear_parameters
    sp = design.shaft_parameters
    hp = design.housing_parameters
    ap = design.assembly_parameters

    # --- Gear checks ---
    checks += 1
    if gp.input_teeth < 8:
        issues.append(ValidationIssue(
            field="gear_parameters.input_teeth",
            message="Pinion tooth count is below the recommended minimum of 17 for standard full-depth teeth "
                    "to avoid undercutting. With fewer teeth, profile shift is required.",
            severity="warning",
        ))

    checks += 1
    if gp.output_teeth <= gp.input_teeth:
        issues.append(ValidationIssue(
            field="gear_parameters.output_teeth",
            message="Output gear tooth count should be greater than the input (pinion) for a reduction gearbox.",
            severity="error",
        ))

    checks += 1
    if gp.module <= 0:
        issues.append(ValidationIssue(
            field="gear_parameters.module",
            message="Module must be a positive value.",
            severity="error",
        ))

    checks += 1
    if gp.pressure_angle.value not in ("14.5", "20", "25"):
        issues.append(ValidationIssue(
            field="gear_parameters.pressure_angle",
            message="Pressure angle must be 14.5°, 20°, or 25°.",
            severity="error",
        ))

    checks += 1
    if gp.face_width < 3 * gp.module:
        issues.append(ValidationIssue(
            field="gear_parameters.face_width",
            message=f"Face width ({gp.face_width} mm) is less than 3× module ({3*gp.module} mm). "
                    "Recommended face width is 8–14× module.",
            severity="warning",
        ))

    checks += 1
    if gp.face_width > 20 * gp.module:
        issues.append(ValidationIssue(
            field="gear_parameters.face_width",
            message=f"Face width ({gp.face_width} mm) exceeds 20× module. "
                    "Load distribution may be uneven across the face.",
            severity="warning",
        ))

    # --- Shaft / bore compatibility ---
    checks += 1
    if sp.input_shaft_diameter > gp.input_bore + 0.5:
        issues.append(ValidationIssue(
            field="shaft_parameters.input_shaft_diameter",
            message=f"Input shaft diameter ({sp.input_shaft_diameter} mm) is larger than the input gear "
                    f"bore ({gp.input_bore} mm). The gear cannot be mounted on the shaft.",
            severity="error",
        ))

    checks += 1
    if sp.output_shaft_diameter > gp.output_bore + 0.5:
        issues.append(ValidationIssue(
            field="shaft_parameters.output_shaft_diameter",
            message=f"Output shaft diameter ({sp.output_shaft_diameter} mm) is larger than the output "
                    f"gear bore ({gp.output_bore} mm). The gear cannot be mounted on the shaft.",
            severity="error",
        ))

    checks += 1
    if sp.bearing_seat_diameter_in < sp.input_shaft_diameter:
        issues.append(ValidationIssue(
            field="shaft_parameters.bearing_seat_diameter_in",
            message="Input bearing seat diameter is smaller than the input shaft diameter. "
                    "The bearing cannot seat correctly.",
            severity="warning",
        ))

    checks += 1
    if sp.bearing_seat_diameter_out < sp.output_shaft_diameter:
        issues.append(ValidationIssue(
            field="shaft_parameters.bearing_seat_diameter_out",
            message="Output bearing seat diameter is smaller than the output shaft diameter. "
                    "The bearing cannot seat correctly.",
            severity="warning",
        ))

    # --- Housing clearance checks ---
    if calc:
        checks += 1
        # The largest gear outside diameter must fit inside the housing height
        max_gear_od = max(calc.input_gear.outside_diameter, calc.output_gear.outside_diameter)
        housing_inner_height = hp.housing_height - 2 * hp.wall_thickness
        if max_gear_od > housing_inner_height:
            issues.append(ValidationIssue(
                field="housing_parameters.housing_height",
                message=f"Maximum gear outside diameter ({max_gear_od:.1f} mm) exceeds housing inner "
                        f"height ({housing_inner_height:.1f} mm). The gear will interfere with the housing wall.",
                severity="error",
            ))

        checks += 1
        # Face width must fit within housing inner width (gear axis direction)
        housing_inner_width = hp.housing_width - 2 * hp.wall_thickness
        if gp.face_width > housing_inner_width:
            issues.append(ValidationIssue(
                field="housing_parameters.housing_width",
                message=f"Gear face width ({gp.face_width:.1f} mm) exceeds housing inner "
                        f"width ({housing_inner_width:.1f} mm). The gear will not fit axially.",
                severity="error",
            ))

        checks += 1
        # Housing length must accommodate centre distance plus gear radii + clearance
        required_length = calc.centre_distance + calc.input_gear.outside_diameter / 2 + calc.output_gear.outside_diameter / 2 + 2 * hp.wall_thickness
        if required_length > hp.housing_length:
            issues.append(ValidationIssue(
                field="housing_parameters.housing_length",
                message=f"Housing length ({hp.housing_length} mm) is shorter than required "
                        f"({required_length:.1f} mm) to contain both gears with wall clearance.",
                severity="error",
            ))

        checks += 1
        # Face width must fit within housing width minus wall and clearance
        required_height = max(calc.input_gear.outside_diameter, calc.output_gear.outside_diameter) + 2 * hp.wall_thickness + 10
        if required_height > hp.housing_height:
            issues.append(ValidationIssue(
                field="housing_parameters.housing_height",
                message=f"Housing height ({hp.housing_height} mm) is shorter than required "
                        f"({required_height:.1f} mm) for the largest gear with clearance.",
                severity="error",
            ))

        checks += 1
        # Gear meshing: centre distance must equal (d1+d2)/2
        if abs(calc.centre_distance - (calc.input_pitch_diameter + calc.output_pitch_diameter) / 2) > 0.01:
            issues.append(ValidationIssue(
                field="calculations.centre_distance",
                message="Centre distance does not match pitch diameter sum. Check gear parameters.",
                severity="error",
            ))

    # --- Housing structural checks ---
    checks += 1
    if hp.wall_thickness < 5:
        issues.append(ValidationIssue(
            field="housing_parameters.wall_thickness",
            message="Wall thickness below 5 mm may not provide adequate structural rigidity or castability.",
            severity="warning",
        ))

    checks += 1
    if hp.cover_thickness < 5:
        issues.append(ValidationIssue(
            field="housing_parameters.cover_thickness",
            message="Cover thickness below 5 mm may be too thin for fastener engagement.",
            severity="warning",
        ))

    checks += 1
    if hp.base_thickness < hp.wall_thickness:
        issues.append(ValidationIssue(
            field="housing_parameters.base_thickness",
            message="Base thickness should be at least equal to wall thickness for stability.",
            severity="warning",
        ))

    # --- Assembly checks ---
    checks += 1
    if hp.mounting_hole_diameter < 4:
        issues.append(ValidationIssue(
            field="housing_parameters.mounting_hole_diameter",
            message="Mounting hole diameter below 4 mm is too small for standard fasteners.",
            severity="warning",
        ))

    # --- Info notes ---
    checks += 1
    if gp.gear_type.value != "spur_external":
        issues.append(ValidationIssue(
            field="gear_parameters.gear_type",
            message=f"Gear type '{gp.gear_type.value}' is not fully implemented. "
                    "Geometry will use the spur-external approximation.",
            severity="info",
        ))

    checks += 1
    issues.append(ValidationIssue(
        field="_general",
        message="Tooth geometry uses a simplified involute approximation. "
                "Full load capacity, fatigue, and manufacturing validation require "
                "dedicated gear analysis software (e.g., KISSsoft, AGMA calculations).",
        severity="info",
    ))

    has_errors = any(i.severity == "error" for i in issues)
    return ValidationResult(
        is_valid=not has_errors,
        issues=issues,
        checks_run=checks,
    )
