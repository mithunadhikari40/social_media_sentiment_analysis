import React from 'react';
import { Pie } from 'react-chartjs-2';
import { Box, Typography } from '@mui/material';
import type { SentimentData } from '../../api/analysis';
import './ChartRegistry';

interface SentimentPieChartProps {
  data: SentimentData[];
  title?: string;
}

const SentimentPieChart: React.FC<SentimentPieChartProps> = ({ 
  data, 
  title = "Sentiment Distribution" 
}) => {
  const chartData = {
    labels: data.map(item => item.sentiment.charAt(0).toUpperCase() + item.sentiment.slice(1)),
    datasets: [
      {
        data: data.map(item => item.count),
        backgroundColor: [
          '#ff6384', // negative - red
          '#36a2eb', // neutral - blue  
          '#4bc0c0', // positive - teal
        ],
        borderColor: [
          '#ff6384',
          '#36a2eb', 
          '#4bc0c0',
        ],
        borderWidth: 2,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom' as const,
        labels: {
          padding: 20,
          usePointStyle: true,
        },
      },
      tooltip: {
        callbacks: {
          label: (context: any) => {
            const item = data[context.dataIndex];
            return `${context.label}: ${item.count} (${item.percentage}%)`;
          },
        },
      },
    },
  };

  return (
    <Box sx={{ height: 300, width: '100%' }}>
      <Typography variant="h6" gutterBottom align="center">
        {title}
      </Typography>
      <Pie data={chartData} options={options} />
    </Box>
  );
};

export default SentimentPieChart;
