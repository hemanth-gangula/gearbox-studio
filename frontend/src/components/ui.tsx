'use client';

import { cn } from '@/lib/utils';

export function Card({ children, className, onClick }: { children: React.ReactNode; className?: string; onClick?: () => void }) {
  return (
    <div
      onClick={onClick}
      className={cn('rounded-lg border', className)}
      style={{
        backgroundColor: 'var(--workspace-card)',
        borderColor: 'var(--workspace-border)',
      }}
    >
      {children}
    </div>
  );
}

export function SectionHeader({ title, subtitle, action }: { title: string; subtitle?: string; action?: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between mb-4">
      <div>
        <h2 className="text-lg font-semibold" style={{ color: 'var(--workspace-text)' }}>{title}</h2>
        {subtitle && <p className="text-xs mt-0.5" style={{ color: 'var(--workspace-text-muted)' }}>{subtitle}</p>}
      </div>
      {action}
    </div>
  );
}

export function StatCard({ label, value, unit, icon }: { label: string; value: string | number; unit?: string; icon?: React.ReactNode }) {
  return (
    <Card className="p-4">
      <div className="flex items-start justify-between">
        <div>
          <div className="tech-label">{label}</div>
          <div className="text-2xl font-semibold mt-1" style={{ color: 'var(--workspace-text)' }}>
            {value}
            {unit && <span className="text-sm ml-1" style={{ color: 'var(--workspace-text-muted)' }}>{unit}</span>}
          </div>
        </div>
        {icon && <div style={{ color: 'var(--workspace-text-muted)' }}>{icon}</div>}
      </div>
    </Card>
  );
}

export function EmptyState({ icon, title, message, action }: { icon: React.ReactNode; title: string; message: string; action?: React.ReactNode }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <div className="mb-4 opacity-40">{icon}</div>
      <h3 className="text-base font-semibold mb-1" style={{ color: 'var(--workspace-text)' }}>{title}</h3>
      <p className="text-sm max-w-md" style={{ color: 'var(--workspace-text-muted)' }}>{message}</p>
      {action && <div className="mt-6">{action}</div>}
    </div>
  );
}

export function Button({ children, onClick, variant = 'primary', size = 'md', disabled, className }: {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: 'primary' | 'secondary' | 'outline' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  className?: string;
}) {
  const base = 'rounded-md font-medium transition-colors inline-flex items-center justify-center gap-2';
  const sizes = { sm: 'px-3 py-1.5 text-xs', md: 'px-4 py-2 text-sm', lg: 'px-5 py-2.5 text-sm' };
  const variants = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50',
    secondary: 'text-white hover:bg-white/10 disabled:opacity-50',
    outline: 'border hover:bg-white/5 disabled:opacity-50',
    danger: 'bg-red-600 text-white hover:bg-red-700 disabled:opacity-50',
  };
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={cn(base, sizes[size], variants[variant], className)}
      style={variant === 'outline' ? { borderColor: 'var(--workspace-border)', color: 'var(--workspace-text)' } : undefined}
    >
      {children}
    </button>
  );
}

export function Badge({ children, variant = 'info' }: { children: React.ReactNode; variant?: 'success' | 'warning' | 'error' | 'info' }) {
  return <span className={`status-badge ${variant}`}>{children}</span>;
}

export function LoadingState({ message = 'Loading...' }: { message?: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-16">
      <div className="spinner mb-3" />
      <p className="text-sm" style={{ color: 'var(--workspace-text-muted)' }}>{message}</p>
    </div>
  );
}
