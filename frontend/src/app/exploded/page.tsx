'use client';

import { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import { Expand, Minimize2, RotateCcw, Layers } from 'lucide-react';
import { Card, EmptyState, Button, Badge } from '@/components/ui';
import { useDesign } from '@/hooks/use-design';
import { api } from '@/lib/api';
import Link from 'next/link';
import type { ComponentInfo } from '@/types';

const CADViewer = dynamic(() => import('@/components/cad-viewer/viewer'), { ssr: false });

export default function ExplodedPage() {
  const { designId, designRecord } = useDesign();
  const [components, setComponents] = useState<ComponentInfo[]>([]);
  const [explodeFactor, setExplodeFactor] = useState(0);
  const [visibleItems, setVisibleItems] = useState<Set<number>>(new Set());

  useEffect(() => {
    if (!designId) return;
    api.getComponents(designId).then(c => {
      setComponents(c);
      setVisibleItems(new Set(c.map(x => x.item_number)));
    }).catch(() => {});
  }, [designId]);

  const glbUrl = designId ? api.getFileUrl(designId, 'assembly.glb') : null;

  if (!designId || !designRecord?.files?.glb) {
    return (
      <div className="p-6">
        <EmptyState
          icon={<Expand className="w-12 h-12" />}
          title="No Exploded View Available"
          message="Generate a design to see the exploded assembly."
          action={<Link href="/new-design"><Button>Configure Design</Button></Link>}
        />
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Toolbar */}
      <div className="flex items-center gap-4 px-6 py-3 border-b" style={{ borderColor: 'var(--workspace-border)', backgroundColor: 'var(--workspace-surface)' }}>
        <div className="flex items-center gap-2 flex-1">
          <span className="tech-label">Explosion Distance</span>
          <input
            type="range"
            min={0}
            max={2}
            step={0.05}
            value={explodeFactor}
            onChange={e => setExplodeFactor(parseFloat(e.target.value))}
            className="flex-1 max-w-xs"
          />
          <span className="text-sm font-mono w-12" style={{ color: 'var(--workspace-text)' }}>{(explodeFactor * 100).toFixed(0)}%</span>
        </div>
        <Button size="sm" variant="outline" onClick={() => setExplodeFactor(1.0)}><Expand className="w-3.5 h-3.5" /> Explode</Button>
        <Button size="sm" variant="outline" onClick={() => setExplodeFactor(0)}><Minimize2 className="w-3.5 h-3.5" /> Assemble</Button>
        <Button size="sm" variant="outline" onClick={() => setExplodeFactor(0)}><RotateCcw className="w-3.5 h-3.5" /> Reset</Button>
      </div>

      <div className="flex flex-1 overflow-hidden">
        {/* Viewer */}
        <div className="flex-1 relative">
          <CADViewer glbUrl={glbUrl} explodeFactor={explodeFactor} backgroundColor="#1a1d28" />
        </div>

        {/* Parts list */}
        <div className="w-72 shrink-0 border-l overflow-y-auto" style={{ borderColor: 'var(--workspace-border)', backgroundColor: 'var(--workspace-surface)' }}>
          <div className="p-3 border-b" style={{ borderColor: 'var(--workspace-border)' }}>
            <h3 className="text-sm font-semibold" style={{ color: 'var(--workspace-text)' }}>Parts List</h3>
            <p className="text-xs mt-0.5" style={{ color: 'var(--workspace-text-muted)' }}>{components.length} components</p>
          </div>
          <div className="py-1">
            {components.map((comp) => (
              <div key={comp.item_number} className="px-3 py-2 border-b" style={{ borderColor: 'var(--workspace-border)' }}>
                <div className="flex items-center gap-2">
                  <span className="flex items-center justify-center w-5 h-5 rounded-full text-[10px] font-bold text-white shrink-0"
                    style={{ backgroundColor: '#3b82f6' }}>{comp.item_number}</span>
                  <span className="text-xs flex-1" style={{ color: 'var(--workspace-text)' }}>{comp.name}</span>
                  <span className="text-xs font-mono" style={{ color: 'var(--workspace-text-muted)' }}>×{comp.quantity}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
