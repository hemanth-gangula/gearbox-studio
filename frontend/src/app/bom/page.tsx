'use client';

import { useEffect, useState } from 'react';
import { ClipboardList, Download, FileSpreadsheet, FileText } from 'lucide-react';
import { Card, SectionHeader, EmptyState, Button, Badge, LoadingState } from '@/components/ui';
import { useDesign } from '@/hooks/use-design';
import { api } from '@/lib/api';
import type { BOM } from '@/types';
import Link from 'next/link';

export default function BOMPage() {
  const { designId, designRecord } = useDesign();
  const [bom, setBom] = useState<BOM | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!designId) return;
    setLoading(true);
    api.getBom(designId).then(setBom).catch(() => {}).finally(() => setLoading(false));
  }, [designId]);

  if (loading) return <LoadingState message="Loading BOM..." />;

  if (!designId || !bom) {
    return (
      <div className="p-6">
        <EmptyState
          icon={<ClipboardList className="w-12 h-12" />}
          title="No BOM Available"
          message="Generate a design to create the Bill of Materials."
          action={<Link href="/new-design"><Button>Configure Design</Button></Link>}
        />
      </div>
    );
  }

  const statusVariant = (s: string) => s === 'verified' ? 'success' : s === 'approximate' ? 'warning' : 'info';

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-bold mb-1" style={{ color: 'var(--workspace-text)' }}>Bill of Materials</h1>
          <p className="text-sm" style={{ color: 'var(--workspace-text-muted)' }}>{bom.total_parts} components in assembly</p>
        </div>
        {designId && (
          <div className="flex gap-2">
            {designRecord?.files?.bom_csv && (
              <a href={api.getFileUrl(designId, 'bom.csv')} download>
                <Button size="sm" variant="outline"><Download className="w-3.5 h-3.5" /> CSV</Button>
              </a>
            )}
            {designRecord?.files?.bom_xlsx && (
              <a href={api.getFileUrl(designId, 'bom.xlsx')} download>
                <Button size="sm" variant="outline"><FileSpreadsheet className="w-3.5 h-3.5" /> XLSX</Button>
              </a>
            )}
          </div>
        )}
      </div>

      <Card className="overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr style={{ backgroundColor: 'var(--workspace-surface)', borderBottom: '1px solid var(--workspace-border)' }}>
                <th className="text-left py-2.5 px-3 tech-label">Item</th>
                <th className="text-left py-2.5 px-3 tech-label">Part Number</th>
                <th className="text-left py-2.5 px-3 tech-label">Component</th>
                <th className="text-center py-2.5 px-3 tech-label">Qty</th>
                <th className="text-left py-2.5 px-3 tech-label">Material</th>
                <th className="text-left py-2.5 px-3 tech-label">Principal Dimensions</th>
                <th className="text-left py-2.5 px-3 tech-label">Validation</th>
              </tr>
            </thead>
            <tbody>
              {bom.components.map((comp) => (
                <tr key={comp.item_number} className="border-b card-hover" style={{ borderColor: 'var(--workspace-border)' }}>
                  <td className="py-2.5 px-3 font-mono" style={{ color: 'var(--workspace-text-muted)' }}>{comp.item_number}</td>
                  <td className="py-2.5 px-3 font-mono text-xs" style={{ color: 'var(--workspace-text)' }}>{comp.part_number}</td>
                  <td className="py-2.5 px-3" style={{ color: 'var(--workspace-text)' }}>{comp.name}</td>
                  <td className="py-2.5 px-3 text-center font-mono" style={{ color: 'var(--workspace-text)' }}>{comp.quantity}</td>
                  <td className="py-2.5 px-3 text-xs" style={{ color: 'var(--workspace-text-muted)' }}>{comp.material}</td>
                  <td className="py-2.5 px-3 text-xs font-mono" style={{ color: 'var(--workspace-text-muted)' }}>{comp.principal_dimensions}</td>
                  <td className="py-2.5 px-3"><Badge variant={statusVariant(comp.validation_status)}>{comp.validation_status}</Badge></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Notes */}
      <Card className="p-4 mt-4">
        <SectionHeader title="Notes" />
        <div className="space-y-2 text-xs" style={{ color: 'var(--workspace-text-muted)' }}>
          <p>• Material selections are proposed only and require engineering verification.</p>
          <p>• Simplified components (gears, bearings, housing) use approximate geometry for visualization.</p>
          <p>• Quantities reflect the modeled assembly configuration.</p>
          <p>• Validation status indicates the level of geometric and engineering verification performed.</p>
        </div>
      </Card>
    </div>
  );
}
