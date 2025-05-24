import apiClient from './axios';

export default {
  // Регистрация пользователя
  register(userData) {
    return apiClient.post('/users/register/', userData);
  },
  
  // Авторизация и получение токена
  login(credentials) {
    // Уберите начальный "/api" - с ним получается дублирование
    return apiClient.post('/token/', credentials);
  },
  
  // Обновление токена
  refreshToken(refreshToken) {
    return apiClient.post('/token/refresh/', { refresh: refreshToken });
  },
  
  // Получение профиля пользователя
  getProfile() {
    return apiClient.get('/users/profile/');
  },
  
  // Получение данных благотворительной организации пользователя
  getUserCharity() {
    return apiClient.get('/users/me/charity/');
  },
  
  // Получение списка всех благотворительных организаций
  getCharities() {
    return apiClient.get('/charities/');
  },
  
  // Проверка токена верификации email
  verifyEmail(token) {
    return apiClient.get(`/users/verify-email/?token=${token}`);
  }
};
