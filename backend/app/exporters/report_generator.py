"""
Engineering report generation — PDF and Markdown.

Creates a professional engineering report from actual project data including:
cover page, project overview, design assumptions, input parameters, calculations,
gear/shaft/housing dimensions, assembly summary, drawing index, BOM,
validation results, and known limitations.
"""
from __future__ import annotations

import os
from datetime import datetime

from app.schemas.design import (
    GearboxDesign,
    CalculationResults,
    ValidationResult,
    BOM,
)
from app.calculations.gear_calcs import format_calculation_summary


def generate_markdown_report(
    design: GearboxDesign,
    calc: CalculationResults,
    validation: ValidationResult,
    bom: BOM,
    drawings: list,
    output_path: str,
) -> str:
    """Generate a Markdown engineering report."""
    lines = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Cover
    lines.append(f"# Gearbox Studio — Engineering Report\n")
    lines.append(f"**Project:** {design.project_info.project_name}\n")
    lines.append(f"**Drawing No:** {design.project_info.drawing_number}\n")
    if design.project_info.designer_name:
        lines.append(f"**Designer:** {design.project_info.designer_name}\n")
    lines.append(f"**Generated:** {now}\n")
    lines.append(f"**Units:** {design.project_info.units}\n\n")
    lines.append("---\n\n")

    # Overview
    lines.append("## 1. Project Overview\n\n")
    lines.append(
        f"This report documents the preliminary design of a single-stage "
        f"external spur gear reduction unit. The pinion has {calc.input_gear.teeth} teeth "
        f"and the output gear has {calc.output_gear.teeth} teeth, yielding a "
        f"reduction ratio of {calc.reduction_ratio:.3f}:1 at a module of {calc.module} mm.\n\n"
    )

    # Assumptions
    lines.append("## 2. Design Assumptions\n\n")
    lines.append(
        "- Standard full-depth involute spur gear teeth (ISO 53 / DIN 3960)\n"
        "- Pressure angle: " + str(calc.pressure_angle_deg) + " degrees\n"
        "- Addendum coefficient: ha* = 1.0 (standard)\n"
        "- Clearance coefficient: c* = 0.25 (standard)\n"
        "- Tooth geometry is a simplified visual approximation\n"
        "- No load capacity, fatigue, or manufacturing analysis performed\n"
        "- Material selections are proposed only, not verified\n"
        "- Bearing selection requires dedicated load and life analysis\n\n"
    )

    # Input parameters
    lines.append("## 3. Input Parameters\n\n")
    gp = design.gear_parameters
    sp = design.shaft_parameters
    hp = design.housing_parameters
    lines.append("| Parameter | Value |\n|---|---|\n")
    lines.append(f"| Gear Type | {gp.gear_type.value} |\n")
    lines.append(f"| Pinion Teeth (z1) | {gp.input_teeth} |\n")
    lines.append(f"| Gear Teeth (z2) | {gp.output_teeth} |\n")
    lines.append(f"| Module (m) | {gp.module} mm |\n")
    lines.append(f"| Pressure Angle | {gp.pressure_angle.value} degrees |\n")
    lines.append(f"| Face Width | {gp.face_width} mm |\n")
    lines.append(f"| Input Speed | {design.input_speed_rpm} rpm |\n")
    lines.append(f"| Input Shaft Diameter | {sp.input_shaft_diameter} mm |\n")
    lines.append(f"| Output Shaft Diameter | {sp.output_shaft_diameter} mm |\n")
    lines.append(f"| Housing Length | {hp.housing_length} mm |\n")
    lines.append(f"| Housing Width | {hp.housing_width} mm |\n")
    lines.append(f"| Housing Height | {hp.housing_height} mm |\n\n")

    # Calculations
    lines.append("## 4. Engineering Calculations\n\n")
    lines.append("| Parameter | Value | Formula |\n|---|---|---|\n")
    for row in format_calculation_summary(calc):
        lines.append(f"| {row['parameter']} | {row['value']} | {row['formula']} |\n")
    lines.append("\n")

    # Gear dimensions
    lines.append("## 5. Gear Dimensions\n\n")
    lines.append("### Input Gear (Pinion)\n\n")
    lines.append("| Dimension | Value |\n|---|---|\n")
    ig = calc.input_gear
    lines.append(f"| Pitch Diameter | {ig.pitch_diameter} mm |\n")
    lines.append(f"| Outside Diameter | {ig.outside_diameter} mm |\n")
    lines.append(f"| Root Diameter | {ig.root_diameter} mm |\n")
    lines.append(f"| Base Circle Diameter | {ig.base_diameter} mm |\n")
    lines.append(f"| Addendum | {ig.addendum} mm |\n")
    lines.append(f"| Dedendum | {ig.dedendum} mm |\n")
    lines.append(f"| Face Width | {ig.face_width} mm |\n")
    lines.append(f"| Bore Diameter | {ig.bore_diameter} mm |\n")
    lines.append(f"| Circular Pitch | {ig.circular_pitch} mm |\n\n")

    lines.append("### Output Gear\n\n")
    lines.append("| Dimension | Value |\n|---|---|\n")
    og = calc.output_gear
    lines.append(f"| Pitch Diameter | {og.pitch_diameter} mm |\n")
    lines.append(f"| Outside Diameter | {og.outside_diameter} mm |\n")
    lines.append(f"| Root Diameter | {og.root_diameter} mm |\n")
    lines.append(f"| Base Circle Diameter | {og.base_diameter} mm |\n")
    lines.append(f"| Addendum | {og.addendum} mm |\n")
    lines.append(f"| Dedendum | {og.dedendum} mm |\n")
    lines.append(f"| Face Width | {og.face_width} mm |\n")
    lines.append(f"| Bore Diameter | {og.bore_diameter} mm |\n\n")

    # Shaft and housing dimensions
    lines.append("## 6. Shaft and Housing Dimensions\n\n")
    lines.append("| Component | Dimension | Value |\n|---|---|---|\n")
    lines.append(f"| Input Shaft | Diameter | {sp.input_shaft_diameter} mm |\n")
    lines.append(f"| Input Shaft | Length | {sp.input_shaft_length} mm |\n")
    lines.append(f"| Input Shaft | Bearing Seat | Ø{sp.bearing_seat_diameter_in} mm |\n")
    lines.append(f"| Output Shaft | Diameter | {sp.output_shaft_diameter} mm |\n")
    lines.append(f"| Output Shaft | Length | {sp.output_shaft_length} mm |\n")
    lines.append(f"| Output Shaft | Bearing Seat | Ø{sp.bearing_seat_diameter_out} mm |\n")
    lines.append(f"| Housing | Length × Width × Height | {hp.housing_length} × {hp.housing_width} × {hp.housing_height} mm |\n")
    lines.append(f"| Housing | Wall Thickness | {hp.wall_thickness} mm |\n")
    lines.append(f"| Housing | Cover Thickness | {hp.cover_thickness} mm |\n\n")

    # Assembly summary
    lines.append("## 7. Assembly Summary\n\n")
    lines.append(f"- Centre Distance: {calc.centre_distance} mm\n")
    lines.append(f"- Reduction Ratio: {calc.reduction_ratio:.3f} : 1\n")
    lines.append(f"- Output Speed: {calc.output_speed_rpm} rpm\n")
    lines.append(f"- Total Components: {bom.total_parts}\n\n")

    # Drawing index
    lines.append("## 8. Drawing Index\n\n")
    lines.append("| No. | Drawing Name | Format |\n|---|---|---|\n")
    for i, d in enumerate(drawings, 1):
        lines.append(f"| {i} | {d.name} | DXF |\n")
    lines.append("\n")

    # BOM
    lines.append("## 9. Bill of Materials\n\n")
    lines.append("| Item | Part No. | Name | Qty | Material | Validation |\n")
    lines.append("|---|---|---|---|---|---|\n")
    for c in bom.components:
        lines.append(f"| {c.item_number} | {c.part_number} | {c.name} | {c.quantity} | {c.material} | {c.validation_status} |\n")
    lines.append("\n")

    # Validation
    lines.append("## 10. Validation Results\n\n")
    lines.append(f"- Overall Valid: {'YES' if validation.is_valid else 'NO'}\n")
    lines.append(f"- Checks Run: {validation.checks_run}\n")
    if validation.issues:
        lines.append("\n| Severity | Field | Message |\n|---|---|---|\n")
        for issue in validation.issues:
            lines.append(f"| {issue.severity.upper()} | {issue.field} | {issue.message} |\n")
    lines.append("\n")

    # Limitations
    lines.append("## 11. Known Limitations\n\n")
    lines.append(
        "- Tooth geometry uses a simplified involute approximation, not manufacturing-accurate.\n"
        "- No tooth bending stress, contact stress, or scuffing analysis performed.\n"
        "- No fatigue life or reliability calculation performed.\n"
        "- Bearing selection is proposed only; actual selection requires load and life analysis.\n"
        "- Material selections are proposed only and require verification.\n"
        "- Housing structural analysis (FEA) not performed.\n"
        "- Thermal analysis not performed.\n"
        "- Lubrication selection not performed.\n"
        "- Manufacturing tolerances and surface finish not specified.\n\n"
    )

    # Suggested checks
    lines.append("## 12. Suggested Engineering Checks Before Manufacture\n\n")
    lines.append(
        "1. Perform AGMA or ISO 6336 gear tooth bending and contact stress analysis.\n"
        "2. Verify bearing selection with proper load and life calculations (ISO 281).\n"
        "3. Perform shaft fatigue and deflection analysis.\n"
        "4. Conduct housing FEA for stiffness and resonance.\n"
        "5. Specify manufacturing tolerances (DIN 3962/3967).\n"
        "6. Select appropriate lubricant and verify film thickness.\n"
        "7. Perform thermal analysis and verify heat dissipation.\n"
        "8. Verify all geometric interferences in a CAD assembly model.\n"
        "9. Create manufacturing drawings with proper GD&T.\n"
        "10. Conduct prototype testing under design loads.\n\n"
    )

    lines.append("---\n")
    lines.append("*This report was generated by Gearbox Studio. "
                 "It represents preliminary design output and does NOT constitute "
                 "a certified engineering analysis.*\n")

    with open(output_path, "w", encoding="utf-8") as f:
        f.writelines(lines)
    return output_path


