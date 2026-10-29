'use client';

import { useEffect, useState } from 'react';
import { FileText, Download, Layers } from 'lucide-react';
import { Card, SectionHeader, EmptyState, Button, Badge, LoadingState } from '@/components/ui';
import { useDesign } from '@/hooks/use-design';
import { api } from '@/lib/api';
import type { DrawingInfo } from '@/types';
import Link from 'next/link';

export default function DrawingsPage() {
  const { designId, designRecord } = useDesign();
  const [drawings, setDrawings] = useState<DrawingInfo[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!designId) return;
    setLoading(true);
    api.getDrawings(designId)
      .then(setDrawings)
      .catch(() => setDrawings([]))
      .finally(() => setLoading(false));
  }, [designId]);

  if (loading) return <LoadingState message="Loading drawings..." />;

  if (!designId || drawings.length === 0) {
    return (
      <div className="p-6">
        <EmptyState
          icon={<FileText className="w-12 h-12" />}
          title="No Drawings Available"
          message="Generate a design to create 2D DXF engineering drawings."
          action={<Link href="/new-design"><Button>Configure Design</Button></Link>}
        />
      </div>
    );
  }

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <div className="mb-6">
        <h1 className="text-xl font-bold mb-1" style={{ color: 'var(--workspace-text)' }}>2D Drawings</h1>
        <p className="text-sm" style={{ color: 'var(--workspace-text-muted)' }}>{drawings.length} DXF drawing sheets generated</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {drawings.map((d, i) => (
          <Card key={d.drawing_id} className="p-4 card-hover">
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-3 flex-1">
                <div className="flex items-center justify-center w-10 h-10 rounded-lg shrink-0"
                  style={{ backgroundColor: 'rgba(59, 130, 246, 0.1)' }}>
                  <span className="text-sm font-bold text-blue-500">{i + 1}</span>
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-sm" style={{ color: 'var(--workspace-text)' }}>{d.name}</h3>
                  <p className="text-xs mt-0.5" style={{ color: 'var(--workspace-text-muted)' }}>{d.description}</p>
                  <div className="flex items-center gap-2 mt-2">
                    {d.dxf_available ? (
                      <Badge variant="success">DXF Ready</Badge>
                    ) : (
                      <Badge variant="warning">Pending</Badge>
                    )}
                  </div>
                </div>
              </div>
              {d.dxf_available && designId && (
                <a href={api.getFileUrl(designId, d.filename)} download>
                  <Button size="sm" variant="outline"><Download className="w-3.5 h-3.5" /> DXF</Button>
                </a>
              )}
            </div>
          </Card>
        ))}
      </div>

      {/* Layers Info */}
      <Card className="p-4 mt-4">
        <SectionHeader title="CAD Layers" subtitle="Organised layer structure used across all drawing sheets" />
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
          {['OUTLINE', 'HIDDEN', 'CENTER', 'DIMENSIONS', 'ANNOTATIONS', 'HOUSING', 'SHAFTS', 'GEARS', 'BEARINGS', 'FASTENERS', 'CONSTRUCTION', 'SECTION_LINES'].map(layer => (
            <div key={layer} className="flex items-center gap-1.5" style={{ color: 'var(--workspace-text-muted)' }}>
              <Layers className="w-3 h-3" />
              <span>{layer}</span>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
