import type {
  GearboxDesign,
  CalculationResults,
  ValidationResult,
  JobInfo,
  DesignSummary,
  DesignRecord,
  DrawingInfo,
  BOM,
  ComponentInfo,
  FileListResponse,
} from '@/types';

const API_BASE = '/api';

async function fetchJSON<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });
  if (!res.ok) {
    const errorBody = await res.text();
    throw new Error(`API ${res.status}: ${errorBody}`);
  }
  return res.json();
}

export const api = {
  health: () => fetchJSON<{ status: string; version: string; cad_engine: string; available_formats: string[] }>('/health'),

  validate: (design: GearboxDesign) =>
    fetchJSON<ValidationResult>('/designs/validate', {
      method: 'POST',
      body: JSON.stringify(design),
    }),

  calculate: (design: GearboxDesign) =>
    fetchJSON<CalculationResults>('/designs/calculate', {
      method: 'POST',
      body: JSON.stringify(design),
    }),

  generate: (design: GearboxDesign) =>
    fetchJSON<{ design_id: string; job_id: string }>('/designs/generate', {
      method: 'POST',
      body: JSON.stringify(design),
    }),

  getJob: (jobId: string) =>
    fetchJSON<JobInfo>(`/jobs/${jobId}`),

  listDesigns: () =>
    fetchJSON<DesignSummary[]>('/designs'),

  getDesign: (designId: string) =>
    fetchJSON<DesignRecord>(`/designs/${designId}`),

  getDrawings: (designId: string) =>
    fetchJSON<DrawingInfo[]>(`/designs/${designId}/drawings`),

  getComponents: (designId: string) =>
    fetchJSON<ComponentInfo[]>(`/designs/${designId}/components`),

  getBom: (designId: string) =>
    fetchJSON<BOM>(`/designs/${designId}/bom`),

  getValidation: (designId: string) =>
    fetchJSON<ValidationResult>(`/designs/${designId}/validation`),

  getCalculations: (designId: string) =>
    fetchJSON<CalculationResults>(`/designs/${designId}/calculations`),

  getFiles: (designId: string) =>
    fetchJSON<FileListResponse>(`/designs/${designId}/files`),

  getFileUrl: (designId: string, filename: string) =>
    `${API_BASE}/designs/${designId}/file/${filename}`,
};

export function pollJob(
  jobId: string,
  onUpdate: (job: JobInfo) => void,
  onComplete: (job: JobInfo) => void,
  intervalMs = 2000,
) {
  const poll = async () => {
    try {
      const job = await api.getJob(jobId);
      onUpdate(job);
      if (job.status === 'completed' || job.status === 'failed') {
        onComplete(job);
        return;
      }
      setTimeout(poll, intervalMs);
    } catch (e) {
      console.error('Poll error:', e);
      setTimeout(poll, intervalMs * 2);
    }
  };
  poll();
}
