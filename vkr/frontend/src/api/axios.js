import axios from 'axios';
import { jwtDecode } from 'jwt-decode';

// Создаем экземпляр axios с базовым URL
const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Accept': 'application/json'
  },
  // Добавляем таймаут для запросов
  timeout: 10000 // 10 секунд
});

// Создаем второй экземпляр axios для запросов обновления токена,
// чтобы избежать бесконечного цикла в перехватчиках
const refreshClient = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
});

// Функция для проверки срока действия токена
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

// Функция для обновления токена
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
    
    // Попытка получить хранилище auth для обновления состояния
    // Так как это может быть вызвано до инициализации Vue/Pinia,
    // оборачиваем в try/catch
    try {
      const { useAuthStore } = await import('../store/auth');
      const authStore = useAuthStore();
      authStore.updateTokens(access);
    } catch (err) {
      console.warn('Unable to update auth store state', err);
    }
    
    return access;
  } catch (error) {
    // Если не удалось обновить токен, очищаем localStorage
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    
    // Попытка получить хранилище auth для обновления состояния
    try {
      const { useAuthStore } = await import('../store/auth');
      const authStore = useAuthStore();
      authStore.logout();
    } catch (err) {
      console.warn('Unable to update auth store state', err);
    }
    
    // Перенаправляем на страницу входа
    window.location.href = '/login';
    throw error;
  }
};

// Добавляем перехватчик запросов для добавления токена авторизации
apiClient.interceptors.request.use(
  async config => {
    let accessToken = localStorage.getItem('access_token');
    
    // Если токен отсутствует или истек срок его действия, пытаемся обновить
    if (accessToken && isTokenExpired(accessToken)) {
      try {
        accessToken = await refreshAccessToken();
      } catch (error) {
        // Ошибка обработана в refreshAccessToken
        return Promise.reject(error);
      }
    }
    
    // Добавляем токен в заголовок, если он есть
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }
    
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// Добавляем перехватчик ответов для обработки ошибок 401 (Unauthorized)
apiClient.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config;
    
    // Если ошибка 401 и это не повторный запрос после обновления токена
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // Обновляем токен и повторяем запрос
        await refreshAccessToken();
        
        // Обновляем токен в заголовке запроса
        originalRequest.headers.Authorization = `Bearer ${localStorage.getItem('access_token')}`;
        
        // Повторяем исходный запрос с новым токеном
        return apiClient(originalRequest);
      } catch (refreshError) {
        // Ошибка обработана в refreshAccessToken
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

export default apiClient;
