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
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  DialogContentText,
} from '@mui/material';
import {
  Visibility as ViewIcon,
  PictureAsPdf as PdfIcon,
  Refresh as RefreshIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';
import { useQuery } from 'react-query';
import { getAnalysisHistory, downloadPdfReport, deleteAnalysis } from '../../api/analysis';
import { format } from 'date-fns';

const ReportsPage = () => {
  const navigate = useNavigate();
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [analysisToDelete, setAnalysisToDelete] = useState<string | null>(null);

  const {
    data: analyses = [],
    isLoading,
    isError,
    refetch,
  } = useQuery('analyses', getAnalysisHistory);

  const handleChangePage = (_event: unknown, newPage: number) => {
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
      link.download = `analysis-${query}-${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading PDF:', error);
    }
  };

  const handleDeleteClick = (id: string) => {
    setAnalysisToDelete(id);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (analysisToDelete) {
      try {
        await deleteAnalysis(analysisToDelete);
        refetch(); // Refresh the list
        setDeleteDialogOpen(false);
        setAnalysisToDelete(null);
      } catch (error) {
        console.error('Error deleting analysis:', error);
      }
    }
  };

  const handleDeleteCancel = () => {
    setDeleteDialogOpen(false);
    setAnalysisToDelete(null);
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
                <TableCell sx={{ minWidth: 200 }}>Query</TableCell>
                <TableCell sx={{ minWidth: 150 }}>Date</TableCell>
                <TableCell sx={{ minWidth: 100 }}>Status</TableCell>
                <TableCell align="right" sx={{ minWidth: 150 }}>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {analyses.length > 0 ? (
                analyses
                  .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                  .map((analysis: any) => (
                    <TableRow hover key={analysis.id || analysis.analysis_id}>
                      <TableCell>
                        <Typography variant="body2" noWrap>
                          {analysis.query}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        {(() => {
                          try {
                            const dateStr = analysis.createdAt || analysis.created_at;
                            if (!dateStr) return 'Unknown date';
                            return format(new Date(dateStr), 'MMM d, yyyy HH:mm');
                          } catch (error) {
                            return 'Invalid date';
                          }
                        })()}
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
                            onClick={() => handleViewReport(analysis.id || analysis.analysis_id)}
                            size="small"
                            color="primary"
                          >
                            <ViewIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Download PDF">
                          <IconButton
                            onClick={() =>
                              handleDownloadPdf(analysis.id || analysis.analysis_id, analysis.query)
                            }
                            size="small"
                            color="secondary"
                          >
                            <PdfIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Delete Analysis">
                          <IconButton
                            onClick={() => handleDeleteClick(analysis.id || analysis.analysis_id)}
                            size="small"
                            color="error"
                          >
                            <DeleteIcon />
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

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={handleDeleteCancel}
        aria-labelledby="delete-dialog-title"
        aria-describedby="delete-dialog-description"
      >
        <DialogTitle id="delete-dialog-title">
          Delete Analysis
        </DialogTitle>
        <DialogContent>
          <DialogContentText id="delete-dialog-description">
            Are you sure you want to delete this analysis? This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDeleteCancel} color="primary">
            Cancel
          </Button>
          <Button onClick={handleDeleteConfirm} color="error" variant="contained">
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ReportsPage;
