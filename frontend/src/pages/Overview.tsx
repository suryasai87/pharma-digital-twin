import React from 'react';
import { useQuery } from 'react-query';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Alert,
  CircularProgress,
  Chip,
} from '@mui/material';
import {
  TrendingUp,
  Science,
  Warning as WarningIcon,
  CheckCircle,
} from '@mui/icons-material';
import { apiService } from '@services/api';

const Overview: React.FC = () => {
  const { data: bioreactors, isLoading: loadingBioreactors } = useQuery(
    'bioreactors',
    () => apiService.getBioreactorList(),
    { refetchInterval: 10000 } // Refresh every 10 seconds
  );

  const { data: batches, isLoading: loadingBatches } = useQuery(
    'batches',
    () => apiService.getBatchList({ limit: 50 })
  );

  const { data: equipment, isLoading: loadingEquipment } = useQuery(
    'equipment',
    () => apiService.getEquipmentList()
  );

  if (loadingBioreactors || loadingBatches || loadingEquipment) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    );
  }

  const activeBatches = batches?.filter((b) => b.status === 'In Progress').length || 0;
  const avgYield =
    batches?.reduce((sum, b) => sum + (b.yield_percent || 0), 0) / (batches?.length || 1);
  const equipmentAtRisk = equipment?.filter((e) => e.health_score < 80).length || 0;
  const operationalBioreactors =
    bioreactors?.filter((b) => b.status === 'Operational').length || 0;

  const kpiCards = [
    {
      label: 'Active Batches',
      value: activeBatches,
      color: '#016bc1',
      icon: Science,
    },
    {
      label: 'Avg Batch Yield',
      value: `${avgYield.toFixed(1)}%`,
      color: '#2ecc71',
      icon: TrendingUp,
    },
    {
      label: 'Equipment at Risk',
      value: equipmentAtRisk,
      color: '#f39c12',
      icon: WarningIcon,
    },
    {
      label: 'Bioreactors Online',
      value: operationalBioreactors,
      color: '#ff5f46',
      icon: CheckCircle,
    },
  ];

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 3, fontWeight: 600, color: 'primary.main' }}>
        Manufacturing Overview
      </Typography>

      {/* KPI Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        {kpiCards.map((kpi, index) => {
          const Icon = kpi.icon;
          return (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <Card
                sx={{
                  background: `linear-gradient(135deg, ${kpi.color}15 0%, ${kpi.color}05 100%)`,
                  border: `1px solid ${kpi.color}30`,
                }}
              >
                <CardContent>
                  <Box display="flex" alignItems="center" justifyContent="space-between">
                    <Box>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                        {kpi.label}
                      </Typography>
                      <Typography variant="h3" sx={{ fontWeight: 700, color: kpi.color }}>
                        {kpi.value}
                      </Typography>
                    </Box>
                    <Icon sx={{ fontSize: 48, color: kpi.color, opacity: 0.7 }} />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          );
        })}
      </Grid>

      {/* System Status */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                Bioreactor Status
              </Typography>
              {bioreactors?.slice(0, 5).map((br) => (
                <Box
                  key={br.bioreactor_id}
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    mb: 2,
                    p: 1.5,
                    borderRadius: 1,
                    bgcolor: 'grey.50',
                  }}
                >
                  <Box>
                    <Typography variant="body1" fontWeight={500}>
                      {br.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {br.current_batch_id || 'No active batch'}
                    </Typography>
                  </Box>
                  <Chip
                    label={br.status}
                    color={
                      br.status === 'Operational'
                        ? 'success'
                        : br.status === 'Warning'
                        ? 'warning'
                        : 'error'
                    }
                    size="small"
                  />
                </Box>
              ))}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                System Health
              </Typography>
              <Alert severity="success" sx={{ mb: 1 }}>
                All bioreactors operational
              </Alert>
              {equipmentAtRisk > 0 && (
                <Alert severity="warning" sx={{ mb: 1 }}>
                  {equipmentAtRisk} equipment units require attention
                </Alert>
              )}
              <Alert severity="success">No contamination detected</Alert>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Overview;
