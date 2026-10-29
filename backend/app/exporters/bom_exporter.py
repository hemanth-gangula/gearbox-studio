"""
Bill of Materials (BOM) export utilities.

Generates BOM data from the component list and exports to CSV and XLSX.
"""
from __future__ import annotations

import csv
import os
import io
from app.schemas.design import BOM, ComponentInfo, GearboxDesign, CalculationResults


def build_bom(components: list[ComponentInfo]) -> BOM:
    """Build a BOM model from a list of ComponentInfo."""
    return BOM(
        components=components,
        total_parts=len(components),
    )


def export_bom_csv(bom: BOM, output_path: str) -> str:
    """Export the BOM to a CSV file."""
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Item", "Part Number", "Component Name", "Qty",
            "Material", "Principal Dimensions", "Notes", "Validation Status",
        ])
        for c in bom.components:
            writer.writerow([
                c.item_number, c.part_number, c.name, c.quantity,
                c.material, c.principal_dimensions, c.notes, c.validation_status,
            ])
    return output_path


def export_bom_xlsx(bom: BOM, output_path: str) -> str:
    """Export the BOM to an Excel file."""
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side

    wb = Workbook()
    ws = wb.active
    ws.title = "Bill of Materials"

    # Header styling
    header_font = Font(bold=True, size=11)
    header_fill = PatternFill(start_color="2B5797", end_color="2B5797", fill_type="solid")
    header_font_white = Font(bold=True, size=11, color="FFFFFF")
    thin_border = Border(
        left=Side(style="thin"), right=Side(style="thin"),
        top=Side(style="thin"), bottom=Side(style="thin"),
    )

    headers = [
        "Item", "Part Number", "Component Name", "Qty",
        "Material", "Principal Dimensions", "Notes", "Validation Status",
    ]
    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=h)
        cell.font = header_font_white
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = thin_border

    for row, c in enumerate(bom.components, 2):
        ws.cell(row=row, column=1, value=c.item_number).border = thin_border
        ws.cell(row=row, column=2, value=c.part_number).border = thin_border
        ws.cell(row=row, column=3, value=c.name).border = thin_border
        ws.cell(row=row, column=4, value=c.quantity).border = thin_border
        ws.cell(row=row, column=5, value=c.material).border = thin_border
        ws.cell(row=row, column=6, value=c.principal_dimensions).border = thin_border
        ws.cell(row=row, column=7, value=c.notes).border = thin_border
        ws.cell(row=row, column=8, value=c.validation_status).border = thin_border

    # Auto-fit column widths
    col_widths = [6, 22, 28, 5, 24, 35, 40, 18]
    for col, w in enumerate(col_widths, 1):
        ws.column_dimensions[chr(64 + col)].width = w

    # Title row
    ws.insert_rows(1)
    ws.cell(row=1, column=1, value="GEARBOX STUDIO — BILL OF MATERIALS").font = Font(bold=True, size=14)
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=8)

    wb.save(output_path)
    return output_path
