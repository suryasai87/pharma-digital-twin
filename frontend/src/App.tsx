import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme, CssBaseline, Box } from '@mui/material';
import { QueryClient, QueryClientProvider } from 'react-query';

// Layout components
import AppLayout from '@components/Layout/AppLayout';

// Pages
import Overview from '@pages/Overview';
import BioreactorMonitoring from '@pages/BioreactorMonitoring';
import BatchQuality from '@pages/BatchQuality';
import PredictiveMaintenance from '@pages/PredictiveMaintenance';
import ContaminationDetection from '@pages/ContaminationDetection';
import AuditTrail from '@pages/AuditTrail';
import DigitalTwinView from '@pages/DigitalTwinView';

// Create Material-UI theme with pharma/Databricks styling
const theme = createTheme({
  palette: {
    primary: {
      main: '#1b3139',
      light: '#2e5266',
      dark: '#0d1a1f',
    },
    secondary: {
      main: '#ff5f46',
      light: '#ff8a76',
      dark: '#c43020',
    },
    info: {
      main: '#016bc1',
      light: '#3d8fd4',
      dark: '#004a87',
    },
    success: {
      main: '#2ecc71',
      light: '#5ed98f',
      dark: '#1f8b4e',
    },
    warning: {
      main: '#f39c12',
      light: '#f6b445',
      dark: '#c27b0a',
    },
    error: {
      main: '#e74c3c',
      light: '#ed796b',
      dark: '#b32a1b',
    },
    background: {
      default: '#f9f7f4',
      paper: '#ffffff',
    },
  },
  typography: {
    fontFamily: '"DM Sans", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 600,
    },
    h5: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 600,
    },
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0px 2px 8px rgba(27, 49, 57, 0.08)',
          borderRadius: '8px',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 500,
          borderRadius: '6px',
        },
      },
    },
  },
});

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 30000, // 30 seconds
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Router>
          <AppLayout>
            <Routes>
              <Route path="/" element={<Navigate to="/overview" replace />} />
              <Route path="/overview" element={<Overview />} />
              <Route path="/bioreactor" element={<BioreactorMonitoring />} />
              <Route path="/bioreactor/:bioreactorId" element={<DigitalTwinView />} />
              <Route path="/batch-quality" element={<BatchQuality />} />
              <Route path="/predictive-maintenance" element={<PredictiveMaintenance />} />
              <Route path="/contamination" element={<ContaminationDetection />} />
              <Route path="/audit" element={<AuditTrail />} />
            </Routes>
          </AppLayout>
        </Router>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
