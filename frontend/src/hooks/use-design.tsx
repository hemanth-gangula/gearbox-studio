'use client';

import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import type { GearboxDesign, DesignRecord, JobInfo } from '@/types';
import { defaultDesign } from '@/types';
import { api, pollJob } from '@/lib/api';

interface DesignContextType {
  design: GearboxDesign;
  setDesign: (d: GearboxDesign) => void;
  designId: string | null;
  setDesignId: (id: string | null) => void;
  designRecord: DesignRecord | null;
  setDesignRecord: (r: DesignRecord | null) => void;
  job: JobInfo | null;
  setJob: (j: JobInfo | null) => void;
  isGenerating: boolean;
  setIsGenerating: (b: boolean) => void;
  generate: () => Promise<void>;
  loadDesign: (id: string) => Promise<void>;
  loadDesigns: () => Promise<void>;
  designs: DesignRecord[];
  theme: 'dark' | 'light';
  toggleTheme: () => void;
}

const DesignContext = createContext<DesignContextType | null>(null);

export function DesignProvider({ children }: { children: React.ReactNode }) {
  const [design, setDesign] = useState<GearboxDesign>(defaultDesign);
  const [designId, setDesignId] = useState<string | null>(null);
  const [designRecord, setDesignRecord] = useState<DesignRecord | null>(null);
  const [job, setJob] = useState<JobInfo | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [designs, setDesigns] = useState<DesignRecord[]>([]);
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');

  useEffect(() => {
    const saved = localStorage.getItem('gearbox-design-id');
    if (saved) {
      setDesignId(saved);
      api.getDesign(saved).then(r => setDesignRecord(r)).catch(() => {});
    }
    const savedTheme = localStorage.getItem('gearbox-theme') as 'dark' | 'light' | null;
    if (savedTheme) setTheme(savedTheme);
  }, []);

  useEffect(() => {
    if (theme === 'light') {
      document.documentElement.setAttribute('data-theme', 'light');
    } else {
      document.documentElement.removeAttribute('data-theme');
    }
    localStorage.setItem('gearbox-theme', theme);
  }, [theme]);

  const toggleTheme = () => setTheme(t => t === 'dark' ? 'light' : 'dark');

  const generate = useCallback(async () => {
    setIsGenerating(true);
    setJob(null);
    try {
      const { design_id, job_id } = await api.generate(design);
      setDesignId(design_id);
      localStorage.setItem('gearbox-design-id', design_id);
      pollJob(
        job_id,
        (j) => setJob(j),
        (j) => {
          setJob(j);
          setIsGenerating(false);
          if (j.status === 'completed') {
            api.getDesign(design_id).then(r => setDesignRecord(r)).catch(() => {});
          }
        },
      );
    } catch (e) {
      setIsGenerating(false);
      console.error('Generation failed:', e);
    }
  }, [design]);

  const loadDesign = useCallback(async (id: string) => {
    try {
      const record = await api.getDesign(id);
      setDesignRecord(record);
      setDesign(record.config);
      setDesignId(id);
      localStorage.setItem('gearbox-design-id', id);
    } catch (e) {
      console.error('Load design failed:', e);
    }
  }, []);

  const loadDesigns = useCallback(async () => {
    try {
      const summaries = await api.listDesigns();
      const records = await Promise.all(
        summaries.map(s => api.getDesign(s.design_id).catch(() => null))
      );
      setDesigns(records.filter((r): r is DesignRecord => r !== null));
    } catch (e) {
      // Backend not available yet
    }
  }, []);

  const value: DesignContextType = {
    design, setDesign,
    designId, setDesignId,
    designRecord, setDesignRecord,
    job, setJob,
    isGenerating, setIsGenerating,
    generate, loadDesign, loadDesigns,
    designs,
    theme, toggleTheme,
  };

  return <DesignContext.Provider value={value}>{children}</DesignContext.Provider>;
}

export function useDesign() {
  const ctx = useContext(DesignContext);
  if (!ctx) throw new Error('useDesign must be used within DesignProvider');
  return ctx;
}
