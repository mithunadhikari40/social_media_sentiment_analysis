import React from 'react';
import { Line } from 'react-chartjs-2';
import { Box, Typography } from '@mui/material';
import './ChartRegistry';

interface TimeSeriesChartProps {
  data: Array<Record<string, any>>;
  title?: string;
}

const TimeSeriesChart: React.FC<TimeSeriesChartProps> = ({ 
  data, 
  title = "Sentiment Trends Over Time" 
}) => {
  const chartData = {
    labels: data.map(item => {
      // Format date for better display with year
      const date = new Date(item.date);
      return date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric',
        year: 'numeric'
      });
    }),
    datasets: [
      {
        label: 'Positive',
        data: data.map(item => item.positive),
        borderColor: '#4bc0c0',
        backgroundColor: 'rgba(75, 192, 192, 0.1)',
        fill: false,
        tension: 0.1,
      },
      {
        label: 'Negative',
        data: data.map(item => item.negative),
        borderColor: '#ff6384',
        backgroundColor: 'rgba(255, 99, 132, 0.1)',
        fill: false,
        tension: 0.1,
      },
      {
        label: 'Neutral',
        data: data.map(item => item.neutral),
        borderColor: '#36a2eb',
        backgroundColor: 'rgba(54, 162, 235, 0.1)',
        fill: false,
        tension: 0.1,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      tooltip: {
        mode: 'index' as const,
        intersect: false,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
    interaction: {
      mode: 'nearest' as const,
      axis: 'x' as const,
      intersect: false,
    },
  };

  return (
    <Box sx={{ height: 300, width: '100%' }}>
      <Typography variant="h6" gutterBottom align="center">
        {title}
      </Typography>
      <Line data={chartData} options={options} />
    </Box>
  );
};

export default TimeSeriesChart;
