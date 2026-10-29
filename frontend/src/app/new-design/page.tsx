'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  RotateCcw, Save, Play, ChevronDown, ChevronRight,
  Info, AlertTriangle, CheckCircle2, Cog, Settings, Building, Boxes, Wrench,
} from 'lucide-react';
import { Card, Button, Badge, SectionHeader } from '@/components/ui';
import { useDesign } from '@/hooks/use-design';
import { api } from '@/lib/api';
import type { ValidationResult, CalculationResults } from '@/types';

function Field({ label, unit, children, error }: { label: string; unit?: string; children: React.ReactNode; error?: string }) {
  return (
    <div className="flex flex-col gap-1">
      <label className="tech-label flex items-center gap-1">
        {label}
        {unit && <span className="text-[10px] opacity-60">({unit})</span>}
      </label>
      {children}
      {error && <span className="text-xs text-red-400">{error}</span>}
    </div>
  );
}

function NumberInput({ value, onChange, step = 0.1, min }: { value: number; onChange: (v: number) => void; step?: number; min?: number }) {
  return (
    <input
      type="number"
      value={value}
      step={step}
      min={min}
      onChange={e => onChange(parseFloat(e.target.value) || 0)}
      className="eng-input"
    />
  );
}

function CollapsibleSection({ title, icon, children, defaultOpen = false }: { title: string; icon: React.ReactNode; children: React.ReactNode; defaultOpen?: boolean }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <Card className="overflow-hidden">
      <button onClick={() => setOpen(!open)} className="w-full flex items-center gap-2 px-4 py-3 text-left">
        {open ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
        {icon}
        <span className="font-medium text-sm" style={{ color: 'var(--workspace-text)' }}>{title}</span>
      </button>
      {open && <div className="px-4 pb-4 pt-1 grid grid-cols-2 md:grid-cols-3 gap-3">{children}</div>}
    </Card>
  );
}

