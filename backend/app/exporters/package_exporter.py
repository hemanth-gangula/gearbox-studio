"""
Package exporter — creates a ZIP archive of all project deliverables.
Also generates AutoCAD .scr script and .lsp AutoLISP files.
"""
from __future__ import annotations

import os
import zipfile
import math

from app.schemas.design import GearboxDesign, CalculationResults


def create_zip_package(files: dict[str, str], output_path: str) -> str:
    """
    Create a ZIP archive containing all provided files.
    files: {relative_filename: absolute_path}
    """
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for rel_name, abs_path in files.items():
            if os.path.isfile(abs_path):
                zf.write(abs_path, rel_name)
    return output_path


def generate_autocad_script(design: GearboxDesign, calc: CalculationResults, output_path: str) -> str:
    """
    Generate an AutoCAD .scr script file that recreates the basic gear geometry.
    This script can be executed in AutoCAD via the SCRIPT command.
    """
    ig = calc.input_gear
    og = calc.output_gear

    lines = []
    lines.append("; Gearbox Studio — AutoCAD Script")
    lines.append(f"; Project: {design.project_info.project_name}")
    lines.append(f"; Generated: by Gearbox Studio")
    lines.append("")
    lines.append("_LAYER _M OUTLINE")
    lines.append("_LAYER _C 7 OUTLINE")
    lines.append("")
    lines.append("; --- Input Gear (Pinion) ---")
    lines.append(f"_CIRCLE 0,0 {ig.outside_diameter / 2:.3f}")
    lines.append(f"_CIRCLE 0,0 {ig.pitch_diameter / 2:.3f}")
    lines.append(f"_CIRCLE 0,0 {ig.bore_diameter / 2:.3f}")
    lines.append("")
    lines.append("; --- Output Gear ---")
    ox = calc.centre_distance
    lines.append(f"_CIRCLE {ox:.3f},0 {og.outside_diameter / 2:.3f}")
    lines.append(f"_CIRCLE {ox:.3f},0 {og.pitch_diameter / 2:.3f}")
    lines.append(f"_CIRCLE {ox:.3f},0 {og.bore_diameter / 2:.3f}")
    lines.append("")
    lines.append("; --- Center lines ---")
    lines.append("_LAYER _M CENTER")
    lines.append("_LAYER _C 1 CENTER")
    lines.append(f"_LINE {-ig.outside_diameter / 2 - 10:.3f},0 {ox + og.outside_diameter / 2 + 10:.3f},0")
    lines.append("")
    lines.append("; --- Centre distance dimension ---")
    lines.append(f"_TEXT 0,{ig.outside_diameter / 2 + 15:.3f} 3 0 a = {calc.centre_distance:.1f} mm")
    lines.append("")
    lines.append("; --- Title block ---")
    lines.append("_LAYER _M TITLEBLOCK")
    lines.append("_LAYER _C 7 TITLEBLOCK")
    lines.append("_RECTANG 0,0 180,40")
    lines.append(f"_TEXT 5,30 4 0 GEARBOX STUDIO")
    lines.append(f"_TEXT 5,16 2.5 0 {design.project_info.project_name}")
    lines.append(f"_TEXT 64,16 2.5 0 Dwg: {design.project_info.drawing_number}")
    lines.append("")
    lines.append("_ZOOM _E")

    with open(output_path, "w") as f:
        f.write("\n".join(lines))
    return output_path


def generate_autolisp_file(design: GearboxDesign, calc: CalculationResults, output_path: str) -> str:
    """
    Generate an AutoLISP .lsp file with functions to draw gearbox geometry.
    This can be loaded in AutoCAD via APPLOAD or (load "file.lsp").
    """
    ig = calc.input_gear
    og = calc.output_gear

    lines = []
    lines.append(";;; ============================================================")
    lines.append(";;; Gearbox Studio — AutoLISP Gear Drawing Routine")
    lines.append(f";;; Project: {design.project_info.project_name}")
    lines.append(";;; ============================================================")
    lines.append("")
    lines.append("(defun c:DRAWGEARBOX ( / cx cy r_out r_pitch r_bore ox)")
    lines.append("  ; Set up layers")
    lines.append('  (command "LAYER" "M" "OUTLINE" "C" 7 "OUTLINE" "")')
    lines.append('  (command "LAYER" "M" "CENTER" "C" 1 "CENTER" "")')
    lines.append('  (command "LAYER" "M" "DIMENSIONS" "C" 3 "DIMENSIONS" "")')
    lines.append("  ;")
    lines.append("  ; Input gear (pinion)")
    lines.append(f'  (setq r_out {ig.outside_diameter / 2:.3f})')
    lines.append(f'  (setq r_pitch {ig.pitch_diameter / 2:.3f})')
    lines.append(f'  (setq r_bore {ig.bore_diameter / 2:.3f})')
    lines.append('  (setq cx 0.0 cy 0.0)')
    lines.append('  (command "CIRCLE" (list cx cy) r_out)')
    lines.append('  (command "CIRCLE" (list cx cy) r_pitch)')
    lines.append('  (command "CIRCLE" (list cx cy) r_bore)')
    lines.append("  ;")
    lines.append("  ; Output gear")
    lines.append(f'  (setq ox {calc.centre_distance:.3f})')
    lines.append(f'  (setq r_out {og.outside_diameter / 2:.3f})')
    lines.append(f'  (setq r_pitch {og.pitch_diameter / 2:.3f})')
    lines.append(f'  (setq r_bore {og.bore_diameter / 2:.3f})')
    lines.append('  (command "CIRCLE" (list ox cy) r_out)')
    lines.append('  (command "CIRCLE" (list ox cy) r_pitch)')
    lines.append('  (command "CIRCLE" (list ox cy) r_bore)')
    lines.append("  ;")
    lines.append("  ; Centre line")
    lines.append('  (setvar "CLAYER" "CENTER")')
    lines.append(f'  (command "LINE" (list {-(ig.outside_diameter / 2) - 10:.3f} 0.0) (list (+ ox {og.outside_diameter / 2 + 10:.3f}) 0.0) "")')
    lines.append("  ;")
    lines.append(f'  (princ (strcat "\\nGearbox drawn. Centre distance = {calc.centre_distance:.1f} mm, Ratio = {calc.reduction_ratio:.1f}:1"))')
    lines.append("  (princ)")
    lines.append(")")
    lines.append("")
    lines.append('  (princ "\\nType DRAWGEARBOX to draw the gearbox geometry.")')
    lines.append("  (princ)")

    with open(output_path, "w") as f:
        f.write("\n".join(lines))
    return output_path
