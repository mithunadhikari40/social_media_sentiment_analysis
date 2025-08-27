import { useState } from 'react';
import { useFormik } from 'formik';
import type { FormikHelpers } from 'formik';
import * as Yup from 'yup';
import { 
  Box, 
  Typography, 
  TextField, 
  Button, 
  Paper, 
  Avatar, 
  Divider, 
  CircularProgress, 
  Alert, 
  Grid 
} from '@mui/material';
import { useAuth } from '../../context/AuthContext';

interface ProfileFormValues {
  name: string;
  email: string;
  currentPassword: string;
  newPassword: string;
  confirmPassword: string;
}

const validationSchema = Yup.object({
  name: Yup.string().required('Name is required'),
  email: Yup.string().email('Enter a valid email').required('Email is required'),
  currentPassword: Yup.string(),
  newPassword: Yup.string().when('currentPassword', {
    is: (val: string) => !!val && val.length > 0,
    then: (schema) =>
      schema
        .min(8, 'Password must be at least 8 characters')
        .notOneOf(
          [Yup.ref('currentPassword')],
          'New password must be different from current password'
        ),
  }),
  confirmPassword: Yup.string().when('newPassword', {
    is: (val: string) => !!val && val.length > 0,
    then: (schema) =>
      schema
        .required('Please confirm your new password')
        .oneOf([Yup.ref('newPassword')], 'Passwords must match'),
  }),
});

const ProfilePage = () => {
  const { user, updateProfile } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');

  const initialValues: ProfileFormValues = {
    name: user?.name || '',
    email: user?.email || '',
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  };

  const handleSubmit = async (
    values: ProfileFormValues,
    { setSubmitting }: FormikHelpers<ProfileFormValues>
  ) => {
    try {
      setIsLoading(true);
      setError('');
      setSuccess('');

      const { currentPassword, newPassword, confirmPassword, ...profileData } = values;
      
      const updateData = currentPassword
        ? { ...profileData, currentPassword, newPassword }
        : profileData;

      await updateProfile(updateData);
      setSuccess('Profile updated successfully!');
      
      if (currentPassword) {
        formik.setFieldValue('currentPassword', '');
        formik.setFieldValue('newPassword', '');
        formik.setFieldValue('confirmPassword', '');
      }
    } catch (err) {
      console.error('Profile update error:', err);
      setError(err instanceof Error ? err.message : 'Failed to update profile');
    } finally {
      setIsLoading(false);
      setSubmitting(false);
    }
  };

  const formik = useFormik({
    initialValues,
    validationSchema,
    enableReinitialize: true,
    onSubmit: handleSubmit,
  });

  const getInitials = (name?: string) => {
    if (!name) return 'U';
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase();
  };

  return (
    <Box sx={{ p: 3, maxWidth: 1200, mx: 'auto' }}>
      <Box mb={4}>
        <Typography variant="h4" component="h1" gutterBottom>
          Profile Settings
        </Typography>
        <Typography variant="body1" color="textSecondary">
          Manage your account information and password
        </Typography>
      </Box>

      <Grid container spacing={4}>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, textAlign: 'center' }}>
            <Box display="flex" flexDirection="column" alignItems="center">
              <Avatar
                sx={{
                  width: 120,
                  height: 120,
                  fontSize: '3rem',
                  mb: 2,
                  bgcolor: 'primary.main',
                }}
              >
                {getInitials(user?.name)}
              </Avatar>
              <Typography variant="h6" component="div">
                {user?.name}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                {user?.email}
              </Typography>
              <Typography variant="caption" color="textSecondary" sx={{ mt: 1 }}>
                {user?.createdAt 
                  ? `Member since ${new Date(user.createdAt).toLocaleDateString()}` 
                  : 'N/A'}
              </Typography>
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <form onSubmit={formik.handleSubmit}>
              {success && (
                <Alert severity="success" sx={{ mb: 3 }}>
                  {success}
                </Alert>
              )}
              {error && (
                <Alert severity="error" sx={{ mb: 3 }}>
                  {error}
                </Alert>
              )}

              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    id="name"
                    name="name"
                    label="Full Name"
                    value={formik.values.name}
                    onChange={formik.handleChange}
                    onBlur={formik.handleBlur}
                    error={formik.touched.name && Boolean(formik.errors.name)}
                    helperText={formik.touched.name && formik.errors.name}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    id="email"
                    name="email"
                    label="Email"
                    type="email"
                    value={formik.values.email}
                    onChange={formik.handleChange}
                    onBlur={formik.handleBlur}
                    error={formik.touched.email && Boolean(formik.errors.email)}
                    helperText={formik.touched.email && formik.errors.email}
                  />
                </Grid>
              </Grid>

              <Divider sx={{ my: 3 }}>
                <Typography variant="subtitle2" color="textSecondary">
                  Change Password (leave blank to keep current password)
                </Typography>
              </Divider>

              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    id="currentPassword"
                    name="currentPassword"
                    label="Current Password"
                    type="password"
                    value={formik.values.currentPassword}
                    onChange={formik.handleChange}
                    onBlur={formik.handleBlur}
                    error={
                      formik.touched.currentPassword &&
                      Boolean(formik.errors.currentPassword)
                    }
                    helperText={
                      formik.touched.currentPassword && formik.errors.currentPassword
                    }
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    id="newPassword"
                    name="newPassword"
                    label="New Password"
                    type="password"
                    value={formik.values.newPassword}
                    onChange={formik.handleChange}
                    onBlur={formik.handleBlur}
                    error={
                      formik.touched.newPassword &&
                      Boolean(formik.errors.newPassword)
                    }
                    helperText={
                      formik.touched.newPassword && formik.errors.newPassword
                    }
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    id="confirmPassword"
                    name="confirmPassword"
                    label="Confirm New Password"
                    type="password"
                    value={formik.values.confirmPassword}
                    onChange={formik.handleChange}
                    onBlur={formik.handleBlur}
                    error={
                      formik.touched.confirmPassword &&
                      Boolean(formik.errors.confirmPassword)
                    }
                    helperText={
                      formik.touched.confirmPassword && formik.errors.confirmPassword
                    }
                  />
                </Grid>
              </Grid>

              <Box mt={4} display="flex" justifyContent="flex-end">
                <Button
                  color="primary"
                  variant="contained"
                  type="submit"
                  disabled={isLoading || !formik.isValid || !formik.dirty}
                  startIcon={
                    isLoading ? <CircularProgress size={20} /> : null
                  }
                >
                  {isLoading ? 'Saving...' : 'Save Changes'}
                </Button>
              </Box>
            </form>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ProfilePage;
