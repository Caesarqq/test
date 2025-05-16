import apiClient from './axios';

export default {
  // Получение всех ставок текущего пользователя
  getUserBids() {
    return apiClient.get('/bids/my_bids/');
  },
  
  // Получение ставок для конкретного лота
  getLotBids(lotId) {
    return apiClient.get(`/bids/by_lot/?lot_id=${lotId}`);
  },
  
  // Создание новой ставки
  createBid(lotId, amount) {
    return apiClient.post('/bids/', {
      lot: lotId,
      amount
    });
  },
  
  // Получение выигрышей пользователя (транзакции со статусом 'completed')
  getUserWinnings() {
    return apiClient.get('/transactions/my_purchases/');
  },
  
  // Получение транзакции по ID
  getTransactionById(transactionId) {
    return apiClient.get(`/transactions/${transactionId}/`);
  },
  
  // Оплата выигранного лота
  payForWinning(bidId, paymentMethod) {
    console.log(`API call: payForWinning with bidId=${bidId}, method=${paymentMethod}`);
    
    if (!bidId) {
      return Promise.reject(new Error('Не указан ID ставки для оплаты'));
    }
    
    // Добавляем параметр для предотвращения кэширования и отслеживания запроса
    const timestamp = new Date().getTime();
    
    // Используем правильный URL для API
    return apiClient.post(`/bids/${bidId}/pay/`, {
      payment_method: paymentMethod,
      timestamp: timestamp
    }, {
      // Добавляем дополнительные заголовки для отладки
      headers: {
        'X-Debug-Info': 'Payment request from frontend',
        'Cache-Control': 'no-cache, no-store, must-revalidate'
      }
    });
  },
  
  // Сохранение данных доставки
  saveDeliveryDetails(transactionId, deliveryData) {
    return apiClient.post(`/delivery/`, {
      transaction: transactionId,
      ...deliveryData
    });
  },
  
  // Подтверждение получения лота
  confirmDelivery(bidId) {
    return apiClient.post(`/bids/${bidId}/confirm-delivery/`);
  },
  
  // Получение деталей доставки по транзакции
  getDeliveryDetails(transactionId) {
    return apiClient.get(`/delivery/${transactionId}/`);
  }
};
