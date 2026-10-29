'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard, FilePlus, Settings2, FileText, Box,
  Layers, Expand, ClipboardList, FileBarChart, Download, Settings,
  Cog,
} from 'lucide-react';
import { cn } from '@/lib/utils';

const navItems = [
  { label: 'Dashboard', href: '/', icon: LayoutDashboard },
  { label: 'New Design', href: '/new-design', icon: FilePlus },
  { label: 'Design Parameters', href: '/parameters', icon: Settings2 },
  { label: '2D Drawings', href: '/drawings', icon: FileText },
  { label: '3D Model', href: '/model', icon: Box },
  { label: 'Assembly Explorer', href: '/assembly', icon: Layers },
  { label: 'Exploded View', href: '/exploded', icon: Expand },
  { label: 'Bill of Materials', href: '/bom', icon: ClipboardList },
  { label: 'Engineering Reports', href: '/reports', icon: FileBarChart },
  { label: 'Export Center', href: '/exports', icon: Download },
  { label: 'Settings', href: '/settings', icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex flex-col w-60 shrink-0 border-r"
      style={{ backgroundColor: 'var(--workspace-surface)', borderColor: 'var(--workspace-border)' }}>
      {/* Logo */}
      <div className="flex items-center gap-2.5 px-5 py-4 border-b"
        style={{ borderColor: 'var(--workspace-border)' }}>
        <div className="flex items-center justify-center w-8 h-8 rounded-lg"
          style={{ backgroundColor: '#3b82f6' }}>
          <Cog className="w-5 h-5 text-white" />
        </div>
        <div>
          <div className="text-sm font-bold tracking-tight" style={{ color: 'var(--workspace-text)' }}>
            Gearbox Studio
          </div>
          <div className="text-[10px] uppercase tracking-wider" style={{ color: 'var(--workspace-text-muted)' }}>
            CAD Automation
          </div>
        </div>
      </div>

      {/* Nav items */}
      <nav className="flex-1 overflow-y-auto py-2">
        {navItems.map((item) => {
          const active = pathname === item.href;
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex items-center gap-3 px-4 py-2.5 text-sm transition-colors',
                active
                  ? 'border-l-2 border-blue-500 font-medium'
                  : 'border-l-2 border-transparent hover:bg-white/5'
              )}
              style={{
                color: active ? '#3b82f6' : 'var(--workspace-text-muted)',
                backgroundColor: active ? 'rgba(59, 130, 246, 0.08)' : undefined,
              }}
            >
              <Icon className="w-4 h-4 shrink-0" />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="px-4 py-3 border-t text-[10px]"
        style={{ borderColor: 'var(--workspace-border)', color: 'var(--workspace-text-muted)' }}>
        v1.0.0 · Local Environment
      </div>
    </aside>
  );
}
