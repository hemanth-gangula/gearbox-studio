'use client';

import { Sun, Moon, HelpCircle, Check, Loader2, AlertCircle } from 'lucide-react';
import { useDesign } from '@/hooks/use-design';

export function TopBar() {
  const { design, theme, toggleTheme, isGenerating, job } = useDesign();

  return (
    <header className="flex items-center justify-between px-6 py-3 border-b shrink-0"
      style={{ backgroundColor: 'var(--workspace-surface)', borderColor: 'var(--workspace-border)' }}>
      <div className="flex items-center gap-4">
        <div className="text-sm font-semibold" style={{ color: 'var(--workspace-text)' }}>
          {design.project_info.project_name || 'Untitled Project'}
        </div>
        <div className="text-xs" style={{ color: 'var(--workspace-text-muted)' }}>
          {design.project_info.drawing_number}
        </div>
      </div>

      <div className="flex items-center gap-4">
        {/* Save / generation status */}
        {isGenerating && job ? (
          <div className="flex items-center gap-2 text-xs" style={{ color: 'var(--workspace-text-muted)' }}>
            <Loader2 className="w-3.5 h-3.5 animate-spin text-blue-500" />
            <span>{job.message} ({Math.round(job.progress)}%)</span>
          </div>
        ) : job && job.status === 'completed' ? (
          <div className="flex items-center gap-1.5 text-xs text-green-500">
            <Check className="w-3.5 h-3.5" />
            <span>Saved</span>
          </div>
        ) : job && job.status === 'failed' ? (
          <div className="flex items-center gap-1.5 text-xs text-red-500">
            <AlertCircle className="w-3.5 h-3.5" />
            <span>Generation Failed</span>
          </div>
        ) : (
          <div className="text-xs" style={{ color: 'var(--workspace-text-muted)' }}>
            Not saved
          </div>
        )}

        {/* Help */}
        <button className="p-1.5 rounded-md transition-colors hover:bg-white/5"
          style={{ color: 'var(--workspace-text-muted)' }}
          title="Help">
          <HelpCircle className="w-4 h-4" />
        </button>

        {/* Theme toggle */}
        <button onClick={toggleTheme} className="p-1.5 rounded-md transition-colors hover:bg-white/5"
          style={{ color: 'var(--workspace-text-muted)' }}
          title="Toggle theme">
          {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
        </button>
      </div>
    </header>
  );
}
