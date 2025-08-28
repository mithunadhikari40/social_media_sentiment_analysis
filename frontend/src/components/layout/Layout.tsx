import { Outlet } from 'react-router-dom';
import { Box, CssBaseline } from '@mui/material';
import AppBar from './AppBar';
import Drawer from './Drawer';
import { useState } from 'react';

const DRAWER_WIDTH = 240;

const Layout = () => {
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  return (
    <Box sx={{ display: 'flex' }}>
      <CssBaseline />
      <AppBar handleDrawerToggle={handleDrawerToggle} />
      <Drawer 
        mobileOpen={mobileOpen} 
        handleDrawerToggle={handleDrawerToggle}
        drawerWidth={DRAWER_WIDTH}
      />
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { xs: '100%', sm: `calc(100% - ${DRAWER_WIDTH}px)` },
          marginLeft: { xs: 0, sm: `${DRAWER_WIDTH}px` },
          marginTop: '64px', // Height of the AppBar
          minHeight: 'calc(100vh - 64px)',
          bgcolor: 'background.default',
        }}
      >
        <Box sx={{ width: '100%' }}>
          <Outlet />
        </Box>
      </Box>
    </Box>
  );
};

export default Layout;
