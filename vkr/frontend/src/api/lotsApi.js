import apiClient from './axios';

export default {
  // Получение списка всех лотов
  getLots(params = {}) {
    return apiClient.get('/v1/lots/', { params });
  },
  
  // Получение списка лотов по аукциону
  getLotsByAuction(auctionId) {
    console.log(`API: Запрос лотов для аукциона с ID ${auctionId}`);
    return apiClient.get(`/v1/lots/auction/${auctionId}/`);
  },
  
  // Получение данных конкретного лота по ID
  getLotById(id) {
    return apiClient.get(`/v1/lots/${id}/`);
  },
  
  // Создание нового лота
  createLot(lotData) {
    console.log('API: Создание лота с данными:', lotData);
    return apiClient.post('/v1/lots/', lotData);
  },
  
  // Обновление лота
  updateLot(id, lotData) {
    return apiClient.put(`/v1/lots/${id}/update/`, lotData);
  },
  
  // Удаление лота
  deleteLot(id) {
    return apiClient.delete(`/v1/lots/${id}/delete/`);
  },
  
  // Загрузка изображения для лота
  uploadImage(lotId, imageFile) {
    const formData = new FormData();
    formData.append('lot', lotId);
    formData.append('image', imageFile);
    
    return apiClient.post('/lot-images/', formData);
  },
  
  // Удаление изображения лота
  deleteImage(imageId) {
    return apiClient.delete(`/lot-images/${imageId}/`);
  },
  
  // Получение списка категорий
  getCategories() {
    return apiClient.get('/v1/categories/');
  },
  
  // Одобрение лота благотворительной организацией
  approveLot(id) {
    console.log(`API: Одобрение лота с ID ${id}`);
    return apiClient.post(`/v1/lots/${id}/approve/`);
  },
  
  // Отклонение лота благотворительной организацией
  rejectLot(id) {
    console.log(`API: Отклонение лота с ID ${id}`);
    return apiClient.post(`/v1/lots/${id}/reject/`);
  }
};
