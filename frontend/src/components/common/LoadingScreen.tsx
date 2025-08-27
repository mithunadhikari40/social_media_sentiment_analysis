import { Box, Typography, Avatar, Fade, Grow, keyframes } from '@mui/material';
import { Assessment, TrendingUp, Psychology, Analytics } from '@mui/icons-material';
import { useState, useEffect } from 'react';

// Keyframe animations
const pulse = keyframes`
  0% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.7;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
`;

const float = keyframes`
  0% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-10px);
  }
  100% {
    transform: translateY(0px);
  }
`;

const rotate = keyframes`
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
`;

const LoadingScreen = () => {
  const [currentMessage, setCurrentMessage] = useState(0);
  const [showIcons, setShowIcons] = useState(false);

  const messages = [
    "Analyzing social media sentiment...",
    "Processing data insights...",
    "Generating analytics reports...",
    "Preparing your dashboard..."
  ];

  const icons = [
    { icon: <Assessment />, color: '#1976d2', delay: 0 },
    { icon: <TrendingUp />, color: '#2e7d32', delay: 200 },
    { icon: <Psychology />, color: '#ed6c02', delay: 400 },
    { icon: <Analytics />, color: '#9c27b0', delay: 600 },
  ];

  useEffect(() => {
    const messageInterval = setInterval(() => {
      setCurrentMessage((prev) => (prev + 1) % messages.length);
    }, 1500);

    const iconTimeout = setTimeout(() => {
      setShowIcons(true);
    }, 500);

    return () => {
      clearInterval(messageInterval);
      clearTimeout(iconTimeout);
    };
  }, [messages.length]);

  return (
    <Box
      display="flex"
      flexDirection="column"
      justifyContent="center"
      alignItems="center"
      minHeight="100vh"
      sx={{
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* Background animated circles */}
      <Box
        sx={{
          position: 'absolute',
          width: '200px',
          height: '200px',
          borderRadius: '50%',
          background: 'rgba(255, 255, 255, 0.1)',
          top: '10%',
          left: '10%',
          animation: `${float} 3s ease-in-out infinite`,
        }}
      />
      <Box
        sx={{
          position: 'absolute',
          width: '150px',
          height: '150px',
          borderRadius: '50%',
          background: 'rgba(255, 255, 255, 0.05)',
          bottom: '20%',
          right: '15%',
          animation: `${float} 4s ease-in-out infinite reverse`,
        }}
      />

      {/* Main content */}
      <Fade in timeout={1000}>
        <Box textAlign="center" sx={{ zIndex: 1 }}>
          {/* Logo/Brand */}
          <Box mb={4}>
            <Avatar
              sx={{
                width: 100,
                height: 100,
                mx: 'auto',
                mb: 2,
                background: 'linear-gradient(45deg, #FE6B8B 30%, #FF8E53 90%)',
                animation: `${pulse} 2s infinite`,
              }}
            >
              <Assessment sx={{ fontSize: 50 }} />
            </Avatar>
            <Typography
              variant="h3"
              component="h1"
              sx={{
                color: 'white',
                fontWeight: 'bold',
                textShadow: '2px 2px 4px rgba(0,0,0,0.3)',
                mb: 1,
              }}
            >
              SentimentScope
            </Typography>
            <Typography
              variant="h6"
              sx={{
                color: 'rgba(255, 255, 255, 0.9)',
                fontWeight: 300,
                letterSpacing: '0.5px',
              }}
            >
              Social Media Analysis Platform
            </Typography>
          </Box>

          {/* Animated icons */}
          {showIcons && (
            <Box display="flex" justifyContent="center" gap={3} mb={4}>
              {icons.map((item, index) => (
                <Grow
                  key={index}
                  in={showIcons}
                  timeout={1000}
                  style={{ transitionDelay: `${item.delay}ms` }}
                >
                  <Avatar
                    sx={{
                      bgcolor: item.color,
                      width: 56,
                      height: 56,
                      animation: `${float} 2s ease-in-out infinite`,
                      animationDelay: `${index * 0.2}s`,
                      boxShadow: `0 4px 20px ${item.color}40`,
                    }}
                  >
                    {item.icon}
                  </Avatar>
                </Grow>
              ))}
            </Box>
          )}

          {/* Loading spinner */}
          <Box
            sx={{
              width: 60,
              height: 60,
              border: '4px solid rgba(255, 255, 255, 0.3)',
              borderTop: '4px solid white',
              borderRadius: '50%',
              animation: `${rotate} 1s linear infinite`,
              mx: 'auto',
              mb: 3,
            }}
          />

          {/* Dynamic loading message */}
          <Fade in key={currentMessage} timeout={500}>
            <Typography
              variant="h6"
              sx={{
                color: 'rgba(255, 255, 255, 0.9)',
                fontWeight: 400,
                minHeight: '32px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              {messages[currentMessage]}
            </Typography>
          </Fade>

          {/* Feature highlights */}
          <Box mt={4} sx={{ maxWidth: 600 }}>
            <Typography
              variant="body1"
              sx={{
                color: 'rgba(255, 255, 255, 0.8)',
                lineHeight: 1.6,
                px: 2,
              }}
            >
              Unlock powerful insights from social media data with advanced sentiment analysis, 
              trend detection, and comprehensive reporting tools.
            </Typography>
          </Box>

          {/* Progress dots */}
          <Box display="flex" justifyContent="center" gap={1} mt={3}>
            {[0, 1, 2, 3].map((index) => (
              <Box
                key={index}
                sx={{
                  width: 8,
                  height: 8,
                  borderRadius: '50%',
                  bgcolor: currentMessage === index ? 'white' : 'rgba(255, 255, 255, 0.4)',
                  transition: 'all 0.3s ease',
                  animation: currentMessage === index ? `${pulse} 1s infinite` : 'none',
                }}
              />
            ))}
          </Box>
        </Box>
      </Fade>
    </Box>
  );
};

export default LoadingScreen;
