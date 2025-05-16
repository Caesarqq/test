import apiClient from './axios';

export default {
  // Получение списка всех аукционов
  getAuctions() {
    return apiClient.get('/v1/auctions/');
  },
  
  // Получение данных конкретного аукциона по ID
  getAuctionById(id) {
    return apiClient.get(`/v1/auctions/${id}/`);
  },
  
  // Получение событий аукциона
  getAuctionEvents(auctionId) {
    return apiClient.get(`/auction-events/?auction=${auctionId}`);
  },
  
  // Получение списка благотворительных организаций
  getCharities() {
    return apiClient.get('/charities/');
  },
  
  // Создание нового аукциона
  createAuction(auctionData) {
    // Используем FormData для отправки файлов
    const config = {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    };
    
    // Выводим отладочную информацию
    console.log('[API] Отправка запроса на создание аукциона:', {
      endpoint: '/v1/auctions/create/',
      headers: config.headers,
      isFormData: auctionData instanceof FormData
    });
    
    // Если это FormData, выведем содержимое
    if (auctionData instanceof FormData) {
      for (let [key, value] of auctionData.entries()) {
        if (key === 'image') {
          console.log(`[API] FormData содержит ${key}: [Файл]`);
        } else {
          console.log(`[API] FormData содержит ${key}: ${value}`);
        }
      }
    }
    
    // Правильный URL для создания аукциона
    return apiClient.post('/v1/auctions/create/', auctionData, config);
  },
  
  // Обновление аукциона
  updateAuction(id, auctionData) {
    // Если есть файл, используем FormData
    const config = {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    };
    return apiClient.put(`/v1/auctions/${id}/update/`, auctionData, config);
  },

  // Удаление аукциона
  deleteAuction(id) {
    return apiClient.delete(`/v1/auctions/${id}/delete/`);
  }
};
