import React, { useEffect, useRef } from 'react';
import { Box, Typography } from '@mui/material';
import WordCloud from 'wordcloud';

interface WordCloudChartProps {
  words: string[];
  sentiment: string;
  title?: string;
}

const WordCloudChart: React.FC<WordCloudChartProps> = ({ 
  words, 
  sentiment, 
  title 
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (!canvasRef.current || !words.length) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Create word frequency map (simple approach - all words equal weight)
    const wordList = words.slice(0, 50).map((word, index) => {
      // Assign decreasing weights to create visual hierarchy
      const weight = Math.max(10, 50 - index);
      return [word, weight] as [string, number];
    });

    // Color scheme based on sentiment
    const getColor = () => {
      switch (sentiment) {
        case 'positive':
          return '#4bc0c0';
        case 'negative':
          return '#ff6384';
        case 'neutral':
          return '#36a2eb';
        default:
          return '#666666';
      }
    };

    WordCloud(canvas, {
      list: wordList,
      gridSize: 8,
      weightFactor: 3,
      fontFamily: 'Arial, sans-serif',
      color: getColor,
      backgroundColor: 'transparent',
      rotateRatio: 0.3,
      rotationSteps: 2,
      minSize: 8,
      drawOutOfBound: false,
    });
  }, [words, sentiment]);

  const displayTitle = title || `${sentiment.charAt(0).toUpperCase() + sentiment.slice(1)} Words`;

  return (
    <Box sx={{ height: 300, width: '100%', textAlign: 'center' }}>
      <Typography variant="h6" gutterBottom>
        {displayTitle}
      </Typography>
      <canvas
        ref={canvasRef}
        width={400}
        height={250}
        style={{ 
          maxWidth: '100%', 
          height: 'auto',
          border: '1px solid #e0e0e0',
          borderRadius: '8px'
        }}
      />
    </Box>
  );
};

export default WordCloudChart;
