import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActionArea,
  Button,
  CircularProgress,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControlLabel,
  Switch,
  Alert,
  Chip,
  Avatar,
} from '@mui/material';
import {
  Assessment as AnalysisIcon,
  Add as AddIcon,
  TrendingUp as TrendingUpIcon,
  Timeline as TimelineIcon,
  BarChart as BarChartIcon,
  Close as CloseIcon,
  Send as SendIcon,
  Insights as InsightsIcon,
} from '@mui/icons-material';
import { useQuery } from 'react-query';
import { getAnalysisHistory, runAnalysis } from '../../api/analysis';
import { useFormik } from 'formik';
import * as Yup from 'yup';

const validationSchema = Yup.object({
  query: Yup.string().required('Please enter a search query'),
  useLiveData: Yup.boolean().default(false),
});

const DashboardPage = () => {
  const navigate = useNavigate();
  const [recentAnalyses, setRecentAnalyses] = useState<any[]>([]);
  const [openDialog, setOpenDialog] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [dialogError, setDialogError] = useState('');

  const { data: analyses, isLoading, error, refetch } = useQuery('analyses', getAnalysisHistory);

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
        refetch();
        navigate(`/analysis/${result.id}`, { state: { analysis: result } });
      } catch (err) {
        console.error('Analysis error:', err);
        setDialogError('Failed to run analysis. Please try again.');
      } finally {
        setIsSubmitting(false);
      }
    },
  });

  useEffect(() => {
    if (analyses) {
      setRecentAnalyses(analyses.slice(0, 3));
    }
  }, [analyses]);

  const stats = [
    { 
      title: 'Total Analyses', 
      value: analyses?.length || 0, 
      icon: <TimelineIcon fontSize="large" color="primary" />,
      color: '#1976d2'
    },
    { 
      title: 'This Month', 
      value: analyses?.filter(a => new Date(a.createdAt).getMonth() === new Date().getMonth()).length || 0, 
      icon: <TrendingUpIcon fontSize="large" color="success" />,
      color: '#2e7d32'
    },
    { 
      title: 'Recent', 
      value: analyses?.filter(a => new Date(a.createdAt) > new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)).length || 0, 
      icon: <BarChartIcon fontSize="large" color="warning" />,
      color: '#ed6c02'
    },
  ];

  const handleCloseDialog = () => {
    setOpenDialog(false);
    formik.resetForm();
    setDialogError('');
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress size={60} />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 3, maxWidth: 1200, mx: 'auto' }}>
        <Paper sx={{ p: 4, textAlign: 'center', borderRadius: 3 }}>
          <Typography color="error" variant="h6" gutterBottom>
            Error loading dashboard data
          </Typography>
          <Typography variant="body1" color="textSecondary" paragraph>
            Please try again later or contact support if the issue persists.
          </Typography>
          <Button variant="contained" onClick={() => window.location.reload()}>
            Retry
          </Button>
        </Paper>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3, maxWidth: 1200, mx: 'auto' }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <Box>
          <Typography variant="h4" component="h1" fontWeight="bold" gutterBottom>
            Dashboard
          </Typography>
          <Typography variant="body1" color="textSecondary">
            Welcome back! Here's your social media analysis overview.
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

      {/* Stats Cards */}
      <Grid container spacing={3} mb={4}>
        {stats.map((stat, index) => (
          <Grid item xs={12} sm={4} key={index}>
            <Card 
              sx={{ 
                height: '100%',
                borderRadius: 3,
                background: `linear-gradient(135deg, ${stat.color}15 0%, ${stat.color}05 100%)`,
                border: `1px solid ${stat.color}20`,
                transition: 'transform 0.2s ease-in-out',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: 4,
                }
              }}
            >
              <CardContent sx={{ p: 3 }}>
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Box>
                    <Typography color="textSecondary" variant="body2" gutterBottom>
                      {stat.title}
                    </Typography>
                    <Typography variant="h3" component="div" fontWeight="bold">
                      {stat.value}
                    </Typography>
                  </Box>
                  <Avatar sx={{ bgcolor: `${stat.color}20`, width: 56, height: 56 }}>
                    {stat.icon}
                  </Avatar>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Main Content */}
      <Grid container spacing={4}>
        {/* Recent Analyses or Empty State */}
        <Grid item xs={12} lg={8}>
          <Paper sx={{ p: 3, borderRadius: 3, height: 'fit-content' }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
              <Typography variant="h6" fontWeight="bold">
                Recent Analyses
              </Typography>
              {recentAnalyses.length > 0 && (
                <Button 
                  variant="outlined" 
                  size="small"
                  onClick={() => navigate('/reports')}
                >
                  View All
                </Button>
              )}
            </Box>
            
            {recentAnalyses.length > 0 ? (
              <Grid container spacing={2}>
                {recentAnalyses.map((analysis) => (
                  <Grid item xs={12} key={analysis.id}>
                    <Card 
                      sx={{ 
                        borderRadius: 2,
                        border: '1px solid',
                        borderColor: 'divider',
                        '&:hover': {
                          borderColor: 'primary.main',
                          boxShadow: 2,
                        }
                      }}
                    >
                      <CardActionArea onClick={() => navigate(`/analysis/${analysis.id}`)}>
                        <CardContent sx={{ p: 2 }}>
                          <Box display="flex" alignItems="center" justifyContent="space-between">
                            <Box display="flex" alignItems="center" flex={1}>
                              <Avatar sx={{ bgcolor: 'primary.light', mr: 2 }}>
                                <AnalysisIcon />
                              </Avatar>
                              <Box>
                                <Typography variant="subtitle1" fontWeight="medium">
                                  {analysis.query}
                                </Typography>
                                <Typography variant="body2" color="textSecondary">
                                  {new Date(analysis.createdAt).toLocaleDateString('en-US', {
                                    year: 'numeric',
                                    month: 'short',
                                    day: 'numeric'
                                  })}
                                </Typography>
                              </Box>
                            </Box>
                            <Chip 
                              label="View Results" 
                              size="small" 
                              color="primary" 
                              variant="outlined"
                            />
                          </Box>
                        </CardContent>
                      </CardActionArea>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            ) : (
              <Box textAlign="center" py={6}>
                <Avatar sx={{ bgcolor: 'primary.light', width: 80, height: 80, mx: 'auto', mb: 2 }}>
                  <InsightsIcon sx={{ fontSize: 40 }} />
                </Avatar>
                <Typography variant="h6" gutterBottom>
                  No analyses yet
                </Typography>
                <Typography variant="body1" color="textSecondary" paragraph>
                  Start your first social media sentiment analysis to see insights here.
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={() => setOpenDialog(true)}
                  sx={{ mt: 2, py: 1.5 }}
                >
                  Create Your First Analysis
                </Button>
              </Box>
            )}
          </Paper>
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12} lg={4}>
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
                sx={{ justifyContent: 'flex-start', py: 1.5 }}
              >
                New Analysis
              </Button>
              <Button
                variant="outlined"
                fullWidth
                startIcon={<AnalysisIcon />}
                onClick={() => navigate('/reports')}
                sx={{ justifyContent: 'flex-start', py: 1.5 }}
              >
                View All Reports
              </Button>
              <Button
                variant="outlined"
                fullWidth
                startIcon={<TimelineIcon />}
                onClick={() => navigate('/analysis')}
                sx={{ justifyContent: 'flex-start', py: 1.5 }}
              >
                Analysis Tools
              </Button>
            </Box>
          </Paper>

          {/* Tips Card */}
          <Paper sx={{ p: 3, borderRadius: 3, bgcolor: 'grey.50' }}>
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
        </Grid>
      </Grid>

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
