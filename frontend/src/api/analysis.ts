import api from './axios';

export interface AnalysisRequest {
  query: string;
  useLiveData: boolean;
}

export interface ChartData {
  type: string;
  data: any;
  options?: any;
}

export interface AnalysisResult {
  id: string;
  query: string;
  createdAt: string;
  charts: ChartData[];
  metrics: Record<string, any>;
}

export const runAnalysis = async (data: AnalysisRequest): Promise<AnalysisResult> => {
  const response = await api.post<AnalysisResult>('/api/analyze_query/', data);
  return response.data;
};

export const getAnalysisHistory = async (): Promise<AnalysisResult[]> => {
  const response = await api.get<AnalysisResult[]>('/api/reports/');
  return response.data;
};

export const getAnalysisById = async (id: string): Promise<AnalysisResult> => {
  const response = await api.get<AnalysisResult>(`/api/reports/${id}`);
  return response.data;
};

export const downloadPdfReport = async (id: string): Promise<Blob> => {
  const response = await api.get(`/api/${id}/pdf/`, {
    responseType: 'blob',
  });
  return response.data;
};

export const previewPdfReport = async (id: string): Promise<string> => {
  const blob = await downloadPdfReport(id);
  return URL.createObjectURL(blob);
};
