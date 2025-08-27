import api from './axios';

export interface AnalysisRequest {
  query: string;
  useLiveData: boolean;
}

export interface SentimentData {
  sentiment: string;
  count: number;
  percentage: number;
}

export interface ModelMetrics {
  accuracy: number;
  precision: number;
  recall: number;
  f1_score: number;
  confusion_matrix: number[][];
}

export interface AnalysisResult {
  id: string;
  query: string;
  createdAt: string;
  sentimentDistribution: SentimentData[];
  modelComparison: Record<string, number>; // model_name -> accuracy
  sentimentCounts: Record<string, SentimentData[]>; // model_name -> sentiment counts
  timeSeriesData: Array<Record<string, any>>; // daily sentiment data
  wordCloudData: Record<string, string[]>; // sentiment -> words
  confusionMatrices: Record<string, number[][]>; // model_name -> matrix
  metrics: Record<string, any>;
  modelMetrics: Record<string, ModelMetrics>;
  insights: Record<string, any>;
  rawData: Array<Record<string, any>>; // processed tweet data
}

export interface AnalysisSummary {
  analysis_id: string;
  query: string;
  created_at: string;
}

export interface DashboardData {
  analysisCount: number;
  analyses: {
    analysis_id: string;
    query: string;
    created_at: string;
  }[];
  singleAnalysis?: AnalysisResult;
}

export const runAnalysis = async (data: AnalysisRequest): Promise<AnalysisResult> => {
  const response = await api.post<AnalysisResult>('/api/analyze_query/', data);
  return response.data;
};

export const getAnalysisHistory = async (): Promise<AnalysisSummary[]> => {
  const response = await api.get<AnalysisSummary[]>('/api/analyses/');
  return response.data;
};

export const getAnalysisById = async (id: string): Promise<AnalysisResult> => {
  const response = await api.get<AnalysisResult>(`/api/analyses/${id}`);
  return response.data;
};

export const getDashboardData = async (): Promise<DashboardData> => {
  const response = await api.get<DashboardData>('/api/dashboard/data');
  return response.data;
};

export const downloadPdfReport = async (id: string): Promise<Blob> => {
  const response = await api.get(`/api/analyses/${id}/pdf`, {
    responseType: 'blob',
  });
  return response.data;
};

export const previewPdfReport = async (id: string): Promise<string> => {
  const blob = await downloadPdfReport(id);
  return URL.createObjectURL(blob);
};

// Get list of PDF reports (legacy reports table)
export const getReportsList = async (): Promise<any[]> => {
  const response = await api.get('/api/reports/');
  return response.data;
};

// Delete analysis by ID
export const deleteAnalysis = async (id: string): Promise<void> => {
  await api.delete(`/api/analyses/${id}`);
};
