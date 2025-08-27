import React from 'react';
import { Bar } from 'react-chartjs-2';
import { Box, Typography } from '@mui/material';
import './ChartRegistry';

interface ModelComparisonChartProps {
  data: Record<string, number>;
  title?: string;
}

const ModelComparisonChart: React.FC<ModelComparisonChartProps> = ({ 
  data, 
  title = "Model Accuracy Comparison" 
}) => {
  const chartData = {
    labels: Object.keys(data),
    datasets: [
      {
        label: 'Accuracy',
        data: Object.values(data),
        backgroundColor: ['#ff6384', '#36a2eb', '#4bc0c0'],
        borderColor: ['#ff6384', '#36a2eb', '#4bc0c0'],
        borderWidth: 2,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        callbacks: {
          label: (context: any) => {
            return `Accuracy: ${(context.parsed.y * 100).toFixed(1)}%`;
          },
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 1.1,
        ticks: {
          callback: (value: any) => `${(value * 100).toFixed(0)}%`,
        },
      },
    },
  };

  return (
    <Box sx={{ height: 300, width: '100%' }}>
      <Typography variant="h6" gutterBottom align="center">
        {title}
      </Typography>
      <Bar data={chartData} options={options} />
    </Box>
  );
};

export default ModelComparisonChart;
