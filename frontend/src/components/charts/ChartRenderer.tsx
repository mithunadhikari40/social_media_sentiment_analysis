import React from 'react';
import { Box, Stack, Paper } from '@mui/material';
import type { AnalysisResult } from '../../api/analysis';
import {
  SentimentPieChart,
  ModelComparisonChart,
  SentimentCountsChart,
  TimeSeriesChart,
  WordCloudChart,
  ConfusionMatrixChart
} from './index';

interface ChartRendererProps {
  analysis: AnalysisResult;
}

const ChartRenderer: React.FC<ChartRendererProps> = ({ analysis }) => {
  return (
    <Box sx={{ width: '100%' }}>
      <Stack spacing={3}>
        {/* Top Row - Pie Chart and Model Comparison */}
        <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
          <Box sx={{ flex: '1 1 300px', minWidth: 300 }}>
            <Paper elevation={2} sx={{ p: 2, height: 350 }}>
              <SentimentPieChart data={analysis.sentimentDistribution} />
            </Paper>
          </Box>
          <Box sx={{ flex: '1 1 300px', minWidth: 300 }}>
            <Paper elevation={2} sx={{ p: 2, height: 350 }}>
              <ModelComparisonChart data={analysis.modelComparison} />
            </Paper>
          </Box>
        </Box>

        {/* Sentiment Counts by Model */}
        <Paper elevation={2} sx={{ p: 2, height: 350 }}>
          <SentimentCountsChart data={analysis.sentimentCounts} />
        </Paper>

        {/* Time Series Chart */}
        <Paper elevation={2} sx={{ p: 2, height: 350 }}>
          <TimeSeriesChart data={analysis.timeSeriesData} />
        </Paper>

        {/* Word Clouds */}
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', justifyContent: 'center' }}>
          {Object.entries(analysis.wordCloudData).map(([sentiment, words]) => (
            <Box key={sentiment} sx={{ flex: '1 1 300px', minWidth: 300, maxWidth: 400 }}>
              <Paper elevation={2} sx={{ p: 2, height: 350 }}>
                <WordCloudChart 
                  words={words} 
                  sentiment={sentiment}
                />
              </Paper>
            </Box>
          ))}
        </Box>

        {/* Confusion Matrices */}
        <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap', justifyContent: 'center' }}>
          {Object.entries(analysis.confusionMatrices).map(([modelName, matrix]) => (
            <Box key={modelName} sx={{ flex: '1 1 300px', minWidth: 300 }}>
              <Paper elevation={2} sx={{ p: 2, display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 300 }}>
                <ConfusionMatrixChart 
                  matrix={matrix}
                  modelName={modelName}
                />
              </Paper>
            </Box>
          ))}
        </Box>
      </Stack>
    </Box>
  );
};

export default ChartRenderer;