export default function NewDesignPage() {
  const router = useRouter();
  const { design, setDesign, generate, isGenerating, job } = useDesign();
  const [validation, setValidation] = useState<ValidationResult | null>(null);
  const [calcs, setCalcs] = useState<CalculationResults | null>(null);
  const [showSummary, setShowSummary] = useState(false);

  const gp = design.gear_parameters;
  const sp = design.shaft_parameters;
  const hp = design.housing_parameters;
  const ap = design.assembly_parameters;
  const pi = design.project_info;

  const update = (section: keyof typeof design, patch: Record<string, any>) => {
    setDesign({ ...design, [section]: { ...(design as any)[section], ...patch } });
    setValidation(null);
    setCalcs(null);
  };

  const updateProject = (patch: Record<string, any>) => {
    setDesign({ ...design, project_info: { ...pi, ...patch } });
  };

  const handleValidate = async () => {
    try {
      const [v, c] = await Promise.all([api.validate(design), api.calculate(design)]);
      setValidation(v);
      setCalcs(c);
      setShowSummary(true);
    } catch (e) {
      console.error(e);
    }
  };

  const handleReset = () => {
    setDesign({
      project_info: { project_name: 'Single-Stage Spur Gearbox', project_description: '', designer_name: '', units: 'mm', drawing_scale: '1:1', drawing_number: 'GB-001' },
      gear_parameters: { gear_type: 'spur_external', input_teeth: 20, output_teeth: 60, module: 2.0, pressure_angle: '20', face_width: 20.0, backlash: 0.0, input_bore: 15.0, output_bore: 25.0 },
      shaft_parameters: { input_shaft_diameter: 15.0, output_shaft_diameter: 25.0, input_shaft_length: 120.0, output_shaft_length: 140.0, shaft_shoulder: 3.0, keyway_width: 5.0, keyway_height: 5.0, bearing_seat_diameter_in: 17.0, bearing_seat_diameter_out: 30.0 },
      housing_parameters: { housing_length: 200.0, housing_width: 80.0, housing_height: 160.0, wall_thickness: 10.0, cover_thickness: 12.0, base_thickness: 15.0, mounting_hole_diameter: 10.0, mounting_hole_count: 4 },
      assembly_parameters: { bearing_arrangement: 'simple', gear_axial_offset: 0.0, input_shaft_z: 0.0, cover_fastener_diameter: 6.0, include_fasteners: true, include_keys: true, include_bearings: true },
      input_speed_rpm: 1450.0,
    });
    setValidation(null);
    setCalcs(null);
    setShowSummary(false);
  };

  const handleGenerate = async () => {
    await generate();
    router.push('/');
  };

  return (
    <div className="p-6 max-w-5xl mx-auto pb-12">
      <div className="mb-6">
        <h1 className="text-xl font-bold mb-1" style={{ color: 'var(--workspace-text)' }}>New Gearbox Design</h1>
        <p className="text-sm" style={{ color: 'var(--workspace-text-muted)' }}>
          Configure parameters for a single-stage external spur gear reduction unit
        </p>
      </div>

      {/* Project Info */}
      <CollapsibleSection title="Project Information" icon={<Info className="w-4 h-4 text-blue-500" />} defaultOpen>
        <Field label="Project Name"><input className="eng-input" value={pi.project_name} onChange={e => updateProject({ project_name: e.target.value })} /></Field>
        <Field label="Project Description"><input className="eng-input" value={pi.project_description} onChange={e => updateProject({ project_description: e.target.value })} /></Field>
        <Field label="Designer Name"><input className="eng-input" value={pi.designer_name} onChange={e => updateProject({ designer_name: e.target.value })} /></Field>
        <Field label="Units"><input className="eng-input" value={pi.units} onChange={e => updateProject({ units: e.target.value })} /></Field>
        <Field label="Drawing Scale"><input className="eng-input" value={pi.drawing_scale} onChange={e => updateProject({ drawing_scale: e.target.value })} /></Field>
        <Field label="Drawing Number"><input className="eng-input" value={pi.drawing_number} onChange={e => updateProject({ drawing_number: e.target.value })} /></Field>
      </CollapsibleSection>

      {/* Gear Parameters */}
      <div className="mt-3">
        <CollapsibleSection title="Gear Parameters" icon={<Cog className="w-4 h-4 text-amber-500" />} defaultOpen>
          <Field label="Gear Type">
            <select className="eng-input" value={gp.gear_type} onChange={e => update('gear_parameters', { gear_type: e.target.value })}>
              <option value="spur_external">Spur External</option>
              <option value="spur_internal">Spur Internal (approx.)</option>
              <option value="helical_external">Helical External (approx.)</option>
            </select>
          </Field>
          <Field label="Input Gear Teeth (z₁)"><NumberInput value={gp.input_teeth} step={1} min={8} onChange={v => update('gear_parameters', { input_teeth: v })} /></Field>
          <Field label="Output Gear Teeth (z₂)"><NumberInput value={gp.output_teeth} step={1} min={8} onChange={v => update('gear_parameters', { output_teeth: v })} /></Field>
          <Field label="Module (m)" unit="mm"><NumberInput value={gp.module} step={0.25} min={0.1} onChange={v => update('gear_parameters', { module: v })} /></Field>
          <Field label="Pressure Angle">
            <select className="eng-input" value={gp.pressure_angle} onChange={e => update('gear_parameters', { pressure_angle: e.target.value })}>
              <option value="14.5">14.5°</option>
              <option value="20">20°</option>
              <option value="25">25°</option>
            </select>
          </Field>
          <Field label="Face Width" unit="mm"><NumberInput value={gp.face_width} step={1} min={1} onChange={v => update('gear_parameters', { face_width: v })} /></Field>
          <Field label="Backlash" unit="mm"><NumberInput value={gp.backlash} step={0.01} min={0} onChange={v => update('gear_parameters', { backlash: v })} /></Field>
          <Field label="Input Gear Bore" unit="mm"><NumberInput value={gp.input_bore} step={0.5} min={1} onChange={v => update('gear_parameters', { input_bore: v })} /></Field>
          <Field label="Output Gear Bore" unit="mm"><NumberInput value={gp.output_bore} step={0.5} min={1} onChange={v => update('gear_parameters', { output_bore: v })} /></Field>
        </CollapsibleSection>
      </div>

      {/* Shaft Parameters */}
      <div className="mt-3">
        <CollapsibleSection title="Shaft Parameters" icon={<Wrench className="w-4 h-4 text-cyan-500" />}>
          <Field label="Input Shaft Diameter" unit="mm"><NumberInput value={sp.input_shaft_diameter} step={0.5} min={1} onChange={v => update('shaft_parameters', { input_shaft_diameter: v })} /></Field>
          <Field label="Output Shaft Diameter" unit="mm"><NumberInput value={sp.output_shaft_diameter} step={0.5} min={1} onChange={v => update('shaft_parameters', { output_shaft_diameter: v })} /></Field>
          <Field label="Input Shaft Length" unit="mm"><NumberInput value={sp.input_shaft_length} step={5} min={10} onChange={v => update('shaft_parameters', { input_shaft_length: v })} /></Field>
          <Field label="Output Shaft Length" unit="mm"><NumberInput value={sp.output_shaft_length} step={5} min={10} onChange={v => update('shaft_parameters', { output_shaft_length: v })} /></Field>
          <Field label="Shaft Shoulder" unit="mm"><NumberInput value={sp.shaft_shoulder} step={0.5} min={0.5} onChange={v => update('shaft_parameters', { shaft_shoulder: v })} /></Field>
          <Field label="Keyway Width" unit="mm"><NumberInput value={sp.keyway_width} step={0.5} min={1} onChange={v => update('shaft_parameters', { keyway_width: v })} /></Field>
          <Field label="Keyway Height" unit="mm"><NumberInput value={sp.keyway_height} step={0.5} min={1} onChange={v => update('shaft_parameters', { keyway_height: v })} /></Field>
          <Field label="Input Bearing Seat Ø" unit="mm"><NumberInput value={sp.bearing_seat_diameter_in} step={0.5} min={1} onChange={v => update('shaft_parameters', { bearing_seat_diameter_in: v })} /></Field>
          <Field label="Output Bearing Seat Ø" unit="mm"><NumberInput value={sp.bearing_seat_diameter_out} step={0.5} min={1} onChange={v => update('shaft_parameters', { bearing_seat_diameter_out: v })} /></Field>
        </CollapsibleSection>
      </div>

      {/* Housing Parameters */}
      <div className="mt-3">
        <CollapsibleSection title="Housing Parameters" icon={<Building className="w-4 h-4 text-purple-500" />}>
          <Field label="Housing Length" unit="mm"><NumberInput value={hp.housing_length} step={5} min={10} onChange={v => update('housing_parameters', { housing_length: v })} /></Field>
          <Field label="Housing Width" unit="mm"><NumberInput value={hp.housing_width} step={5} min={10} onChange={v => update('housing_parameters', { housing_width: v })} /></Field>
          <Field label="Housing Height" unit="mm"><NumberInput value={hp.housing_height} step={5} min={10} onChange={v => update('housing_parameters', { housing_height: v })} /></Field>
          <Field label="Wall Thickness" unit="mm"><NumberInput value={hp.wall_thickness} step={0.5} min={1} onChange={v => update('housing_parameters', { wall_thickness: v })} /></Field>
          <Field label="Cover Thickness" unit="mm"><NumberInput value={hp.cover_thickness} step={0.5} min={1} onChange={v => update('housing_parameters', { cover_thickness: v })} /></Field>
          <Field label="Base Thickness" unit="mm"><NumberInput value={hp.base_thickness} step={0.5} min={1} onChange={v => update('housing_parameters', { base_thickness: v })} /></Field>
          <Field label="Mounting Hole Ø" unit="mm"><NumberInput value={hp.mounting_hole_diameter} step={0.5} min={2} onChange={v => update('housing_parameters', { mounting_hole_diameter: v })} /></Field>
          <Field label="Mounting Hole Count"><NumberInput value={hp.mounting_hole_count} step={1} min={2} onChange={v => update('housing_parameters', { mounting_hole_count: v })} /></Field>
        </CollapsibleSection>
      </div>

      {/* Assembly Parameters */}
      <div className="mt-3">
        <CollapsibleSection title="Assembly Parameters" icon={<Boxes className="w-4 h-4 text-green-500" />}>
          <Field label="Bearing Arrangement">
            <select className="eng-input" value={ap.bearing_arrangement} onChange={e => update('assembly_parameters', { bearing_arrangement: e.target.value })}>
              <option value="simple">Simple (one per end)</option>
              <option value="fixed_free">Fixed / Free</option>
              <option value="cross_located">Cross Located</option>
            </select>
          </Field>
          <Field label="Cover Fastener Diameter" unit="mm"><NumberInput value={ap.cover_fastener_diameter} step={0.5} min={2} onChange={v => update('assembly_parameters', { cover_fastener_diameter: v })} /></Field>
          <Field label="Input Speed" unit="rpm"><NumberInput value={design.input_speed_rpm} step={10} min={1} onChange={v => setDesign({ ...design, input_speed_rpm: v })} /></Field>
          <Field label="Include Fasteners"><input type="checkbox" checked={ap.include_fasteners} onChange={e => update('assembly_parameters', { include_fasteners: e.target.checked })} /></Field>
          <Field label="Include Keys"><input type="checkbox" checked={ap.include_keys} onChange={e => update('assembly_parameters', { include_keys: e.target.checked })} /></Field>
          <Field label="Include Bearings"><input type="checkbox" checked={ap.include_bearings} onChange={e => update('assembly_parameters', { include_bearings: e.target.checked })} /></Field>
        </CollapsibleSection>
      </div>

      {/* Validation & Summary */}
      {validation && calcs && showSummary && (
        <Card className="mt-4 p-4">
          <SectionHeader title="Design Summary" subtitle="Review before generating" />
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
            <div className="text-center p-2"><div className="tech-label">Pitch Ø (Pinion)</div><div className="text-lg font-mono mt-1" style={{ color: 'var(--workspace-text)' }}>{calcs.input_pitch_diameter} mm</div></div>
            <div className="text-center p-2"><div className="tech-label">Pitch Ø (Gear)</div><div className="text-lg font-mono mt-1" style={{ color: 'var(--workspace-text)' }}>{calcs.output_pitch_diameter} mm</div></div>
            <div className="text-center p-2"><div className="tech-label">Centre Distance</div><div className="text-lg font-mono mt-1" style={{ color: 'var(--workspace-text)' }}>{calcs.centre_distance} mm</div></div>
            <div className="text-center p-2"><div className="tech-label">Reduction Ratio</div><div className="text-lg font-mono mt-1" style={{ color: 'var(--workspace-text)' }}>{calcs.reduction_ratio.toFixed(2)} : 1</div></div>
          </div>
          <div className="flex items-center gap-2 mb-3">
            {validation.is_valid ? (
              <Badge variant="success"><CheckCircle2 className="w-3 h-3" /> Design Valid</Badge>
            ) : (
              <Badge variant="error"><AlertTriangle className="w-3 h-3" /> {validation.issues.filter(i => i.severity === 'error').length} Error(s)</Badge>
            )}
            <span className="text-xs" style={{ color: 'var(--workspace-text-muted)' }}>{validation.checks_run} checks run</span>
          </div>
          {validation.issues.length > 0 && (
            <div className="space-y-1 max-h-32 overflow-y-auto">
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

      {/* Action Buttons */}
      <div className="flex items-center gap-3 mt-6 sticky bottom-0 p-4 -mx-6" style={{ backgroundColor: 'var(--workspace-bg)' }}>
        <Button variant="outline" onClick={handleReset}><RotateCcw className="w-4 h-4" /> Reset to Defaults</Button>
        <Button variant="secondary" onClick={handleValidate} disabled={isGenerating}><Save className="w-4 h-4" /> Validate</Button>
        <Button onClick={handleGenerate} disabled={isGenerating || (validation !== null && !validation.is_valid)}>
          <Play className="w-4 h-4" /> {isGenerating ? 'Generating...' : 'Generate Design'}
        </Button>
        {job && job.status === 'running' && (
          <span className="text-xs" style={{ color: 'var(--workspace-text-muted)' }}>{job.message} ({Math.round(job.progress)}%)</span>
        )}
      </div>
    </div>
  );
}
