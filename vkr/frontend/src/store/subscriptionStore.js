import { defineStore } from 'pinia';
import subscriptionApi from '../api/subsriptionApi';

export const useSubscriptionStore = defineStore('subscription', {
  state: () => ({
    hasSubscription: false,
    subscriptionEndDate: null,
    loading: false,
    error: null,
    success: false,
    subscriptionPrice: 500, // Цена подписки (руб./месяц)
  }),
  
  getters: {
    // Проверка, активна ли подписка
    isActive: (state) => state.hasSubscription && state.subscriptionEndDate && new Date(state.subscriptionEndDate) > new Date(),
    
    // Форматированная дата окончания подписки
    formattedEndDate: (state) => {
      if (!state.subscriptionEndDate) return '';
      
      const date = new Date(state.subscriptionEndDate);
      return new Intl.DateTimeFormat('ru-RU', {
        day: '2-digit',
        month: 'long',
        year: 'numeric'
      }).format(date);
    },
    
    // Расчет оставшихся дней подписки
    remainingDays: (state) => {
      if (!state.subscriptionEndDate) return 0;
      
      const now = new Date();
      const endDate = new Date(state.subscriptionEndDate);
      
      if (endDate <= now) return 0;
      
      const diffTime = Math.abs(endDate - now);
      return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    }
  },
  
  actions: {
    // Получение статуса подписки
    async fetchSubscriptionStatus() {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await subscriptionApi.getSubscriptionStatus();
        
        this.hasSubscription = response.data.has_subscription || false;
        this.subscriptionEndDate = response.data.end_date || null;
        
        return response.data;
      } catch (error) {
        this.error = error.response?.data?.detail || 'Не удалось получить информацию о подписке';
        console.error('Error fetching subscription status:', error);
        return null;
      } finally {
        this.loading = false;
      }
    },
    
    // Оформление подписки
    async createSubscription(paymentMethod) {
      this.loading = true;
      this.error = null;
      this.success = false;
      
      try {
        const response = await subscriptionApi.createSubscription(paymentMethod);
        
        this.hasSubscription = true;
        this.subscriptionEndDate = response.data.end_date;
        this.success = true;
        
        return response.data;
      } catch (error) {
        this.error = error.response?.data?.detail || 'Не удалось оформить подписку';
        console.error('Error creating subscription:', error);
        return null;
      } finally {
        this.loading = false;
      }
    },
    
    // Отмена подписки
    async cancelSubscription() {
      this.loading = true;
      this.error = null;
      
      try {
        await subscriptionApi.cancelSubscription();
        
        this.hasSubscription = false;
        this.subscriptionEndDate = null;
        
        return true;
      } catch (error) {
        this.error = error.response?.data?.detail || 'Не удалось отменить подписку';
        console.error('Error canceling subscription:', error);
        return false;
      } finally {
        this.loading = false;
      }
    },
    
    // Сброс состояния успеха
    resetSuccessState() {
      this.success = false;
    }
  }
});