import { defineStore } from 'pinia';
import auctionsApi from '../api/auctionsApi';

export const useAuctionsStore = defineStore('auctions', {
  state: () => ({
    auctions: [],
    currentAuction: null,
    auctionEvents: [],
    loading: false,
    error: null,
    $api: auctionsApi
  }),
  
  getters: {
    // Проверка наличия аукционов
    hasAuctions: (state) => state.auctions.length > 0,
    
    // Фильтр активных аукционов
    activeAuctions: (state) => {
      const now = new Date();
      return state.auctions.filter(auction => {
        const endDate = new Date(auction.end_date);
        return endDate > now;
      });
    }
  },
  
  actions: {
    // Получение списка всех аукционов
    async fetchAuctions() {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await this.$api.getAuctions();
        this.auctions = response.data;
        return response.data;
      } catch (error) {
        this.error = error.response?.data?.detail || 'Ошибка при загрузке аукционов';
        console.error('Error fetching auctions:', error);
        return null;
      } finally {
        this.loading = false;
      }
    },
    
    // Получение данных конкретного аукциона
    async fetchAuctionById(id) {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await this.$api.getAuctionById(id);
        this.currentAuction = response.data;
        return response.data;
      } catch (error) {
        this.error = error.response?.data?.detail || 'Ошибка при загрузке данных аукциона';
        console.error(`Error fetching auction with ID ${id}:`, error);
        return null;
      } finally {
        this.loading = false;
      }
    },
    
    // Получение событий аукциона
    async fetchAuctionEvents(auctionId) {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await this.$api.getAuctionEvents(auctionId);
        this.auctionEvents = response.data;
        return response.data;
      } catch (error) {
        this.error = error.response?.data?.detail || 'Ошибка при загрузке событий аукциона';
        console.error(`Error fetching auction events for auction ID ${auctionId}:`, error);
        return null;
      } finally {
        this.loading = false;
      }
    },
    
    // Создание нового аукциона
    async createAuction(formData) {
      this.loading = true;
      this.error = null;
      
      try {
        console.log('Store: отправка запроса на создание аукциона');
        const response = await this.$api.createAuction(formData);
        console.log('Store: ответ от API:', response.data);
        
        // Запрашиваем обновленный список аукционов сразу после создания
        await this.fetchAuctions();
        
        return response.data;
      } catch (error) {
        console.error('Store: ошибка при создании аукциона:', error);
        
        // Обработка различных ошибок от сервера
        if (error.response?.status === 400) {
          // Обработка ошибок валидации
          const errors = error.response.data;
          if (typeof errors === 'object' && errors !== null) {
            let errorMessage = '';
            for (const key in errors) {
              errorMessage += `${key}: ${errors[key].join(', ')}\n`;
            }
            this.error = errorMessage || 'Ошибка валидации формы';
          } else {
            this.error = errors?.detail || 'Ошибка при создании аукциона';
          }
        } else {
          this.error = error.response?.data?.detail || 'Ошибка при создании аукциона';
        }
        
        throw error; // Прокидываем ошибку дальше для обработки в компоненте
      } finally {
        this.loading = false;
      }
    },
    
    // Сброс текущего аукциона
    clearCurrentAuction() {
      this.currentAuction = null;
      this.auctionEvents = [];
    },
    
    // Обновление аукциона
    async updateAuction(id, formData) {
      this.loading = true;
      this.error = null;
      try {
        const response = await this.$api.updateAuction(id, formData);
        // Обновляем текущий аукцион и список аукционов
        await this.fetchAuctions();
        if (this.currentAuction && this.currentAuction.id === id) {
          this.currentAuction = response.data;
        }
        return response.data;
      } catch (error) {
        this.error = error.response?.data?.detail || 'Ошибка при обновлении аукциона';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    // Удаление аукциона
    async deleteAuction(id) {
      this.loading = true;
      this.error = null;
      try {
        await this.$api.deleteAuction(id);
        // Обновляем список аукционов
        await this.fetchAuctions();
        // Если текущий аукцион был удалён, сбрасываем его
        if (this.currentAuction && this.currentAuction.id === id) {
          this.clearCurrentAuction();
        }
        return true;
      } catch (error) {
        this.error = error.response?.data?.detail || 'Ошибка при удалении аукциона';
        throw error;
      } finally {
        this.loading = false;
      }
    }
  }
}); 