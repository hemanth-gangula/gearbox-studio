'use client';

import { useEffect, useState } from 'react';
import {
  Download, FileText, Box, ClipboardList, FileBarChart,
  FileCode, Archive, CheckCircle2, Clock, XCircle, Package,
} from 'lucide-react';
import { Card, SectionHeader, EmptyState, Button, Badge, LoadingState } from '@/components/ui';
import { useDesign } from '@/hooks/use-design';
import { api } from '@/lib/api';
import { formatBytes } from '@/lib/utils';
import type { FileListResponse } from '@/types';
import Link from 'next/link';

interface ExportCategory {
  category: string;
  icon: React.ReactNode;
  items: { key: string; label: string; format: string }[];
}

export default function ExportsPage() {
  const { designId, designRecord } = useDesign();
  const [files, setFiles] = useState<FileListResponse | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!designId) return;
    setLoading(true);
    api.getFiles(designId).then(setFiles).catch(() => {}).finally(() => setLoading(false));
  }, [designId]);

  if (loading) return <LoadingState message="Loading export data..." />;

  if (!designId || !designRecord) {
    return (
      <div className="p-6">
        <EmptyState
          icon={<Download className="w-12 h-12" />}
          title="No Exports Available"
          message="Generate a design to create exportable files."
          action={<Link href="/new-design"><Button>Configure Design</Button></Link>}
        />
      </div>
    );
  }

  const categories: ExportCategory[] = [
    {
      category: '2D Drawings (DXF)',
      icon: <FileText className="w-5 h-5" />,
      items: [
        { key: 'dxf_01_general_assembly', label: 'General Assembly', format: 'DXF' },
        { key: 'dxf_02_gearbox_housing', label: 'Gearbox Housing', format: 'DXF' },
        { key: 'dxf_03_input_shaft', label: 'Input Shaft', format: 'DXF' },
        { key: 'dxf_04_output_shaft', label: 'Output Shaft', format: 'DXF' },
        { key: 'dxf_05_input_gear', label: 'Input Gear', format: 'DXF' },
        { key: 'dxf_06_output_gear', label: 'Output Gear', format: 'DXF' },
        { key: 'dxf_07_housing_cover', label: 'Housing Cover', format: 'DXF' },
        { key: 'dxf_08_assembly_section', label: 'Assembly Section', format: 'DXF' },
        { key: 'dxf_09_exploded_assembly', label: 'Exploded Assembly', format: 'DXF' },
      ],
    },
    {
      category: '3D Models',
      icon: <Box className="w-5 h-5" />,
      items: [
        { key: 'glb', label: '3D Assembly Preview', format: 'GLB' },
        { key: 'step', label: 'STEP Geometry', format: 'STEP' },
      ],
    },
    {
      category: 'Bill of Materials',
      icon: <ClipboardList className="w-5 h-5" />,
      items: [
        { key: 'bom_csv', label: 'BOM — CSV', format: 'CSV' },
        { key: 'bom_xlsx', label: 'BOM — Excel', format: 'XLSX' },
      ],
    },
    {
      category: 'Engineering Reports',
      icon: <FileBarChart className="w-5 h-5" />,
      items: [
        { key: 'report_pdf', label: 'Engineering Report — PDF', format: 'PDF' },
        { key: 'report_md', label: 'Engineering Report — Markdown', format: 'MD' },
      ],
    },
    {
      category: 'AutoCAD Scripts',
      icon: <FileCode className="w-5 h-5" />,
      items: [
        { key: 'autocad_scr', label: 'AutoCAD Script (.scr)', format: 'SCR' },
        { key: 'autolisp', label: 'AutoLISP Routine (.lsp)', format: 'LSP' },
      ],
    },
    {
      category: 'Complete Package',
      icon: <Archive className="w-5 h-5" />,
      items: [
        { key: 'zip', label: 'All Deliverables (ZIP)', format: 'ZIP' },
      ],
    },
  ];

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="mb-6">
        <h1 className="text-xl font-bold mb-1" style={{ color: 'var(--workspace-text)' }}>Export Center</h1>
        <p className="text-sm" style={{ color: 'var(--workspace-text-muted)' }}>
          Download generated CAD files, reports, and project deliverables
        </p>
      </div>

      {categories.map((cat) => (
        <Card key={cat.category} className="p-4 mb-3">
          <div className="flex items-center gap-2 mb-3">
            <div style={{ color: 'var(--workspace-text-muted)' }}>{cat.icon}</div>
            <h3 className="text-sm font-semibold" style={{ color: 'var(--workspace-text)' }}>{cat.category}</h3>
          </div>
          <div className="space-y-2">
            {cat.items.map((item) => {
              const fileInfo = files?.files[item.key];
              const available = fileInfo?.available || item.key in (designRecord?.files || {});
              const fileName = fileInfo?.filename || (designRecord?.files || {})[item.key];
              const size = fileInfo?.size_bytes;

              return (
                <div key={item.key} className="flex items-center justify-between py-2 border-b last:border-0" style={{ borderColor: 'var(--workspace-border)' }}>
                  <div className="flex items-center gap-2">
                    {available ? (
                      <CheckCircle2 className="w-4 h-4 text-green-500" />
                    ) : (
                      <XCircle className="w-4 h-4" style={{ color: 'var(--workspace-text-muted)' }} />
                    )}
                    <span className="text-sm" style={{ color: 'var(--workspace-text)' }}>{item.label}</span>
                    <Badge variant={available ? 'success' : 'info'}>{item.format}</Badge>
                    {size && <span className="text-xs" style={{ color: 'var(--workspace-text-muted)' }}>{formatBytes(size)}</span>}
                  </div>
                  {available && fileName && (
                    <a href={api.getFileUrl(designId, fileName)} download>
                      <Button size="sm" variant="outline"><Download className="w-3.5 h-3.5" /> Download</Button>
                    </a>
                  )}
                </div>
              );
            })}
          </div>
        </Card>
      ))}

      {/* DWG Note */}
      <Card className="p-4">
        <div className="flex items-start gap-3">
          <Package className="w-5 h-5 text-amber-500 mt-0.5" />
          <div className="text-xs space-y-1" style={{ color: 'var(--workspace-text-muted)' }}>
            <p><strong style={{ color: 'var(--workspace-text)' }}>DWG Format:</strong> Native DWG is not available without AutoCAD or a verified conversion workflow. Use the DXF format for compatibility with all CAD software, or use the AutoCAD scripts (.scr/.lsp) to generate geometry directly in AutoCAD.</p>
            <p><strong style={{ color: 'var(--workspace-text)' }}>STEP Format:</strong> STEP export uses a custom faceted approximation. For analytical B-rep STEP, install FreeCAD or build123d.</p>
          </div>
        </div>
      </Card>
    </div>
  );
}
