'use client';

import { useEffect, useState } from 'react';
import { FileBarChart, Download, FileText, File } from 'lucide-react';
import { Card, SectionHeader, EmptyState, Button, Badge, LoadingState } from '@/components/ui';
import { useDesign } from '@/hooks/use-design';
import { api } from '@/lib/api';
import Link from 'next/link';

export default function ReportsPage() {
  const { designId, designRecord } = useDesign();
  const [reportMd, setReportMd] = useState<string>('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!designId) return;
    setLoading(true);
    fetch(`/api/designs/${designId}/file/report.md`)
      .then(r => r.text())
      .then(setReportMd)
      .catch(() => setReportMd(''))
      .finally(() => setLoading(false));
  }, [designId]);

  if (loading) return <LoadingState message="Loading report..." />;

  if (!designId || !designRecord?.files?.report_pdf) {
    return (
      <div className="p-6">
        <EmptyState
          icon={<FileBarChart className="w-12 h-12" />}
          title="No Report Available"
          message="Generate a design to create an engineering report with calculations, validation, and BOM."
          action={<Link href="/new-design"><Button>Configure Design</Button></Link>}
        />
      </div>
    );
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-bold mb-1" style={{ color: 'var(--workspace-text)' }}>Engineering Report</h1>
          <p className="text-sm" style={{ color: 'var(--workspace-text-muted)' }}>
            {designRecord?.project_name} · {designRecord?.drawing_number}
          </p>
        </div>
        <div className="flex gap-2">
          {designRecord?.files?.report_pdf && (
            <a href={api.getFileUrl(designId, 'report.pdf')} download>
              <Button size="sm" variant="outline"><FileText className="w-3.5 h-3.5" /> PDF</Button>
            </a>
          )}
          {designRecord?.files?.report_md && (
            <a href={api.getFileUrl(designId, 'report.md')} download>
              <Button size="sm" variant="outline"><File className="w-3.5 h-3.5" /> Markdown</Button>
            </a>
          )}
        </div>
      </div>

      {/* Report content */}
      {reportMd ? (
        <Card className="p-6">
          <div className="prose prose-sm max-w-none" style={{ color: 'var(--workspace-text)' }}>
            <pre className="whitespace-pre-wrap font-mono text-xs leading-relaxed" style={{ color: 'var(--workspace-text-muted)' }}>
              {reportMd}
            </pre>
          </div>
        </Card>
      ) : (
        <Card className="p-4">
          <p className="text-sm" style={{ color: 'var(--workspace-text-muted)' }}>Report file is available for download but could not be previewed.</p>
        </Card>
      )}

      {/* Report sections */}
      <Card className="p-4 mt-4">
        <SectionHeader title="Report Contents" subtitle="Sections included in the engineering report" />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
          {[
            'Cover Page', 'Project Overview', 'Design Assumptions', 'Input Parameters',
            'Engineering Calculations', 'Gear Dimensions', 'Shaft & Housing Dimensions',
            'Assembly Summary', 'Drawing Index', 'Bill of Materials',
            'Validation Results', 'Known Limitations', 'Suggested Engineering Checks',
          ].map(section => (
            <div key={section} className="flex items-center gap-2 text-xs" style={{ color: 'var(--workspace-text-muted)' }}>
              <FileText className="w-3 h-3" />
              <span>{section}</span>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
