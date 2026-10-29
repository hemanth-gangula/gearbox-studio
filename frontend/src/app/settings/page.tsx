'use client';

import { useEffect, useState } from 'react';
import { Settings as SettingsIcon, Server, Palette, Cog, Info } from 'lucide-react';
import { Card, SectionHeader, Badge, Button } from '@/components/ui';
import { useDesign } from '@/hooks/use-design';
import { api } from '@/lib/api';

export default function SettingsPage() {
  const { theme, toggleTheme } = useDesign();
  const [health, setHealth] = useState<{ status: string; version: string; cad_engine: string; available_formats: string[] } | null>(null);

  useEffect(() => {
    api.health().then(setHealth).catch(() => setHealth(null));
  }, []);

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <div className="mb-6">
        <h1 className="text-xl font-bold mb-1" style={{ color: 'var(--workspace-text)' }}>Settings</h1>
        <p className="text-sm" style={{ color: 'var(--workspace-text-muted)' }}>Application and environment configuration</p>
      </div>

      {/* Theme */}
      <Card className="p-4 mb-3">
        <div className="flex items-center gap-2 mb-3">
          <Palette className="w-4 h-4 text-blue-500" />
          <h3 className="text-sm font-semibold" style={{ color: 'var(--workspace-text)' }}>Appearance</h3>
        </div>
        <div className="flex items-center justify-between">
          <div>
            <div className="text-sm" style={{ color: 'var(--workspace-text)' }}>Theme</div>
            <p className="text-xs" style={{ color: 'var(--workspace-text-muted)' }}>Switch between dark and light workspace</p>
          </div>
          <Button variant="outline" onClick={toggleTheme}>{theme === 'dark' ? 'Dark' : 'Light'}</Button>
        </div>
      </Card>

      {/* Backend Status */}
      <Card className="p-4 mb-3">
        <div className="flex items-center gap-2 mb-3">
          <Server className="w-4 h-4 text-green-500" />
          <h3 className="text-sm font-semibold" style={{ color: 'var(--workspace-text)' }}>Backend Status</h3>
        </div>
        {health ? (
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span style={{ color: 'var(--workspace-text-muted)' }}>Status</span>
              <Badge variant="success">{health.status}</Badge>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span style={{ color: 'var(--workspace-text-muted)' }}>Version</span>
              <span className="font-mono" style={{ color: 'var(--workspace-text)' }}>{health.version}</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span style={{ color: 'var(--workspace-text-muted)' }}>CAD Engine</span>
              <span className="font-mono text-xs" style={{ color: 'var(--workspace-text)' }}>{health.cad_engine}</span>
            </div>
          </div>
        ) : (
          <div className="flex items-center gap-2 text-sm" style={{ color: 'var(--workspace-text-muted)' }}>
            <span>Backend not connected</span>
          </div>
        )}
      </Card>

      {/* Available Formats */}
      <Card className="p-4 mb-3">
        <div className="flex items-center gap-2 mb-3">
          <Cog className="w-4 h-4 text-amber-500" />
          <h3 className="text-sm font-semibold" style={{ color: 'var(--workspace-text)' }}>Available Export Formats</h3>
        </div>
        {health && (
          <div className="flex flex-wrap gap-2">
            {health.available_formats.map(fmt => (
              <Badge key={fmt} variant="info">{fmt}</Badge>
            ))}
          </div>
        )}
      </Card>

      {/* Environment Info */}
      <Card className="p-4">
        <div className="flex items-center gap-2 mb-3">
          <Info className="w-4 h-4 text-blue-500" />
          <h3 className="text-sm font-semibold" style={{ color: 'var(--workspace-text)' }}>Environment Information</h3>
        </div>
        <div className="space-y-2 text-xs" style={{ color: 'var(--workspace-text-muted)' }}>
          <div><strong style={{ color: 'var(--workspace-text)' }}>Python:</strong> 3.14.6 — FastAPI, ezdxf, trimesh, reportlab, openpyxl</div>
          <div><strong style={{ color: 'var(--workspace-text)' }}>Node.js:</strong> v22.23.2 — Next.js, React, TypeScript, Three.js</div>
          <div><strong style={{ color: 'var(--workspace-text)' }}>CAD Engine:</strong> ezdxf (DXF) + trimesh (3D mesh/GLB) + custom STEP exporter</div>
          <div><strong style={{ color: 'var(--workspace-text)' }}>FreeCAD:</strong> Not available — STEP export uses faceted approximation</div>
          <div><strong style={{ color: 'var(--workspace-text)' }}>AutoCAD:</strong> Not available — DWG not supported, use DXF or scripts</div>
        </div>
      </Card>
    </div>
  );
}
