'use client';

import { useEffect, useState } from 'react';
import { Cog, Calculator, AlertTriangle, CheckCircle2 } from 'lucide-react';
import { Card, SectionHeader, EmptyState, Button, Badge, LoadingState } from '@/components/ui';
import { useDesign } from '@/hooks/use-design';
import { api } from '@/lib/api';
import type { CalculationResults, ValidationResult } from '@/types';
import Link from 'next/link';

export default function ParametersPage() {
  const { design, designId, designRecord } = useDesign();
  const [calcs, setCalcs] = useState<CalculationResults | null>(null);
  const [validation, setValidation] = useState<ValidationResult | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (designRecord?.calculations) {
      setCalcs(designRecord.calculations);
      setValidation(designRecord.validation);
    } else if (designId) {
      setLoading(true);
      Promise.all([api.getCalculations(designId), api.getValidation(designId)])
        .then(([c, v]) => { setCalcs(c); setValidation(v); })
        .catch(() => {})
        .finally(() => setLoading(false));
    }
  }, [designId, designRecord]);

  if (loading) return <LoadingState message="Loading calculations..." />;

  if (!calcs) {
    return (
      <div className="p-6">
        <EmptyState
          icon={<Calculator className="w-12 h-12" />}
          title="No Calculation Results"
          message="Generate a design to see engineering calculations and validation results."
          action={<Link href="/new-design"><Button>Configure Design</Button></Link>}
        />
      </div>
    );
  }

  const ig = calcs.input_gear;
  const og = calcs.output_gear;

  const calcRows = [
    { param: 'Pitch Diameter (Pinion)', value: `${calcs.input_pitch_diameter} mm`, formula: 'd₁ = m × z₁' },
    { param: 'Pitch Diameter (Gear)', value: `${calcs.output_pitch_diameter} mm`, formula: 'd₂ = m × z₂' },
    { param: 'Centre Distance', value: `${calcs.centre_distance} mm`, formula: 'a = (d₁ + d₂) / 2' },
    { param: 'Reduction Ratio', value: `${calcs.reduction_ratio.toFixed(3)} : 1`, formula: 'i = z₂ / z₁' },
    { param: 'Output Speed', value: `${calcs.output_speed_rpm.toFixed(1)} rpm`, formula: 'n₂ = n₁ / i' },
    { param: 'Pressure Angle', value: `${calcs.pressure_angle_deg}°`, formula: 'α (given)' },
    { param: 'Module', value: `${calcs.module} mm`, formula: 'm (given)' },
    { param: 'Circular Pitch', value: `${calcs.circular_pitch} mm`, formula: 'p = π × m' },
    { param: 'Base Circle (Pinion)', value: `${calcs.base_circle_input} mm`, formula: 'd_b1 = d₁ × cos(α)' },
    { param: 'Base Circle (Gear)', value: `${calcs.base_circle_output} mm`, formula: 'd_b2 = d₂ × cos(α)' },
  ];

  const gearDims = (g: typeof ig, name: string) => [
    { dim: 'Teeth', val: `${g.teeth}` },
    { dim: 'Pitch Diameter', val: `${g.pitch_diameter} mm` },
    { dim: 'Outside Diameter', val: `${g.outside_diameter} mm` },
    { dim: 'Root Diameter', val: `${g.root_diameter} mm` },
    { dim: 'Base Circle', val: `${g.base_diameter} mm` },
    { dim: 'Addendum', val: `${g.addendum} mm` },
    { dim: 'Dedendum', val: `${g.dedendum} mm` },
    { dim: 'Face Width', val: `${g.face_width} mm` },
    { dim: 'Bore', val: `${g.bore_diameter} mm` },
    { dim: 'Circular Pitch', val: `${g.circular_pitch} mm` },
  ];

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <div className="mb-6">
        <h1 className="text-xl font-bold mb-1" style={{ color: 'var(--workspace-text)' }}>Design Parameters</h1>
        <p className="text-sm" style={{ color: 'var(--workspace-text-muted)' }}>Engineering calculations and design validation</p>
      </div>

      {/* Validation status */}
      {validation && (
        <Card className="p-4 mb-4">
          <div className="flex items-center gap-3 mb-2">
            {validation.is_valid ? (
              <Badge variant="success"><CheckCircle2 className="w-3 h-3" /> Design Valid</Badge>
            ) : (
              <Badge variant="error"><AlertTriangle className="w-3 h-3" /> Issues Found</Badge>
            )}
            <span className="text-xs" style={{ color: 'var(--workspace-text-muted)' }}>{validation.checks_run} checks</span>
          </div>
          {validation.issues.length > 0 && (
            <div className="space-y-1">
              {validation.issues.map((issue, i) => (
                <div key={i} className="flex items-start gap-2 text-xs py-1">
                  <Badge variant={issue.severity as any}>{issue.severity}</Badge>
                  <span style={{ color: 'var(--workspace-text-muted)' }}>{issue.message}</span>
                </div>
              ))}
            </div>
          )}
        </Card>
      )}

      {/* Calculations */}
      <Card className="p-4 mb-4">
        <SectionHeader title="Engineering Calculations" subtitle="Spur gear pair — ISO 53 / DIN 3960" />
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr style={{ borderBottom: '1px solid var(--workspace-border)' }}>
                <th className="text-left py-2 px-2 tech-label">Parameter</th>
                <th className="text-left py-2 px-2 tech-label">Value</th>
                <th className="text-left py-2 px-2 tech-label">Formula</th>
              </tr>
            </thead>
            <tbody>
              {calcRows.map((row, i) => (
                <tr key={i} style={{ borderBottom: '1px solid var(--workspace-border)' }}>
                  <td className="py-2 px-2" style={{ color: 'var(--workspace-text)' }}>{row.param}</td>
                  <td className="py-2 px-2 font-mono" style={{ color: 'var(--workspace-text)' }}>{row.value}</td>
                  <td className="py-2 px-2 font-mono text-xs" style={{ color: 'var(--workspace-text-muted)' }}>{row.formula}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Gear Dimensions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card className="p-4">
          <SectionHeader title="Input Gear (Pinion)" subtitle={`z=${ig.teeth}, m=${ig.module} mm`} />
          <table className="w-full text-sm">
            <tbody>
              {gearDims(ig, 'Input').map((row, i) => (
                <tr key={i} style={{ borderBottom: '1px solid var(--workspace-border)' }}>
                  <td className="py-1.5 px-2" style={{ color: 'var(--workspace-text-muted)' }}>{row.dim}</td>
                  <td className="py-1.5 px-2 font-mono text-right" style={{ color: 'var(--workspace-text)' }}>{row.val}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>

        <Card className="p-4">
          <SectionHeader title="Output Gear" subtitle={`z=${og.teeth}, m=${og.module} mm`} />
          <table className="w-full text-sm">
            <tbody>
              {gearDims(og, 'Output').map((row, i) => (
                <tr key={i} style={{ borderBottom: '1px solid var(--workspace-border)' }}>
                  <td className="py-1.5 px-2" style={{ color: 'var(--workspace-text-muted)' }}>{row.dim}</td>
                  <td className="py-1.5 px-2 font-mono text-right" style={{ color: 'var(--workspace-text)' }}>{row.val}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      </div>

      {/* Shaft & Housing Summary */}
      <div className="mt-4">
        <Card className="p-4">
          <SectionHeader title="Shaft &amp; Housing Dimensions" />
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div><div className="tech-label">Input Shaft Ø</div><div className="text-sm font-mono mt-1" style={{ color: 'var(--workspace-text)' }}>{design.shaft_parameters.input_shaft_diameter} mm</div></div>
            <div><div className="tech-label">Output Shaft Ø</div><div className="text-sm font-mono mt-1" style={{ color: 'var(--workspace-text)' }}>{design.shaft_parameters.output_shaft_diameter} mm</div></div>
            <div><div className="tech-label">Housing L×W×H</div><div className="text-sm font-mono mt-1" style={{ color: 'var(--workspace-text)' }}>{design.housing_parameters.housing_length}×{design.housing_parameters.housing_width}×{design.housing_parameters.housing_height}</div></div>
            <div><div className="tech-label">Wall Thickness</div><div className="text-sm font-mono mt-1" style={{ color: 'var(--workspace-text)' }}>{design.housing_parameters.wall_thickness} mm</div></div>
          </div>
        </Card>
      </div>
    </div>
  );
}
