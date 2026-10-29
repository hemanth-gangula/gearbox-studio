'use client';

import { useEffect, useState, useRef } from 'react';
import dynamic from 'next/dynamic';
import { Box, Grid3x3, Eye, EyeOff, Maximize2 } from 'lucide-react';
import { Card, EmptyState, Button, Badge } from '@/components/ui';
import { useDesign } from '@/hooks/use-design';
import { api } from '@/lib/api';
import Link from 'next/link';
import type { ComponentInfo } from '@/types';

const CADViewer = dynamic(() => import('@/components/cad-viewer/viewer'), { ssr: false });

export default function ModelPage() {
  const { designId, designRecord } = useDesign();
  const [components, setComponents] = useState<ComponentInfo[]>([]);
  const [wireframe, setWireframe] = useState(false);
  const [selectedComp, setSelectedComp] = useState<number | null>(null);

  useEffect(() => {
    if (!designId) return;
    api.getComponents(designId).then(setComponents).catch(() => {});
  }, [designId]);

  const glbUrl = designId ? api.getFileUrl(designId, 'assembly.glb') : null;

  if (!designId || !designRecord?.files?.glb) {
    return (
      <div className="p-6">
        <EmptyState
          icon={<Box className="w-12 h-12" />}
          title="No 3D Model Available"
          message="Generate a design to create the 3D gearbox model and preview it here."
          action={<Link href="/new-design"><Button>Configure Design</Button></Link>}
        />
      </div>
    );
  }

  return (
    <div className="flex h-full">
      {/* Viewer */}
      <div className="flex-1 relative">
        <CADViewer
          glbUrl={glbUrl}
          wireframe={wireframe}
          backgroundColor="#1a1d28"
        />
        {/* Controls overlay */}
        <div className="absolute top-4 right-4 flex flex-col gap-2">
          <Button size="sm" variant="outline" onClick={() => setWireframe(!wireframe)}>
            {wireframe ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
            {wireframe ? 'Solid' : 'Wireframe'}
          </Button>
        </div>
      </div>

      {/* Component tree */}
      <div className="w-72 shrink-0 border-l overflow-y-auto" style={{ borderColor: 'var(--workspace-border)', backgroundColor: 'var(--workspace-surface)' }}>
        <div className="p-4 border-b" style={{ borderColor: 'var(--workspace-border)' }}>
          <h3 className="text-sm font-semibold" style={{ color: 'var(--workspace-text)' }}>Component Tree</h3>
          <p className="text-xs mt-0.5" style={{ color: 'var(--workspace-text-muted)' }}>{components.length} components</p>
        </div>
        <div className="py-2">
          {components.map((comp) => (
            <div
              key={comp.item_number}
              onClick={() => setSelectedComp(selectedComp === comp.item_number ? null : comp.item_number)}
              className={`px-4 py-2 cursor-pointer transition-colors ${selectedComp === comp.item_number ? 'bg-blue-500/10' : 'hover:bg-white/5'}`}
            >
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono w-6" style={{ color: 'var(--workspace-text-muted)' }}>{comp.item_number}</span>
                <div className="flex-1">
                  <div className="text-xs font-medium" style={{ color: 'var(--workspace-text)' }}>{comp.name}</div>
                  <div className="text-[10px]" style={{ color: 'var(--workspace-text-muted)' }}>{comp.part_number}</div>
                </div>
              </div>
              {selectedComp === comp.item_number && (
                <div className="mt-2 ml-8 space-y-1 text-[11px]" style={{ color: 'var(--workspace-text-muted)' }}>
                  <div>Qty: {comp.quantity}</div>
                  <div>Material: {comp.material}</div>
                  <div>Dimensions: {comp.principal_dimensions}</div>
                  <div>Status: <Badge variant={comp.validation_status === 'verified' ? 'success' : comp.validation_status === 'approximate' ? 'warning' : 'info'}>{comp.validation_status}</Badge></div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
