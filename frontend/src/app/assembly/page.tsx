'use client';

import { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import { Layers, Info } from 'lucide-react';
import { Card, EmptyState, Button, Badge } from '@/components/ui';
import { useDesign } from '@/hooks/use-design';
import { api } from '@/lib/api';
import Link from 'next/link';
import type { ComponentInfo } from '@/types';

const CADViewer = dynamic(() => import('@/components/cad-viewer/viewer'), { ssr: false });

export default function AssemblyPage() {
  const { designId, designRecord } = useDesign();
  const [components, setComponents] = useState<ComponentInfo[]>([]);
  const [selected, setSelected] = useState<number | null>(null);

  useEffect(() => {
    if (!designId) return;
    api.getComponents(designId).then(setComponents).catch(() => {});
  }, [designId]);

  const glbUrl = designId ? api.getFileUrl(designId, 'assembly.glb') : null;

  if (!designId || !designRecord?.files?.glb) {
    return (
      <div className="p-6">
        <EmptyState
          icon={<Layers className="w-12 h-12" />}
          title="No Assembly Available"
          message="Generate a design to explore the 3D assembly."
          action={<Link href="/new-design"><Button>Configure Design</Button></Link>}
        />
      </div>
    );
  }

  return (
    <div className="flex h-full">
      <div className="flex-1 relative">
        <CADViewer glbUrl={glbUrl} backgroundColor="#1a1d28" />
      </div>
      <div className="w-80 shrink-0 border-l overflow-y-auto" style={{ borderColor: 'var(--workspace-border)', backgroundColor: 'var(--workspace-surface)' }}>
        <div className="p-4 border-b" style={{ borderColor: 'var(--workspace-border)' }}>
          <h3 className="text-sm font-semibold" style={{ color: 'var(--workspace-text)' }}>Assembly Components</h3>
          <p className="text-xs mt-0.5" style={{ color: 'var(--workspace-text-muted)' }}>{components.length} parts in assembly</p>
        </div>
        <div className="py-2">
          {components.map((comp) => (
            <div key={comp.item_number} className="border-b" style={{ borderColor: 'var(--workspace-border)' }}>
              <div
                onClick={() => setSelected(selected === comp.item_number ? null : comp.item_number)}
                className={`px-4 py-2.5 cursor-pointer transition-colors ${selected === comp.item_number ? 'bg-blue-500/10' : 'hover:bg-white/5'}`}
              >
                <div className="flex items-center gap-2">
                  <span className="text-xs font-mono w-6 text-blue-500">{comp.item_number}</span>
                  <div className="flex-1">
                    <div className="text-sm font-medium" style={{ color: 'var(--workspace-text)' }}>{comp.name}</div>
                    <div className="text-[10px]" style={{ color: 'var(--workspace-text-muted)' }}>{comp.part_number} · Qty: {comp.quantity}</div>
                  </div>
                  <Badge variant={comp.validation_status === 'verified' ? 'success' : comp.validation_status === 'approximate' ? 'warning' : 'info'}>
                    {comp.validation_status}
                  </Badge>
                </div>
              </div>
              {selected === comp.item_number && (
                <div className="px-4 pb-3 pt-1 ml-8 space-y-1 text-xs" style={{ color: 'var(--workspace-text-muted)' }}>
                  <div><span className="font-medium" style={{ color: 'var(--workspace-text)' }}>Material:</span> {comp.material}</div>
                  <div><span className="font-medium" style={{ color: 'var(--workspace-text)' }}>Dimensions:</span> {comp.principal_dimensions}</div>
                  <div><span className="font-medium" style={{ color: 'var(--workspace-text)' }}>Notes:</span> {comp.notes}</div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
