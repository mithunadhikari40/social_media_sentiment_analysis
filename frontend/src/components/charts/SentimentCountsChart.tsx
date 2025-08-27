import React from 'react';
import { Bar } from 'react-chartjs-2';
import { Box, Typography } from '@mui/material';
import type { SentimentData } from '../../api/analysis';
import './ChartRegistry';

interface SentimentCountsChartProps {
  data: Record<string, SentimentData[]>;
  title?: string;
}

const SentimentCountsChart: React.FC<SentimentCountsChartProps> = ({ 
  data, 
  title = "Sentiment Count by Model" 
}) => {
  const sentiments = ['negative', 'neutral', 'positive'];
  const models = Object.keys(data);
  
  const chartData = {
    labels: sentiments.map(s => s.charAt(0).toUpperCase() + s.slice(1)),
    datasets: models.map((model, index) => {
      const colors = ['#ff6384', '#36a2eb', '#4bc0c0'];
      const modelData = data[model];
      
      return {
        label: model,
        data: sentiments.map(sentiment => {
          const item = modelData.find(d => d.sentiment === sentiment);
          return item ? item.count : 0;
        }),
        backgroundColor: colors[index % colors.length],
        borderColor: colors[index % colors.length],
        borderWidth: 2,
      };
    }),
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      tooltip: {
        callbacks: {
          label: (context: any) => {
            const modelName = context.dataset.label;
            const sentiment = sentiments[context.dataIndex];
            const modelData = data[modelName];
            const item = modelData.find(d => d.sentiment === sentiment);
            return `${modelName}: ${context.parsed.y} (${item?.percentage || 0}%)`;
          },
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
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

export default SentimentCountsChart;
