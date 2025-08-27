import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import {
  Box,
  Typography,
  TextField,
  Button,
  Paper,
  FormControlLabel,
  Switch,
  CircularProgress,
  Grid,
  Card,
  CardContent,
  Alert,
} from '@mui/material';
import { Send as SendIcon } from '@mui/icons-material';
import { runAnalysis } from '../../api/analysis';

const validationSchema = Yup.object({
  query: Yup.string().required('Please enter a search query'),
  useLiveData: Yup.boolean().default(false),
});

const AnalysisPage = () => {
  const navigate = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  const formik = useFormik({
    initialValues: {
      query: '',
      useLiveData: false,
    },
    validationSchema,
    onSubmit: async (values) => {
      try {
        setIsSubmitting(true);
        setError('');
        const result = await runAnalysis(values);
        navigate(`/analysis/${result.id}`, { state: { analysis: result } });
      } catch (err) {
        console.error('Analysis error:', err);
        setError('Failed to run analysis. Please try again.');
      } finally {
        setIsSubmitting(false);
      }
    },
  });

  return (
    <Box sx={{ p: 3, maxWidth: 1200, mx: 'auto' }}>
      <Box mb={4}>
        <Typography variant="h4" component="h1" gutterBottom>
          New Analysis
        </Typography>
        <Typography variant="body1" color="textSecondary" paragraph>
          Enter a search query to analyze social media sentiment and trends.
        </Typography>
      </Box>

      <Grid container spacing={4}>
        <Grid item xs={12} md={8}>
          <Paper elevation={0} sx={{ p: 3, mb: 3 }}>
            <form onSubmit={formik.handleSubmit}>
              {error && (
                <Alert severity="error" sx={{ mb: 3 }}>
                  {error}
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
                rows={4}
                value={formik.values.query}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.query && Boolean(formik.errors.query)}
                helperText={formik.touched.query && formik.errors.query}
                disabled={isSubmitting}
                sx={{ mb: 2 }}
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
                sx={{ mb: 3, display: 'block' }}
              />

              <Button
                type="submit"
                variant="contained"
                color="primary"
                size="large"
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
            </form>
          </Paper>

          {/* Analysis Tips */}
          <Paper elevation={0} sx={{ p: 3, backgroundColor: 'grey.50' }}>
            <Typography variant="h6" gutterBottom>
              Analysis Tips
            </Typography>
            <ul style={{ paddingLeft: 20, margin: 0 }}>
              <li>
                <Typography variant="body2" paragraph>
                  Use hashtags (#) to track specific topics or campaigns
                </Typography>
              </li>
              <li>
                <Typography variant="body2" paragraph>
                  Use OR between terms to search for multiple keywords
                </Typography>
              </li>
              <li>
                <Typography variant="body2" paragraph>
                  Use quotes for exact phrase matches
                </Typography>
              </li>
              <li>
                <Typography variant="body2">
                  Enable live data for the most recent social media posts
                </Typography>
              </li>
            </ul>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Analyses
              </Typography>
              <Typography variant="body2" color="textSecondary" paragraph>
                Your recent analyses will appear here.
              </Typography>
              <Button
                variant="outlined"
                size="small"
                fullWidth
                onClick={() => navigate('/reports')}
              >
                View All Reports
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default AnalysisPage;
