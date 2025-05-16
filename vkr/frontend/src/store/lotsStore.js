import { defineStore } from 'pinia';
import lotsApi from '../api/lotsApi';

export const useLotsStore = defineStore('lots', {
  state: () => ({
    lots: [],
    currentLot: null,
    categories: [],
    loading: false,
    error: null,
    success: false
  }),
  
  getters: {
    // Проверка наличия лотов
    hasLots: (state) => state.lots.length > 0,
    
    // Фильтр активных лотов
    activeLots: (state) => {
      return state.lots.filter(lot => lot.status === 'active');
    },
    
    // Получение лотов по аукциону
    lotsByAuction: (state) => (auctionId) => {
      return state.lots.filter(lot => lot.auction === auctionId);
    }
  },
  
  actions: {
    // Получение списка всех лотов
    async fetchLots(params = {}) {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await lotsApi.getLots(params);
        this.lots = response.data;
        return response.data;
      } catch (error) {
        this.error = error.response?.data?.detail || 'Ошибка при загрузке лотов';
        console.error('Error fetching lots:', error);
        return null;
      } finally {
        this.loading = false;
      }
    },
    
    // Получение списка лотов по аукциону
    async fetchLotsByAuction(auctionId) {
      this.loading = true;
      this.error = null;
      
      try {
        console.log(`Store: запрос лотов для аукциона ${auctionId}`);
        
        if (!auctionId) {
          console.error('Store: не указан ID аукциона');
          this.error = 'Не указан ID аукциона';
          return [];
        }
        
        const response = await lotsApi.getLotsByAuction(auctionId);
        
        // Дополнительная проверка, что все лоты действительно принадлежат этому аукциону
        const filteredLots = response.data.filter(lot => lot.auction == auctionId);
        
        console.log(`Store: получено ${response.data.length} лотов, отфильтровано ${filteredLots.length} лотов`);
        
        this.lots = filteredLots;
        return filteredLots;
      } catch (error) {
        this.error = error.response?.data?.detail || 'Ошибка при загрузке лотов';
        console.error(`Error fetching lots for auction ID ${auctionId}:`, error);
        return null;
      } finally {
        this.loading = false;
      }
    },
    
    // Получение данных конкретного лота
    async fetchLotById(id) {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await lotsApi.getLotById(id);
        this.currentLot = response.data;
        return response.data;
      } catch (error) {
        this.error = error.response?.data?.detail || 'Ошибка при загрузке данных лота';
        console.error(`Error fetching lot with ID ${id}:`, error);
        return null;
      } finally {
        this.loading = false;
      }
    },
    
    // Создание нового лота
    async createLot(lotData) {
      this.loading = true;
      this.error = null;
      this.success = false;
      
      try {
        console.log('Creating lot with data:', lotData);
        const response = await lotsApi.createLot(lotData);
        this.success = true;
        return response.data;
      } catch (error) {
        this.error = error.response?.data?.detail || 'Ошибка при создании лота';
        console.error('Error creating lot:', error);
        return null;
      } finally {
        this.loading = false;
      }
    },
    
    // Загрузка изображения для лота
    async uploadImage(lotId, imageFile) {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await lotsApi.uploadImage(lotId, imageFile);
        return response.data;
      } catch (error) {
        this.error = error.response?.data?.detail || 'Ошибка при загрузке изображения';
        console.error('Error uploading image:', error);
        return null;
      } finally {
        this.loading = false;
      }
    },
    
    // Удаление изображения лота
    async deleteImage(imageId) {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await lotsApi.deleteImage(imageId);
        return response.data;
      } catch (error) {
        this.error = error.response?.data?.detail || 'Ошибка при удалении изображения';
        console.error('Error deleting image:', error);
        return null;
      } finally {
        this.loading = false;
      }
    },
    
    // Получение списка категорий
    async fetchCategories() {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await lotsApi.getCategories();
        this.categories = response.data;
        return response.data;
      } catch (error) {
        this.error = error.response?.data?.detail || 'Ошибка при загрузке категорий';
        console.error('Error fetching categories:', error);
        return null;
      } finally {
        this.loading = false;
      }
    },
    
    // Обновление лота
    async updateLot(id, lotData) {
      this.loading = true;
      this.error = null;
      this.success = false;
      
      try {
        const response = await lotsApi.updateLot(id, lotData);
        this.success = true;
        return response.data;
      } catch (error) {
        this.error = error.response?.data?.detail || 'Ошибка при обновлении лота';
        console.error(`Error updating lot with ID ${id}:`, error);
        return null;
      } finally {
        this.loading = false;
      }
    },
    
    // Удаление лота
    async deleteLot(id) {
      this.loading = true;
      this.error = null;
      this.success = false;
      
      try {
        await lotsApi.deleteLot(id);
        this.success = true;
        return true;
      } catch (error) {
        this.error = error.response?.data?.detail || 'Ошибка при удалении лота';
        console.error(`Error deleting lot with ID ${id}:`, error);
        return false;
      } finally {
        this.loading = false;
      }
    },
    
    // Одобрение лота благотворительной организацией
    async approveLot(id) {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await lotsApi.approveLot(id);
        
        // Обновляем текущий лот, если это он
        if (this.currentLot && this.currentLot.id === id) {
          this.currentLot = response.data;
        }
        
        // Обновляем лот в списке лотов, если он там есть
        const lotIndex = this.lots.findIndex(lot => lot.id === id);
        if (lotIndex !== -1) {
          this.lots[lotIndex] = response.data;
        }
        
        return response.data;
      } catch (error) {
        this.error = error.response?.data?.detail || 'Ошибка при одобрении лота';
        console.error(`Error approving lot with ID ${id}:`, error);
        throw error;
      } finally {
        this.loading = false;
      }
    },
    
    // Отклонение лота благотворительной организацией
    async rejectLot(id) {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await lotsApi.rejectLot(id);
        
        // Обновляем текущий лот, если это он
        if (this.currentLot && this.currentLot.id === id) {
          this.currentLot = response.data;
        }
        
        // Обновляем лот в списке лотов, если он там есть
        const lotIndex = this.lots.findIndex(lot => lot.id === id);
        if (lotIndex !== -1) {
          this.lots[lotIndex] = response.data;
        }
        
        return response.data;
      } catch (error) {
        this.error = error.response?.data?.detail || 'Ошибка при отклонении лота';
        console.error(`Error rejecting lot with ID ${id}:`, error);
        throw error;
      } finally {
        this.loading = false;
      }
    },
    
    // Сброс текущего лота
    clearCurrentLot() {
      this.currentLot = null;
    },
    
    // Сброс состояния успеха
    resetSuccess() {
      this.success = false;
    }
  }
}); 