import apiClient from './axios';

export default {
  // Получение текущего баланса пользователя
  getBalance() {
    return apiClient.get('/users/balance/');
  },
  
  // Пополнение баланса
  topUp(amount) {
    return apiClient.post('/users/balance/top-up/', { amount });
  },
  
  // История операций с балансом
  getHistory() {
    return apiClient.get('/users/balance/history/');
  }
}; 