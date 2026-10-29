# Engineering Assumptions

## Scope

This document describes the engineering assumptions used in the Gearbox Studio calculation and modeling pipeline. The application performs **preliminary design calculations** for a single-stage external spur gear reduction unit. It does **not** perform load capacity analysis, fatigue life calculation, or manufacturing readiness verification.

## Gear Standard

- **Standard**: ISO 53 / DIN 3960 for spur gears
- **Tooth system**: Standard full-depth involute
- **Addendum coefficient**: ha* = 1.0
- **Clearance coefficient**: c* = 0.25
- **Pressure angles supported**: 14.5°, 20°, 25°
- **Default pressure angle**: 20°

## Calculation Formulas

| Parameter | Formula | Notes |
|-----------|---------|-------|
| Pitch diameter | d = m × z | m = module, z = tooth count |
| Centre distance | a = (d₁ + d₂) / 2 | Nominal, no profile shift |
| Reduction ratio | i = z₂ / z₁ | Ideal, no slip |
| Output speed | n₂ = n₁ / i | n₁ = input speed |
| Base circle | db = d × cos(α) | α = pressure angle |
| Addendum | ha = m | Standard full-depth |
| Dedendum | hf = 1.25 × m | Standard + clearance |
| Outside diameter | da = d + 2 × ha | Tip circle |
| Root diameter | df = d - 2 × hf | Root circle |
| Circular pitch | p = π × m | |
| Tooth thickness | s = p / 2 | On pitch circle |

## Default Configuration

| Parameter | Value |
|-----------|-------|
| Input gear teeth (z₁) | 20 |
| Output gear teeth (z₂) | 60 |
| Module (m) | 2.0 mm |
| Pressure angle (α) | 20° |
| Face width | 20 mm |
| Input speed | 1450 rpm |

**Expected results:**
- Input pitch diameter: 40 mm
- Output pitch diameter: 120 mm
- Centre distance: 80 mm
- Reduction ratio: 3:1
- Output speed: 483.33 rpm

## Tooth Geometry

The 3D model uses a **simplified involute approximation** for visualization. The tooth profile is generated as a trapezoidal form with:
- Tip (addendum circle) at r = d/2 + m
- Root (dedendum circle) at r = d/2 - 1.25m
- Flank transition with straight lines

This is **not** a manufacturing-accurate involute profile. For manufacturing:
- Use KISSsoft, GearTrax, or similar for proper tooth generation
- Apply profile shift corrections as needed
- Specify manufacturing tolerances per DIN 3962/3967

## Material Selections (Proposed)

| Component | Proposed Material | Notes |
|-----------|------------------|-------|
| Gears | Steel C45 | Requires heat treatment verification |
| Shafts | Steel C45 | Requires fatigue analysis |
| Housing | Cast Iron GG25 | Requires FEA verification |
| Bearings | Bearing Steel 100Cr6 | Requires load/life analysis |
| Keys | Steel C45 | Standard rectangular keys |
| Fasteners | Steel grade 8.8 | Standard hex bolts |

All material selections are **proposed** and require engineering verification before manufacture.

## Limitations

1. No tooth bending stress analysis (AGMA 2001 / ISO 6336)
2. No contact (Hertzian) stress analysis
3. No scuffing or wear analysis
4. No fatigue life or reliability calculation
5. No bearing life calculation (ISO 281)
6. No shaft fatigue or deflection analysis
7. No housing FEA (stiffness, resonance)
8. No thermal analysis
9. No lubrication selection or film thickness verification
10. No manufacturing tolerance specification
11. Tooth geometry is a visual approximation
12. Bearing selection requires dedicated load analysis
13. Housing structural analysis not performed

## Suggested Engineering Checks Before Manufacture

1. Perform AGMA or ISO 6336 gear tooth bending and contact stress analysis
2. Verify bearing selection with proper load and life calculations (ISO 281)
3. Perform shaft fatigue and deflection analysis
4. Conduct housing FEA for stiffness and resonance
5. Specify manufacturing tolerances (DIN 3962/3967)
6. Select appropriate lubricant and verify film thickness
7. Perform thermal analysis and verify heat dissipation
8. Verify all geometric interferences in a CAD assembly model
9. Create manufacturing drawings with proper GD&T
10. Conduct prototype testing under design loads