def generate_pdf_report(
    design: GearboxDesign,
    calc: CalculationResults,
    validation: ValidationResult,
    bom: BOM,
    drawings: list,
    output_path: str,
) -> str:
    """Generate a PDF engineering report using reportlab."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image,
    )
    from reportlab.lib.enums import TA_CENTER

    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        topMargin=20 * mm, bottomMargin=20 * mm,
        leftMargin=18 * mm, rightMargin=18 * mm,
    )
    styles = getSampleStyleSheet()
    elements = []

    title_style = ParagraphStyle("Title", parent=styles["Title"], fontSize=22, spaceAfter=6)
    subtitle_style = ParagraphStyle("Subtitle", parent=styles["Normal"], fontSize=11, alignment=TA_CENTER, textColor=colors.grey)
    h2_style = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=14, spaceBefore=12, spaceAfter=6, textColor=colors.HexColor("#1a365d"))
    h3_style = ParagraphStyle("H3", parent=styles["Heading3"], fontSize=12, spaceBefore=8, spaceAfter=4, textColor=colors.HexColor("#2b6cb0"))
    body_style = ParagraphStyle("Body", parent=styles["Normal"], fontSize=10, spaceAfter=4)
    small_style = ParagraphStyle("Small", parent=styles["Normal"], fontSize=8, textColor=colors.grey)

    # Cover page
    elements.append(Spacer(1, 60 * mm))
    elements.append(Paragraph("Gearbox Studio", title_style))
    elements.append(Paragraph("Engineering Design Report", subtitle_style))
    elements.append(Spacer(1, 20 * mm))
    elements.append(Paragraph(f"<b>Project:</b> {design.project_info.project_name}", body_style))
    elements.append(Paragraph(f"<b>Drawing No:</b> {design.project_info.drawing_number}", body_style))
    if design.project_info.designer_name:
        elements.append(Paragraph(f"<b>Designer:</b> {design.project_info.designer_name}", body_style))
    elements.append(Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}", body_style))
    elements.append(Paragraph(f"<b>Units:</b> {design.project_info.units}", body_style))
    elements.append(PageBreak())

    # Overview
    elements.append(Paragraph("1. Project Overview", h2_style))
    elements.append(Paragraph(
        f"This report documents the preliminary design of a single-stage external "
        f"spur gear reduction unit. The pinion has {calc.input_gear.teeth} teeth and the "
        f"output gear has {calc.output_gear.teeth} teeth, yielding a reduction ratio of "
        f"{calc.reduction_ratio:.3f}:1 at a module of {calc.module} mm.",
        body_style,
    ))

    # Assumptions
    elements.append(Paragraph("2. Design Assumptions", h2_style))
    assumptions = [
        "Standard full-depth involute spur gear teeth (ISO 53 / DIN 3960)",
        f"Pressure angle: {calc.pressure_angle_deg} degrees",
        "Addendum coefficient: ha* = 1.0 (standard)",
        "Clearance coefficient: c* = 0.25 (standard)",
        "Tooth geometry is a simplified visual approximation",
        "No load capacity, fatigue, or manufacturing analysis performed",
        "Material selections are proposed only, not verified",
    ]
    for a in assumptions:
        elements.append(Paragraph(f"• {a}", body_style))

    # Parameters
    elements.append(Paragraph("3. Input Parameters", h2_style))
    param_data = [
        ["Parameter", "Value"],
        ["Gear Type", design.gear_parameters.gear_type.value],
        ["Pinion Teeth (z1)", str(design.gear_parameters.input_teeth)],
        ["Gear Teeth (z2)", str(design.gear_parameters.output_teeth)],
        ["Module (m)", f"{design.gear_parameters.module} mm"],
        ["Pressure Angle", f"{design.gear_parameters.pressure_angle.value}°"],
        ["Face Width", f"{design.gear_parameters.face_width} mm"],
        ["Input Speed", f"{design.input_speed_rpm} rpm"],
        ["Input Shaft Diameter", f"{design.shaft_parameters.input_shaft_diameter} mm"],
        ["Output Shaft Diameter", f"{design.shaft_parameters.output_shaft_diameter} mm"],
        ["Housing L × W × H", f"{design.housing_parameters.housing_length} × {design.housing_parameters.housing_width} × {design.housing_parameters.housing_height} mm"],
    ]
    t = Table(param_data, colWidths=[80*mm, 95*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2B5797")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f4f8")]),
    ]))
    elements.append(t)

    # Calculations
    elements.append(Paragraph("4. Engineering Calculations", h2_style))
    calc_data = [["Parameter", "Value", "Formula"]]
    for row in format_calculation_summary(calc):
        calc_data.append([row["parameter"], row["value"], row["formula"]])
    t = Table(calc_data, colWidths=[65*mm, 45*mm, 65*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2B5797")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f4f8")]),
    ]))
    elements.append(t)

    # Gear dimensions
    elements.append(Paragraph("5. Gear Dimensions", h2_style))
    elements.append(Paragraph("Input Gear (Pinion)", h3_style))
    ig = calc.input_gear
    ig_data = [["Dimension", "Value"]]
    for label, val in [
        ("Pitch Diameter", f"{ig.pitch_diameter} mm"),
        ("Outside Diameter", f"{ig.outside_diameter} mm"),
        ("Root Diameter", f"{ig.root_diameter} mm"),
        ("Base Circle Diameter", f"{ig.base_diameter} mm"),
        ("Addendum", f"{ig.addendum} mm"),
        ("Dedendum", f"{ig.dedendum} mm"),
        ("Face Width", f"{ig.face_width} mm"),
        ("Bore Diameter", f"{ig.bore_diameter} mm"),
    ]:
        ig_data.append([label, val])
    t = Table(ig_data, colWidths=[80*mm, 95*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2B5797")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(t)

    elements.append(Paragraph("Output Gear", h3_style))
    og = calc.output_gear
    og_data = [["Dimension", "Value"]]
    for label, val in [
        ("Pitch Diameter", f"{og.pitch_diameter} mm"),
        ("Outside Diameter", f"{og.outside_diameter} mm"),
        ("Root Diameter", f"{og.root_diameter} mm"),
        ("Base Circle Diameter", f"{og.base_diameter} mm"),
        ("Addendum", f"{og.addendum} mm"),
        ("Dedendum", f"{og.dedendum} mm"),
        ("Face Width", f"{og.face_width} mm"),
        ("Bore Diameter", f"{og.bore_diameter} mm"),
    ]:
        og_data.append([label, val])
    t = Table(og_data, colWidths=[80*mm, 95*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2B5797")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(t)

    # BOM
    elements.append(Paragraph("6. Bill of Materials", h2_style))
    bom_data = [["Item", "Part No.", "Name", "Qty", "Material", "Status"]]
    for c in bom.components:
        bom_data.append([
            str(c.item_number), c.part_number, c.name, str(c.quantity),
            c.material, c.validation_status,
        ])
    t = Table(bom_data, colWidths=[12*mm, 32*mm, 35*mm, 12*mm, 50*mm, 25*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2B5797")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f4f8")]),
    ]))
    elements.append(t)

    # Validation
    elements.append(Paragraph("7. Validation Results", h2_style))
    elements.append(Paragraph(f"<b>Overall Valid:</b> {'YES' if validation.is_valid else 'NO'}  "
                             f"<b>Checks Run:</b> {validation.checks_run}", body_style))
    if validation.issues:
        val_data = [["Severity", "Field", "Message"]]
        for issue in validation.issues:
            val_data.append([issue.severity.upper(), issue.field, issue.message])
        t = Table(val_data, colWidths=[22*mm, 40*mm, 108*mm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2B5797")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f4f8")]),
        ]))
        elements.append(t)

    # Limitations
    elements.append(Paragraph("8. Known Limitations", h2_style))
    limitations = [
        "Tooth geometry uses a simplified involute approximation, not manufacturing-accurate.",
        "No tooth bending stress, contact stress, or scuffing analysis performed.",
        "No fatigue life or reliability calculation performed.",
        "Bearing selection is proposed only; actual selection requires load and life analysis.",
        "Material selections are proposed only and require verification.",
        "Housing structural analysis (FEA) not performed.",
        "Thermal analysis not performed.",
        "Lubrication selection not performed.",
        "Manufacturing tolerances and surface finish not specified.",
    ]
    for l in limitations:
        elements.append(Paragraph(f"• {l}", body_style))

    elements.append(Spacer(1, 10 * mm))
    elements.append(Paragraph(
        "This report was generated by Gearbox Studio. It represents preliminary "
        "design output and does NOT constitute a certified engineering analysis.",
        small_style,
    ))

    doc.build(elements)
    return output_path
