'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import {
  FilePlus, FolderOpen, FileText, Box, CheckCircle2,
  AlertTriangle, Download, Clock, Cog, ChevronRight,
  Layers, ClipboardList,
} from 'lucide-react';
import { Card, SectionHeader, StatCard, EmptyState, Button, Badge, LoadingState } from '@/components/ui';
import { useDesign } from '@/hooks/use-design';
import { api } from '@/lib/api';

export default function DashboardPage() {
  const { design, designId, designRecord, job, loadDesigns, designs } = useDesign();
  const [health, setHealth] = useState<{ available_formats: string[] } | null>(null);
  const [loadingDesigns, setLoadingDesigns] = useState(false);

  useEffect(() => {
    api.health().then(setHealth).catch(() => {});
    setLoadingDesigns(true);
    loadDesigns().finally(() => setLoadingDesigns(false));
  }, [loadDesigns]);

  const calc = designRecord?.calculations;
  const validation = designRecord?.validation;
  const files = designRecord?.files || {};
  const fileCount = Object.keys(files).length;

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-xl font-bold mb-1" style={{ color: 'var(--workspace-text)' }}>Dashboard</h1>
        <p className="text-sm" style={{ color: 'var(--workspace-text-muted)' }}>
          Parametric Mechanical Design &amp; CAD Automation
        </p>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <Link href="/new-design">
          <Card className="p-5 card-hover cursor-pointer h-full">
            <div className="flex items-start gap-3">
              <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-blue-500/10">
                <FilePlus className="w-5 h-5 text-blue-500" />
              </div>
              <div>
                <h3 className="font-semibold text-sm mb-0.5" style={{ color: 'var(--workspace-text)' }}>Create New Gearbox Design</h3>
                <p className="text-xs" style={{ color: 'var(--workspace-text-muted)' }}>Configure parameters and generate a complete design package</p>
              </div>
            </div>
          </Card>
        </Link>

        <Card className="p-5 card-hover cursor-pointer h-full" onClick={() => { if (designs.length > 0) loadDesigns(); }}>
          <div className="flex items-start gap-3">
            <div className="flex items-center justify-center w-10 h-10 rounded-lg" style={{ backgroundColor: 'rgba(245, 158, 11, 0.1)' }}>
              <FolderOpen className="w-5 h-5 text-amber-500" />
            </div>
            <div>
              <h3 className="font-semibold text-sm mb-0.5" style={{ color: 'var(--workspace-text)' }}>Open Existing Project</h3>
              <p className="text-xs" style={{ color: 'var(--workspace-text-muted)' }}>
                {designs.length > 0 ? `${designs.length} project(s) available` : 'No saved projects yet'}
              </p>
            </div>
          </div>
        </Card>

        <Link href="/exports">
          <Card className="p-5 card-hover cursor-pointer h-full">
            <div className="flex items-start gap-3">
              <div className="flex items-center justify-center w-10 h-10 rounded-lg" style={{ backgroundColor: 'rgba(34, 197, 94, 0.1)' }}>
                <Download className="w-5 h-5 text-green-500" />
              </div>
              <div>
                <h3 className="font-semibold text-sm mb-0.5" style={{ color: 'var(--workspace-text)' }}>Export Center</h3>
                <p className="text-xs" style={{ color: 'var(--workspace-text-muted)' }}>
                  {fileCount > 0 ? `${fileCount} files ready to download` : 'Generate a design first'}
                </p>
              </div>
            </div>
          </Card>
        </Link>
      </div>

      {/* Current Design Summary */}
      <div className="mb-6">
        <SectionHeader title="Current Design" subtitle={design.project_info.project_name} />
        {calc ? (
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
            <StatCard label="Reduction Ratio" value={`${calc.reduction_ratio.toFixed(2)} : 1`} icon={<Cog className="w-4 h-4" />} />
            <StatCard label="Module" value={calc.module} unit="mm" />
            <StatCard label="Pinion Teeth" value={design.gear_parameters.input_teeth} />
            <StatCard label="Gear Teeth" value={design.gear_parameters.output_teeth} />
            <StatCard label="Centre Distance" value={calc.centre_distance.toFixed(1)} unit="mm" />
          </div>
        ) : (
          <Card className="p-8">
            <EmptyState
              icon={<Cog className="w-12 h-12" />}
              title="No Design Generated Yet"
              message="Create a new gearbox design to see calculation results, generate drawings, and export files."
              action={<Link href="/new-design"><Button>Start New Design</Button></Link>}
            />
          </Card>
        )}
      </div>

      {/* Two-column area */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Validation Status */}
        <div>
          <SectionHeader title="Design Validation" subtitle={validation ? `${validation.checks_run} checks run` : 'Not validated'} />
          {validation ? (
            <Card className="p-4">
              <div className="flex items-center gap-2 mb-3">
                {validation.is_valid ? (
                  <Badge variant="success"><CheckCircle2 className="w-3 h-3" /> Valid</Badge>
                ) : (
                  <Badge variant="error"><AlertTriangle className="w-3 h-3" /> Issues Found</Badge>
                )}
              </div>
              {validation.issues.slice(0, 5).map((issue, i) => (
                <div key={i} className="flex items-start gap-2 py-1.5 text-xs">
                  <span className={`status-badge ${issue.severity} shrink-0`}>{issue.severity}</span>
                  <span style={{ color: 'var(--workspace-text-muted)' }}>{issue.message}</span>
                </div>
              ))}
              {validation.issues.length > 5 && (
                <p className="text-xs mt-2" style={{ color: 'var(--workspace-text-muted)' }}>
                  +{validation.issues.length - 5} more issue(s)
                </p>
              )}
            </Card>
          ) : (
            <Card className="p-6">
              <EmptyState icon={<AlertTriangle className="w-10 h-10" />} title="No Validation Data" message="Generate a design to see validation results." />
            </Card>
          )}
        </div>

        {/* Export Availability */}
        <div>
          <SectionHeader title="Export Availability" subtitle={health ? `${health.available_formats.length} formats` : 'Checking...'} />
          <Card className="p-4">
            <div className="space-y-2">
              {[
                { fmt: 'DXF', label: '2D Drawings', icon: <FileText className="w-4 h-4" /> },
                { fmt: 'GLB', label: '3D Preview', icon: <Box className="w-4 h-4" /> },
                { fmt: 'STEP', label: 'STEP Geometry', icon: <Layers className="w-4 h-4" /> },
                { fmt: 'BOM', label: 'Bill of Materials', icon: <ClipboardList className="w-4 h-4" /> },
                { fmt: 'Report', label: 'Engineering Report', icon: <FileText className="w-4 h-4" /> },
              ].map(({ fmt, label, icon }) => {
                const available = Object.values(files).some(f => f.toLowerCase().includes(fmt.toLowerCase()));
                return (
                  <div key={fmt} className="flex items-center justify-between py-1.5 text-sm">
                    <div className="flex items-center gap-2" style={{ color: 'var(--workspace-text)' }}>
                      {icon}
                      <span>{label}</span>
                    </div>
                    {available ? (
                      <Badge variant="success">Ready</Badge>
                    ) : (
                      <Badge variant="info">Pending</Badge>
                    )}
                  </div>
                );
              })}
            </div>
          </Card>
        </div>
      </div>

      {/* Recent Designs */}
      <div className="mt-6">
        <SectionHeader title="Recent Designs" subtitle="Previously generated projects" />
        {loadingDesigns ? (
          <LoadingState message="Loading designs..." />
        ) : designs.length === 0 ? (
          <Card className="p-6">
            <p className="text-sm text-center" style={{ color: 'var(--workspace-text-muted)' }}>
              No previous projects. Create a new design to get started.
            </p>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {designs.map((d) => (
              <Card key={d.design_id} className="p-4 card-hover cursor-pointer" onClick={() => window.location.href = '/'}>
                <div className="flex items-center justify-between mb-2">
                  <div className="text-sm font-medium" style={{ color: 'var(--workspace-text)' }}>
                    {d.project_name}
                  </div>
                  <Badge variant={d.files && Object.keys(d.files).length > 0 ? 'success' : 'info'}>
                    {d.files && Object.keys(d.files).length > 0 ? 'Generated' : 'Configured'}
                  </Badge>
                </div>
                <div className="text-xs space-y-0.5" style={{ color: 'var(--workspace-text-muted)' }}>
                  <div>{d.drawing_number} · {d.created_at.split('T')[0]}</div>
                  {d.calculations && (
                    <div>Ratio: {d.calculations.reduction_ratio.toFixed(2)}:1 · Module: {d.calculations.module} mm</div>
                  )}
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Job Progress (if generating) */}
      {job && job.status === 'running' && (
        <Card className="mt-6 p-4">
          <div className="flex items-center gap-3 mb-2">
            <div className="spinner" />
            <div>
              <div className="text-sm font-medium" style={{ color: 'var(--workspace-text)' }}>{job.message}</div>
              <div className="text-xs" style={{ color: 'var(--workspace-text-muted)' }}>{job.stage.replace(/_/g, ' ')}</div>
            </div>
          </div>
          <div className="w-full h-1.5 rounded-full" style={{ backgroundColor: 'var(--workspace-border)' }}>
            <div className="h-1.5 rounded-full bg-blue-500 transition-all" style={{ width: `${job.progress}%` }} />
          </div>
        </Card>
      )}
    </div>
  );
}
