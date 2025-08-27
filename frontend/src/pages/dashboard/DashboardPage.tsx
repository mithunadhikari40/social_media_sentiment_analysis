import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import {
  Typography,
  Box,
  Button,
  Card,
  Avatar,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControlLabel,
  Switch,
  Alert,
  Paper,
  useTheme,
  Stack,
  CircularProgress,
} from '@mui/material';
import type { Theme } from '@mui/material/styles';
import {
  Add as AddIcon,
  TrendingUp as TrendingUpIcon,
  Assessment as AssessmentIcon,
  Timeline as TimelineIcon,
  Close as CloseIcon,
  Send as SendIcon,
  Insights as InsightsIcon,
  BarChart as BarChartIcon,
} from '@mui/icons-material';
import { getDashboardData, runAnalysis } from '../../api/analysis';
import type { DashboardData, AnalysisResult } from '../../api/analysis';
import ChartRenderer from '../../components/charts/ChartRenderer';

const validationSchema = Yup.object({
  query: Yup.string().required('Please enter a search query'),
  useLiveData: Yup.boolean().default(false),
});

const DashboardPage = () => {
  const navigate = useNavigate();
  const theme = useTheme();
  const [openDialog, setOpenDialog] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [dialogError, setDialogError] = useState<string>('');
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const data = await getDashboardData();
      setDashboardData(data);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const formik = useFormik({
    initialValues: {
      query: '',
      useLiveData: false,
    },
    validationSchema,
    onSubmit: async (values) => {
      try {
        setIsSubmitting(true);
        setDialogError('');
        const result = await runAnalysis(values);
        setOpenDialog(false);
        formik.resetForm();
        // Refresh dashboard data
        await fetchDashboardData();
        // Navigate to the new analysis
        navigate(`/analysis/${result.id}`);
      } catch (error: any) {
        setDialogError(error.message || 'Failed to run analysis');
      } finally {
        setIsSubmitting(false);
      }
    },
  });

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setDialogError('');
    formik.resetForm();
  };

  // Mock stats data - replace with real data from API
  const stats = [
    { title: 'Total Analyses', value: dashboardData?.analyses?.length || 0, icon: <TrendingUpIcon />, color: '#1976d2' },
    { title: 'Recent Analyses', value: dashboardData?.analyses?.length || 0, icon: <BarChartIcon />, color: '#388e3c' },
    { title: 'Avg Accuracy', value: '94%', icon: <TimelineIcon />, color: '#f57c00' },
    { title: 'Insights Generated', value: '127', icon: <InsightsIcon />, color: '#7b1fa2' },
  ];

  // Check if we should auto-display a single analysis
  const singleAnalysis = dashboardData?.analyses?.length === 1 ? dashboardData?.analyses[0] : null;

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <Box>
          <Typography variant="h4" component="h1" fontWeight="bold" gutterBottom>
            Social Media Analysis Dashboard
          </Typography>
          <Typography variant="body1" color="textSecondary">
            Monitor sentiment trends and analyze social media data
          </Typography>
        </Box>
        <Button
          variant="contained"
          size="large"
          startIcon={<AddIcon />}
          onClick={() => setOpenDialog(true)}
          sx={{ py: 1.5 }}
        >
          New Analysis
        </Button>
      </Box>

      <Box display="flex" flexWrap="wrap" gap={3}>
        {/* Quick Stats Cards */}
        {[
          { title: 'Total Analyses', value: dashboardData?.analyses?.length || 0, icon: <AssessmentIcon />, color: 'primary' },
          { title: 'Avg Sentiment Score', value: '0.75', icon: <TrendingUpIcon />, color: 'success' },
          { title: 'Recent Analyses', value: dashboardData?.analyses?.length || 0, icon: <TimelineIcon />, color: 'info' },
          { title: 'Data Sources', value: '3', icon: <BarChartIcon />, color: 'warning' },
        ].map((stat, index) => (
          <Box key={index} sx={{ flex: '1 1 250px', minWidth: '250px' }}>
            <Card sx={{ 
              p: 2, 
              borderRadius: 3,
              background: `linear-gradient(135deg, ${(theme.palette as any)[stat.color].light}20, ${(theme.palette as any)[stat.color].main}10)`,
              border: `1px solid ${(theme.palette as any)[stat.color].light}40`,
              transition: 'all 0.3s ease',
              '&:hover': {
                transform: 'translateY(-2px)',
                boxShadow: theme.shadows[8],
              }
            }}>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h4" fontWeight="bold" color={`${stat.color}.main`}>
                    {stat.value}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    {stat.title}
                  </Typography>
                </Box>
                <Box sx={{ color: `${stat.color}.main`, opacity: 0.7 }}>
                  {stat.icon}
                </Box>
              </Box>
            </Card>
          </Box>
        ))}
      </Box>

      {/* Main Content */}
      <Box sx={{ mt: 2, display: 'flex', gap: 3, flexWrap: 'wrap' }}>
        <Box sx={{ flex: singleAnalysis ? '1 1 100%' : '1 1 65%', minWidth: '300px' }}>
          {singleAnalysis ? (
            // Auto-display single analysis
            <Paper sx={{ p: 3, borderRadius: 3 }}>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                <Box>
                  <Typography variant="h6" fontWeight="bold">
                    Analysis Results: {singleAnalysis.query}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Created on {new Date((singleAnalysis as any).created_at).toLocaleDateString('en-US', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </Typography>
                </Box>
                <Button 
                  variant="outlined" 
                  size="small"
                  onClick={() => navigate(`/analysis/${(singleAnalysis as any).analysis_id}`)}
                >
                  View Full Analysis
                </Button>
              </Box>
              
              {/* Analysis Charts */}
              {(singleAnalysis as any).sentimentDistribution ? (
                <ChartRenderer analysis={singleAnalysis as unknown as AnalysisResult} />
              ) : (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Typography variant="body2" color="textSecondary">
                    No recent analyses found. Start your first analysis above!
                  </Typography>
                </Box>
              )}

              {/* Key Insights */}
              <Box mt={3}>
                <Typography variant="h6" gutterBottom>
                  Key Insights
                </Typography>
                <Paper sx={{ p: 2, borderRadius: 2, bgcolor: 'grey.50' }}>
                  <Typography variant="body2">
                    Analysis completed successfully. Full results available in detailed view.
                  </Typography>
                </Paper>
              </Box>
            </Paper>
          ) : (
            // Show recent analyses list
            <Paper sx={{ p: 3, borderRadius: 3 }}>
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                Recent Analyses
              </Typography>
              {dashboardData?.analyses && dashboardData.analyses.length > 0 ? (
                <Stack spacing={2}>
                  {dashboardData.analyses.slice(0, 5).map((analysis: any, index: number) => (
                    <Card 
                      key={index}
                      sx={{ 
                        p: 2, 
                        borderRadius: 2,
                        cursor: 'pointer',
                        transition: 'all 0.2s ease',
                        '&:hover': {
                          transform: 'translateX(4px)',
                          boxShadow: theme.shadows[4],
                        }
                      }}
                      onClick={() => navigate(`/analysis/${analysis.analysis_id}`)}
                    >
                      <Box display="flex" justifyContent="space-between" alignItems="center">
                        <Box>
                          <Typography variant="subtitle2" fontWeight="medium">
                            {analysis.query.length > 50 ? `${analysis.query.substring(0, 50)}...` : analysis.query}
                          </Typography>
                          <Typography variant="caption" color="textSecondary">
                            {new Date(analysis.created_at).toLocaleDateString()}
                          </Typography>
                        </Box>
                        <InsightsIcon color="action" fontSize="small" />
                      </Box>
                    </Card>
                  ))}
                </Stack>
              ) : (
                <Box textAlign="center" py={6}>
                  <Avatar sx={{ mx: 'auto', mb: 2, bgcolor: 'grey.100', width: 64, height: 64 }}>
                    <AssessmentIcon sx={{ fontSize: 32, color: 'grey.400' }} />
                  </Avatar>
                  <Typography variant="h6" gutterBottom>
                    No analyses yet
                  </Typography>
                  <Typography variant="body2" color="textSecondary" mb={3}>
                    Create your first analysis to get started with social media sentiment analysis.
                  </Typography>
                  <Button
                    variant="contained"
                    startIcon={<AddIcon />}
                    onClick={() => setOpenDialog(true)}
                  >
                    Create Your First Analysis
                  </Button>
                </Box>
              )}
            </Paper>
          )}
        </Box>

        {/* Quick Actions - Only show if not displaying single analysis */}
        {!singleAnalysis && (
          <Box sx={{ flex: '1 1 30%', minWidth: '300px' }}>
            <Paper sx={{ p: 3, borderRadius: 3, mb: 3 }}>
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                Quick Actions
              </Typography>
              <Box display="flex" flexDirection="column" gap={2}>
                <Button
                  variant="outlined"
                  fullWidth
                  startIcon={<AddIcon />}
                  onClick={() => setOpenDialog(true)}
                >
                  New Analysis
                </Button>
                <Button
                  variant="outlined"
                  fullWidth
                  startIcon={<TrendingUpIcon />}
                  onClick={() => navigate('/reports')}
                >
                  View Reports
                </Button>
              </Box>
            </Paper>

            <Paper sx={{ p: 3, borderRadius: 3 }}>
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                Analysis Tips
              </Typography>
              <Box component="ul" sx={{ pl: 2, m: 0 }}>
                <Typography component="li" variant="body2" paragraph>
                  Use hashtags (#) to track specific topics
                </Typography>
                <Typography component="li" variant="body2" paragraph>
                  Use OR between terms for multiple keywords
                </Typography>
                <Typography component="li" variant="body2">
                  Enable live data for recent posts
                </Typography>
              </Box>
            </Paper>
          </Box>
        )}
      </Box>

      {/* New Analysis Dialog */}
      <Dialog 
        open={openDialog} 
        onClose={handleCloseDialog}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: { borderRadius: 3 }
        }}
      >
        <DialogTitle sx={{ pb: 1 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6" fontWeight="bold">
              Create New Analysis
            </Typography>
            <Button
              onClick={handleCloseDialog}
              sx={{ minWidth: 'auto', p: 1 }}
            >
              <CloseIcon />
            </Button>
          </Box>
        </DialogTitle>
        <form onSubmit={formik.handleSubmit}>
          <DialogContent>
            {dialogError && (
              <Alert severity="error" sx={{ mb: 3 }}>
                {dialogError}
              </Alert>
            )}
            
            <TextField
              fullWidth
              id="query"
              name="query"
              label="Search Query"
              placeholder="e.g., #YourBrandName OR @YourHandle"
              variant="outlined"
              multiline
              rows={3}
              value={formik.values.query}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.query && Boolean(formik.errors.query)}
              helperText={formik.touched.query && formik.errors.query}
              disabled={isSubmitting}
              sx={{ mb: 3 }}
            />

            <FormControlLabel
              control={
                <Switch
                  name="useLiveData"
                  checked={formik.values.useLiveData}
                  onChange={formik.handleChange}
                  color="primary"
                />
              }
              label="Use live social media data (may take longer)"
              sx={{ mb: 2 }}
            />
          </DialogContent>
          <DialogActions sx={{ p: 3, pt: 1 }}>
            <Button onClick={handleCloseDialog} disabled={isSubmitting}>
              Cancel
            </Button>
            <Button
              type="submit"
              variant="contained"
              startIcon={
                isSubmitting ? (
                  <CircularProgress size={20} color="inherit" />
                ) : (
                  <SendIcon />
                )
              }
              disabled={isSubmitting || !formik.dirty || !formik.isValid}
            >
              {isSubmitting ? 'Analyzing...' : 'Run Analysis'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </Box>
  );
};

export default DashboardPage;
