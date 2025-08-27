import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

interface ConfusionMatrixChartProps {
  matrix: number[][];
  modelName: string;
  labels?: string[];
  title?: string;
}

const ConfusionMatrixChart: React.FC<ConfusionMatrixChartProps> = ({ 
  matrix, 
  modelName,
  labels = ['Negative', 'Neutral', 'Positive'],
  title 
}) => {
  const maxValue = Math.max(...matrix.flat());
  
  const getIntensity = (value: number) => {
    return value / maxValue;
  };

  const getBackgroundColor = (value: number) => {
    const intensity = getIntensity(value);
    return `rgba(54, 162, 235, ${0.1 + intensity * 0.8})`;
  };

  const getTextColor = (value: number) => {
    const intensity = getIntensity(value);
    return intensity > 0.5 ? '#ffffff' : '#000000';
  };

  const displayTitle = title || `Confusion Matrix - ${modelName}`;

  return (
    <Box sx={{ width: '100%', textAlign: 'center' }}>
      <Typography variant="h6" gutterBottom>
        {displayTitle}
      </Typography>
      
      <Paper elevation={2} sx={{ p: 2, display: 'inline-block' }}>
        <Box sx={{ mb: 1 }}>
          <Typography variant="body2" color="text.secondary">
            Predicted Label
          </Typography>
        </Box>
        
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Box sx={{ 
            writingMode: 'vertical-rl', 
            textOrientation: 'mixed',
            mr: 1,
            display: 'flex',
            alignItems: 'center',
            height: '200px'
          }}>
            <Typography variant="body2" color="text.secondary">
              True Label
            </Typography>
          </Box>
          
          <Box>
            {/* Header row with predicted labels */}
            <Box sx={{ display: 'flex', mb: 1 }}>
              <Box sx={{ width: 60 }}></Box>
              {labels.map((label, index) => (
                <Box 
                  key={index}
                  sx={{ 
                    width: 60, 
                    textAlign: 'center',
                    fontSize: '0.75rem',
                    fontWeight: 'bold'
                  }}
                >
                  {label}
                </Box>
              ))}
            </Box>
            
            {/* Matrix rows */}
            {matrix.map((row, rowIndex) => (
              <Box key={rowIndex} sx={{ display: 'flex', alignItems: 'center' }}>
                <Box sx={{ 
                  width: 60, 
                  textAlign: 'center',
                  fontSize: '0.75rem',
                  fontWeight: 'bold',
                  pr: 1
                }}>
                  {labels[rowIndex]}
                </Box>
                {row.map((value, colIndex) => (
                  <Box
                    key={colIndex}
                    sx={{
                      width: 60,
                      height: 60,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      backgroundColor: getBackgroundColor(value),
                      color: getTextColor(value),
                      border: '1px solid #e0e0e0',
                      fontWeight: 'bold',
                      fontSize: '0.875rem'
                    }}
                  >
                    {value}
                  </Box>
                ))}
              </Box>
            ))}
          </Box>
        </Box>
        
        <Box sx={{ mt: 2, fontSize: '0.75rem', color: 'text.secondary' }}>
          <Typography variant="caption">
            Darker colors indicate higher values
          </Typography>
        </Box>
      </Paper>
    </Box>
  );
};

export default ConfusionMatrixChart;
