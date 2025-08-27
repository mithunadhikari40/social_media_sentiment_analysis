import { CssBaseline, ThemeProvider, Box } from '@mui/material';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { ReactQueryDevtools } from 'react-query/devtools';
import { AuthProvider, useAuth } from './context/AuthContext';
import theme from './theme/theme';

// Lazy load pages
import { lazy, Suspense } from 'react';
import LoadingScreen from './components/common/LoadingScreen';
import Layout from './components/layout/Layout';

const LoginPage = lazy(() => import('./pages/auth/LoginPage'));
const RegisterPage = lazy(() => import('./pages/auth/RegisterPage'));
const DashboardPage = lazy(() => import('./pages/dashboard/DashboardPage'));
const AnalysisPage = lazy(() => import('./pages/analysis/AnalysisPage'));
const AnalysisDetailsPage = lazy(() => import('./pages/analysis/AnalysisDetailsPage'));
const ReportsPage = lazy(() => import('./pages/reports/ReportsPage'));
const ProfilePage = lazy(() => import('./pages/profile/ProfilePage'));

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

// Protected Route Component
const ProtectedRoute = ({ children }: { children: React.ReactElement }) => {
  const { isAuthenticated, loading, user, token } = useAuth();
  
  console.log('ProtectedRoute - isAuthenticated:', isAuthenticated);
  console.log('ProtectedRoute - loading:', loading);
  console.log('ProtectedRoute - user:', user);
  console.log('ProtectedRoute - token exists:', !!token);

  if (loading) {
    console.log('ProtectedRoute - Loading, showing loading screen');
    return <LoadingScreen />;
  }

  if (!isAuthenticated) {
    console.log('ProtectedRoute - Not authenticated, redirecting to login');
    return <Navigate to="/login" replace />;
  }

  console.log('ProtectedRoute - User is authenticated, rendering children');
  return children;
};

// Public Only Route Component
const PublicRoute = ({ children }: { children: React.ReactElement }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <LoadingScreen />;
  }

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
};

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <AuthProvider>
          <Router>
            <Box sx={{ display: 'flex', minHeight: '100vh' }}>
              <Suspense fallback={<LoadingScreen />}>
                <Routes>
                  {/* Public Routes */}
                  <Route
                    path="/login"
                    element={
                      <PublicRoute>
                        <LoginPage />
                      </PublicRoute>
                    }
                  />
                  <Route
                    path="/register"
                    element={
                      <PublicRoute>
                        <RegisterPage />
                      </PublicRoute>
                    }
                  />

                  {/* Protected Routes */}
                  <Route
                    path="/"
                    element={
                      <ProtectedRoute>
                        <Layout />
                      </ProtectedRoute>
                    }
                  >
                    <Route index element={<Navigate to="/dashboard" replace />} />
                    <Route path="dashboard" element={<DashboardPage />} />
                    <Route path="analysis" element={<AnalysisPage />} />
                    <Route path="analysis/:id" element={<AnalysisDetailsPage />} />
                    <Route path="reports" element={<ReportsPage />} />
                    <Route path="profile" element={<ProfilePage />} />
                  </Route>

                  {/* 404 Route */}
                  <Route path="*" element={<Navigate to="/dashboard" replace />} />
                </Routes>
              </Suspense>
            </Box>
          </Router>
        </AuthProvider>
      </ThemeProvider>
      {import.meta.env.DEV && <ReactQueryDevtools initialIsOpen={false} />}
    </QueryClientProvider>
  );
}

export default App;
