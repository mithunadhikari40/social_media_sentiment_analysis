import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Paper,
  Button,
  Breadcrumbs,
  Link,
  CircularProgress,
  Alert,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  Download as DownloadIcon,
} from '@mui/icons-material';
import { getAnalysisById, downloadPdfReport } from '../../api/analysis';
import type { AnalysisResult } from '../../api/analysis';
import ChartRenderer from '../../components/charts/ChartRenderer';

const AnalysisDetailsPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [downloadingPdf, setDownloadingPdf] = useState(false);

  useEffect(() => {
    if (id) {
      fetchAnalysis(id);
    }
  }, [id]);

  const fetchAnalysis = async (analysisId: string) => {
    try {
      setLoading(true);
      setError('');
      const result = await getAnalysisById(analysisId);
      setAnalysis(result);
    } catch (err) {
      console.error('Error fetching analysis:', err);
      setError('Failed to load analysis. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPdf = async () => {
    if (!id || !analysis) return;
    
    try {
      setDownloadingPdf(true);
      const blob = await downloadPdfReport(id);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      
      // Create a clean filename
      const queryText = analysis.query.replace(/[^a-zA-Z0-9]/g, '-').substring(0, 20);
      const dateStr = new Date().toISOString().split('T')[0];
      link.download = `analysis-${queryText}-${dateStr}.pdf`;
      
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading PDF:', error);
      setError('Failed to download PDF report. Please try again.');
    } finally {
      setDownloadingPdf(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 3, maxWidth: 1200, mx: 'auto' }}>
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
        <Button
          variant="outlined"
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/reports')}
        >
          Back to Reports
        </Button>
      </Box>
    );
  }

  if (!analysis) {
    return (
      <Box sx={{ p: 3, maxWidth: 1200, mx: 'auto' }}>
        <Alert severity="warning" sx={{ mb: 3 }}>
          Analysis not found.
        </Alert>
        <Button
          variant="outlined"
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/reports')}
        >
          Back to Reports
        </Button>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3, maxWidth: 1200, mx: 'auto' }}>
      {/* Breadcrumbs */}
      <Breadcrumbs sx={{ mb: 3 }}>
        <Link
          component="button"
          variant="body2"
          onClick={() => navigate('/dashboard')}
          sx={{ textDecoration: 'none' }}
        >
          Dashboard
        </Link>
        <Link
          component="button"
          variant="body2"
          onClick={() => navigate('/reports')}
          sx={{ textDecoration: 'none' }}
        >
          Reports
        </Link>
        <Typography variant="body2" color="textPrimary">
          Analysis Details
        </Typography>
      </Breadcrumbs>

      {/* Header */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
          <Box>
            <Typography variant="h4" component="h1" gutterBottom>
              Analysis Results
            </Typography>
            <Typography variant="h6" color="textSecondary" gutterBottom>
              Query: {analysis.query}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Created on {new Date(analysis.createdAt).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
              })}
            </Typography>
          </Box>
          <Box display="flex" gap={2}>
            <Button
              variant="outlined"
              startIcon={downloadingPdf ? <CircularProgress size={20} /> : <DownloadIcon />}
              onClick={handleDownloadPdf}
              disabled={downloadingPdf}
            >
              {downloadingPdf ? 'Generating PDF...' : 'Download PDF'}
            </Button>
            <Button
              variant="outlined"
              startIcon={<ArrowBackIcon />}
              onClick={() => navigate('/reports')}
            >
              Back to Reports
            </Button>
          </Box>
        </Box>
      </Paper>

      {/* Analysis Charts */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h5" gutterBottom>
          Analysis Visualizations
        </Typography>
        <ChartRenderer analysis={analysis} />
      </Paper>

      {/* Key Insights */}
      {analysis.insights && Object.keys(analysis.insights).length > 0 && (
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h5" gutterBottom>
            Key Insights
          </Typography>
          <Box 
            sx={{ 
              display: 'flex', 
              flexWrap: 'wrap', 
              gap: 3,
              '& > *': { 
                flex: '1 1 300px',
                minWidth: '300px'
              }
            }}
          >
            {Object.entries(analysis.insights).map(([key, value]) => {
              const title = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
              
              // Handle different types of insights
              if (typeof value === 'object' && value !== null) {
                return (
                  <Card key={key} sx={{ height: 'fit-content' }}>
                    <CardContent>
                      <Typography variant="h6" gutterBottom color="primary">
                        {title}
                      </Typography>
                      {key === 'SentimentBalance' ? (
                        <TableContainer>
                          <Table size="small">
                            <TableHead>
                              <TableRow>
                                <TableCell><strong>Sentiment</strong></TableCell>
                                <TableCell align="right"><strong>Percentage</strong></TableCell>
                              </TableRow>
                            </TableHead>
                            <TableBody>
                              {Object.entries(value as Record<string, number>).map(([sentiment, percentage]) => (
                                <TableRow key={sentiment}>
                                  <TableCell>
                                    <Chip 
                                      label={sentiment.charAt(0).toUpperCase() + sentiment.slice(1)}
                                      color={
                                        sentiment === 'positive' ? 'success' : 
                                        sentiment === 'negative' ? 'error' : 'default'
                                      }
                                      size="small"
                                    />
                                  </TableCell>
                                  <TableCell align="right">{percentage}%</TableCell>
                                </TableRow>
                              ))}
                            </TableBody>
                          </Table>
                        </TableContainer>
                      ) : key === 'BestModel' ? (
                        <Box>
                          <Typography variant="body1">
                            <strong>Model:</strong> {(value as any).name}
                          </Typography>
                          <Typography variant="body1">
                            <strong>Accuracy:</strong> {((value as any).accuracy * 100).toFixed(1)}%
                          </Typography>
                        </Box>
                      ) : (
                        <TableContainer>
                          <Table size="small">
                            <TableBody>
                              {Object.entries(value as Record<string, any>).map(([k, v]) => (
                                <TableRow key={k}>
                                  <TableCell><strong>{k}</strong></TableCell>
                                  <TableCell>{String(v)}</TableCell>
                                </TableRow>
                              ))}
                            </TableBody>
                          </Table>
                        </TableContainer>
                      )}
                    </CardContent>
                  </Card>
                );
              } else {
                return (
                  <Card key={key} sx={{ height: 'fit-content' }}>
                    <CardContent>
                      <Typography variant="h6" gutterBottom color="primary">
                        {title}
                      </Typography>
                      <Typography variant="body1">
                        {String(value)}
                      </Typography>
                    </CardContent>
                  </Card>
                );
              }
            })}
          </Box>
        </Paper>
      )}

      {/* Model Metrics */}
      {analysis.modelMetrics && Object.keys(analysis.modelMetrics).length > 0 && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h5" gutterBottom>
            Model Performance Metrics
          </Typography>
          <Box display="flex" flexWrap="wrap" gap={3}>
            {Object.entries(analysis.modelMetrics).map(([modelName, metrics]) => (
              <Box key={modelName} sx={{ minWidth: 250 }}>
                <Typography variant="h6" gutterBottom>
                  {modelName.toUpperCase()}
                </Typography>
                <Typography variant="body2">Accuracy: {(metrics.accuracy * 100).toFixed(2)}%</Typography>
                <Typography variant="body2">Precision: {(metrics.precision * 100).toFixed(2)}%</Typography>
                <Typography variant="body2">Recall: {(metrics.recall * 100).toFixed(2)}%</Typography>
                <Typography variant="body2">F1 Score: {(metrics.f1_score * 100).toFixed(2)}%</Typography>
              </Box>
            ))}
          </Box>
        </Paper>
      )}
    </Box>
  );
};

export default AnalysisDetailsPage;
