import apiClient from './axios';

export default {
  // Получение информации о подписке пользователя
  getSubscriptionStatus() {
    return apiClient.get('/users/subscription/');
  },
  
  // Оформление подписки
  createSubscription(paymentMethod) {
    return apiClient.post('/users/subscription/', { payment_method: paymentMethod });
  },
  
  // Отмена подписки
  cancelSubscription() {
    return apiClient.delete('/users/subscription/');
  }
};