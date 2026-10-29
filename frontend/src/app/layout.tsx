import type { Metadata } from 'next';
import './globals.css';
import { DesignProvider } from '@/hooks/use-design';
import { Sidebar } from '@/components/layout/sidebar';
import { TopBar } from '@/components/layout/topbar';

export const metadata: Metadata = {
  title: 'Gearbox Studio — Parametric CAD Automation',
  description: 'Parametric Mechanical Design & CAD Automation Platform',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <DesignProvider>
          <div className="flex h-screen overflow-hidden">
            <Sidebar />
            <div className="flex flex-col flex-1 overflow-hidden">
              <TopBar />
              <main className="flex-1 overflow-y-auto">
                {children}
              </main>
            </div>
          </div>
        </DesignProvider>
      </body>
    </html>
  );
}
