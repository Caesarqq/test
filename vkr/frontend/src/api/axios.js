import axios from 'axios';
import { jwtDecode } from 'jwt-decode';

const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Accept': 'application/json'
  },
  timeout: 10000
});

const refreshClient = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
});

const isTokenExpired = (token) => {
  if (!token) return true;
  
  try {
    const decoded = jwtDecode(token);
    const currentTime = Date.now() / 1000;
    return decoded.exp < currentTime;
  } catch (error) {
    return true;
  }
};

const refreshAccessToken = async () => {
  try {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }
    
    const response = await refreshClient.post('/token/refresh/', {
      refresh: refreshToken
    });
    
    const { access } = response.data;
    localStorage.setItem('access_token', access);

    try {
      const { useAuthStore } = await import('../store/auth');
      const authStore = useAuthStore();
      authStore.updateTokens(access);
    } catch (err) {
      console.warn('Unable to update auth store state', err);
    }
    
    return access;
  } catch (error) {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');

    try {
      const { useAuthStore } = await import('../store/auth');
      const authStore = useAuthStore();
      authStore.logout();
    } catch (err) {
      console.warn('Unable to update auth store state', err);
    }

    window.location.href = '/login';
    throw error;
  }
};

apiClient.interceptors.request.use(
  async config => {
    let accessToken = localStorage.getItem('access_token');

    if (accessToken && isTokenExpired(accessToken)) {
      try {
        accessToken = await refreshAccessToken();
      } catch (error) {
        return Promise.reject(error);
      }
    }

    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }
    
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

apiClient.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        await refreshAccessToken();

        originalRequest.headers.Authorization = `Bearer ${localStorage.getItem('access_token')}`;

        return apiClient(originalRequest);
      } catch (refreshError) {
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

export default apiClient;
