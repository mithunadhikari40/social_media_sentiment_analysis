import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  IconButton,
  Button,
  Chip,
  CircularProgress,
  Tooltip,
} from '@mui/material';
import {
  Visibility as ViewIcon,
  PictureAsPdf as PdfIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { useQuery } from 'react-query';
import { getAnalysisHistory, downloadPdfReport } from '../../api/analysis';
import { format } from 'date-fns';

const ReportsPage = () => {
  const navigate = useNavigate();
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  const {
    data: analyses = [],
    isLoading,
    isError,
    refetch,
  } = useQuery('analyses', getAnalysisHistory);

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleViewReport = (id: string) => {
    navigate(`/analysis/${id}`);
  };

  const handleDownloadPdf = async (id: string, query: string) => {
    try {
      const blob = await downloadPdfReport(id);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `report-${query}-${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading PDF:', error);
    }
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    );
  }

  if (isError) {
    return (
      <Paper sx={{ p: 3, textAlign: 'center' }}>
        <Typography color="error" gutterBottom>
          Error loading reports. Please try again.
        </Typography>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={() => refetch()}
          sx={{ mt: 2 }}
        >
          Retry
        </Button>
      </Paper>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <Typography variant="h4" component="h1">
          Analysis Reports
        </Typography>
        <Button
          variant="contained"
          onClick={() => navigate('/analysis')}
          startIcon={<RefreshIcon />}
        >
          New Analysis
        </Button>
      </Box>

      <Paper sx={{ width: '100%', overflow: 'hidden', mb: 3 }}>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Query</TableCell>
                <TableCell>Date</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {analyses.length > 0 ? (
                analyses
                  .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                  .map((analysis: any) => (
                    <TableRow hover key={analysis.id}>
                      <TableCell>
                        <Typography variant="body2" noWrap>
                          {analysis.query}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        {format(new Date(analysis.createdAt), 'MMM d, yyyy HH:mm')}
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={analysis.status || 'Completed'}
                          color={
                            analysis.status === 'completed'
                              ? 'success'
                              : analysis.status === 'processing'
                              ? 'warning'
                              : 'default'
                          }
                          size="small"
                        />
                      </TableCell>
                      <TableCell align="right">
                        <Tooltip title="View Report">
                          <IconButton
                            onClick={() => handleViewReport(analysis.id)}
                            size="small"
                            color="primary"
                          >
                            <ViewIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Download PDF">
                          <IconButton
                            onClick={() =>
                              handleDownloadPdf(analysis.id, analysis.query)
                            }
                            size="small"
                            color="secondary"
                          >
                            <PdfIcon />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))
              ) : (
                <TableRow>
                  <TableCell colSpan={4} align="center" sx={{ py: 4 }}>
                    <Typography variant="body1" color="textSecondary">
                      No analysis reports found. Create your first analysis to get started.
                    </Typography>
                    <Button
                      variant="outlined"
                      onClick={() => navigate('/analysis')}
                      sx={{ mt: 2 }}
                    >
                      New Analysis
                    </Button>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
        {analyses.length > 0 && (
          <TablePagination
            rowsPerPageOptions={[5, 10, 25]}
            component="div"
            count={analyses.length}
            rowsPerPage={rowsPerPage}
            page={page}
            onPageChange={handleChangePage}
            onRowsPerPageChange={handleChangeRowsPerPage}
          />
        )}
      </Paper>
    </Box>
  );
};

export default ReportsPage;
