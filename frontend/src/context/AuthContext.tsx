import { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import { jwtDecode } from 'jwt-decode';
import apiClient from '../api/client';

export interface User {
  id: string;
  email: string;
  name: string;
  createdAt?: string;
  updatedAt?: string;
}

interface UpdateProfileData {
  name?: string;
  email?: string;
  currentPassword?: string;
  newPassword?: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  updateProfile: (data: UpdateProfileData) => Promise<void>;
  isAuthenticated: boolean;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const verifyToken = async () => {
      const storedToken = localStorage.getItem('token');
      if (!storedToken) {
        setLoading(false);
        return;
      }

      try {
        const decoded: any = jwtDecode(storedToken);
        if (decoded.exp * 1000 < Date.now()) {
          throw new Error('Token expired');
        }
        
        // Set apiClient default headers
        apiClient.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`;
        
        // Fetch user data
        const response = await apiClient.get('/auth/me');
        setUser(response.data);
        setToken(storedToken);
      } catch (error) {
        console.error('Token verification failed:', error);
        localStorage.removeItem('token');
        delete apiClient.defaults.headers.common['Authorization'];
      } finally {
        setLoading(false);
      }
    };

    verifyToken();
  }, []);

  const login = async (email: string, password: string): Promise<void> => {
    console.log('Starting login process...');
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);
    
    try {
      console.log('Sending login request...');
      const response = await apiClient.post('/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        withCredentials: true
      });
      
      console.log('Login response received:', response.data);
      const { access_token: token } = response.data;
      
      if (token) {
        console.log('Token received, storing and fetching user data...');
        // Store the token
        localStorage.setItem('token', token);
        
        // Set the default authorization header
        apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        
        try {
          // Fetch user data using the token
          console.log('Fetching user data...');
          const userResponse = await apiClient.get('/auth/me');
          console.log('User data received:', userResponse.data);
          
          // Update the user state
          setUser(userResponse.data);
          setToken(token);
          console.log('Login successful, user state updated');
        } catch (error) {
          console.error('Failed to fetch user data:', error);
          throw new Error('Failed to fetch user data');
        }
      } else {
        console.error('No access token in response');
        throw new Error('No access token received');
      }
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  };

  const register = async (name: string, email: string, password: string): Promise<void> => {
    const registerData = {
      email,
      password,
      name
    };
    
    await apiClient.post('/auth/register', registerData, {
      headers: {
        'Content-Type': 'application/json',
      },
      withCredentials: true
    });
    
    // Login after successful registration
    await login(email, password);
  };

  const logout = () => {
    localStorage.removeItem('token');
    delete apiClient.defaults.headers.common['Authorization'];
    setUser(null);
    setToken(null);
  };

  const updateProfile = async (data: UpdateProfileData) => {
    try {
      const response = await apiClient.put('/auth/me', data);
      setUser(prev => ({
        ...prev!,
        ...response.data.user,
        updatedAt: new Date().toISOString()
      }));
      if (response.data.token) {
        const newToken = response.data.token;
        localStorage.setItem('token', newToken);
        apiClient.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
        setToken(newToken);
      }
    } catch (error) {
      console.error('Profile update failed:', error);
      throw error;
    }
  };

  const isAuthenticated = !!token && !!user;

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated,
        loading,
        login,
        register,
        logout,
        updateProfile
      }}
    >
      {!loading && children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
