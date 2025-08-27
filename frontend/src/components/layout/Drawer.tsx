import { 
  Drawer as MuiDrawer, 
  List, 
  ListItem, 
  ListItemButton,
  ListItemIcon, 
  ListItemText, 
  Toolbar, 
  Divider, 
  useTheme, 
  Typography 
} from '@mui/material';
import { Link as RouterLink, useLocation } from 'react-router-dom';
import {
  Dashboard as DashboardIcon,
  Assessment as AnalysisIcon,
  Description as ReportsIcon,
  Person as ProfileIcon,
} from '@mui/icons-material';

interface DrawerProps {
  mobileOpen: boolean;
  handleDrawerToggle: () => void;
  drawerWidth: number;
}

const menuItems = [
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/dashboard' },
  { text: 'New Analysis', icon: <AnalysisIcon />, path: '/analysis' },
  { text: 'Reports', icon: <ReportsIcon />, path: '/reports' },
  { text: 'Profile', icon: <ProfileIcon />, path: '/profile' },
];

const Drawer = ({ mobileOpen, handleDrawerToggle, drawerWidth }: DrawerProps) => {
  const theme = useTheme();
  const location = useLocation();

  const drawer = (
    <div>
      <Toolbar>
        <Typography 
          variant="h6" 
          component="div"
          sx={{ 
            whiteSpace: 'normal',
            lineHeight: 1.2,
            fontSize: '1.1rem',
            fontWeight: 600,
            padding: '8px 0'
          }}
        >
          Social Media Analysis
        </Typography>
      </Toolbar>
      <Divider />
      <List>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton 
              component={RouterLink}
              to={item.path}
              selected={location.pathname === item.path}
              sx={{
                '&.Mui-selected': {
                  backgroundColor: theme.palette.action.selected,
                  '&:hover': {
                    backgroundColor: theme.palette.action.hover,
                  },
                },
                '&.Mui-selected .MuiListItemIcon-root': {
                  color: theme.palette.primary.main,
                },
                '&.Mui-selected .MuiListItemText-primary': {
                  color: theme.palette.primary.main,
                  fontWeight: 500,
                },
              }}
            >
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </div>
  );

  return (
    <>
      <MuiDrawer
        variant="temporary"
        open={mobileOpen}
        onClose={handleDrawerToggle}
        ModalProps={{
          keepMounted: true, // Better open performance on mobile.
        }}
        sx={{
          display: { xs: 'block', sm: 'none' },
          '& .MuiDrawer-paper': {
            boxSizing: 'border-box',
            width: drawerWidth,
            backgroundColor: theme.palette.background.paper,
          },
        }}
      >
        {drawer}
      </MuiDrawer>
      <MuiDrawer
        variant="permanent"
        sx={{
          display: { xs: 'none', sm: 'block' },
          '& .MuiDrawer-paper': {
            boxSizing: 'border-box',
            width: drawerWidth,
            backgroundColor: theme.palette.background.paper,
            borderRight: 'none',
          },
        }}
        open
      >
        {drawer}
      </MuiDrawer>
    </>
  );
};

export default Drawer;
