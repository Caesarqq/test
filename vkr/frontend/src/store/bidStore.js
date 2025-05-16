import { defineStore } from 'pinia';
import bidsApi from '../api/bidsApi';

export const useBidStore = defineStore('bid', {
  state: () => ({
    bids: [],
    winnings: [],
    loading: false,
    error: null,
    bidSuccess: false,
    bidMessage: '',
    paymentSuccess: false,
    deliverySuccess: false,
    confirmationSuccess: false
  }),
  
  getters: {
    // Сортированные ставки по дате (от новых к старым)
    sortedBids: (state) => {
      return [...state.bids].sort((a, b) => 
        new Date(b.created_at) - new Date(a.created_at)
      );
    },
    
    // Выигрышные ставки
    wonBids: (state) => {
      return state.bids.filter(bid => bid.is_winner);
    },
    
    // Ожидающие оплаты выигрыши
    pendingPaymentWinnings: (state) => {
      return state.winnings.filter(w => w.status === 'pending');
    },
    
    // Оплаченные выигрыши (ожидают подтверждения получения)
    pendingConfirmationWinnings: (state) => {
      return state.winnings.filter(w => w.status === 'completed' && w.delivery_status !== 'delivered');
    }
  },
  
  actions: {
    // Получить все ставки пользователя
    async fetchUserBids() {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await bidsApi.getUserBids();
        this.bids = response.data;
        return response.data;
      } catch (error) {
        this.error = error.response?.data?.detail || 'Ошибка при получении ставок';
        console.error('Error fetching user bids:', error);
        return null;
      } finally {
        this.loading = false;
      }
    },
    
    // Получить выигрыши пользователя
    async fetchUserWinnings() {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await bidsApi.getUserWinnings();
        this.winnings = response.data;
        return response.data;
      } catch (error) {
        this.error = error.response?.data?.detail || 'Ошибка при получении выигрышей';
        console.error('Error fetching user winnings:', error);
        return null;
      } finally {
        this.loading = false;
      }
    },
    
    // Создать новую ставку
    async createBid(lotId, amount) {
      this.loading = true;
      this.error = null;
      this.bidSuccess = false;
      this.bidMessage = '';
      
      try {
        const response = await bidsApi.createBid(lotId, amount);
        this.bidSuccess = true;
        this.bidMessage = 'Ставка успешно создана!';
        
        // Обновляем список ставок
        await this.fetchUserBids();
        
        return response.data;
      } catch (error) {
        this.error = error.response?.data?.error || 'Ошибка при создании ставки';
        console.error('Error creating bid:', error);
        return null;
      } finally {
        this.loading = false;
      }
    },
    
    // Оплата выигрыша
    async payForWinning(bidId, paymentMethod) {
      this.loading = true;
      this.error = null;
      this.paymentSuccess = false;
      
      try {
        console.log(`Attempting to pay for winning bid ID=${bidId}, method=${paymentMethod}`);
        
        if (!bidId) {
          throw new Error('Не указан ID ставки для оплаты');
        }
        
        const response = await bidsApi.payForWinning(bidId, paymentMethod);
        console.log('Payment API response:', response);
        
        if (!response || !response.data) {
          throw new Error('Пустой ответ от сервера при оплате');
        }
        
        this.paymentSuccess = true;
        
        // Обновляем список выигрышей
        await this.fetchUserWinnings();
        
        return response.data;
      } catch (error) {
        console.error('Payment API error:', error);
        // Более детальный вывод ошибки
        if (error.response) {
          console.error('Error status:', error.response.status);
          console.error('Error data:', error.response.data);
          
          // Проверяем, является ли ошибка связанной с тем, что лот уже оплачен
          if (error.response.status === 400 && 
             (error.response.data.detail?.includes('уже оплачен') || 
              error.response.data.error?.includes('уже оплачен') ||
              JSON.stringify(error.response.data).includes('уже оплачен'))) {
            this.error = 'Этот лот уже был оплачен ранее';
          } else {
            this.error = error.response?.data?.detail || 
                        error.response?.data?.error || 
                        JSON.stringify(error.response.data) || 
                        'Ошибка при оплате выигрыша';
          }
        } else if (error.request) {
          console.error('Error request:', error.request);
          this.error = 'Нет ответа от сервера. Проверьте соединение с интернетом.';
        } else {
          console.error('Error message:', error.message);
          this.error = error.message || 'Неизвестная ошибка при оплате';
        }
        
        throw error;  // Пробрасываем ошибку дальше для обработки в компоненте
      } finally {
        this.loading = false;
      }
    },
    
    // Сохранение деталей доставки
    async saveDeliveryDetails(transactionId, deliveryData) {
      this.loading = true;
      this.error = null;
      this.deliverySuccess = false;
      
      try {
        const response = await bidsApi.saveDeliveryDetails(transactionId, deliveryData);
        this.deliverySuccess = true;
        
        // Обновляем список выигрышей
        await this.fetchUserWinnings();
        
        // Обновление выигрыша после оформления доставки
        this.updateWinningDeliveryStatus(transactionId, deliveryData);
        
        return response.data;
      } catch (error) {
        this.error = error.response?.data?.detail || 'Ошибка при сохранении данных доставки';
        console.error('Error saving delivery details:', error);
        return null;
      } finally {
        this.loading = false;
      }
    },
    
    // Подтверждение получения лота
    async confirmDelivery(bidId) {
      this.loading = true;
      this.error = null;
      this.confirmationSuccess = false;
      
      try {
        const response = await bidsApi.confirmDelivery(bidId);
        this.confirmationSuccess = true;
        
        // Обновляем список выигрышей
        await this.fetchUserWinnings();
        
        return response.data;
      } catch (error) {
        this.error = error.response?.data?.detail || 'Ошибка при подтверждении получения';
        console.error('Error confirming delivery:', error);
        return null;
      } finally {
        this.loading = false;
      }
    },
    
    // Получение деталей доставки
    async getDeliveryDetails(transactionId) {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await bidsApi.getDeliveryDetails(transactionId);
        return response.data;
      } catch (error) {
        this.error = error.response?.data?.detail || 'Ошибка при получении данных доставки';
        console.error('Error getting delivery details:', error);
        return null;
      } finally {
        this.loading = false;
      }
    },
    
    // Сбросить состояние успешного создания ставки
    resetBidState() {
      this.bidSuccess = false;
      this.bidMessage = '';
    },
    
    // Сбросить состояние оплаты
    resetPaymentState() {
      this.paymentSuccess = false;
    },
    
    // Сбросить состояние доставки
    resetDeliveryState() {
      this.deliverySuccess = false;
    },
    
    // Сбросить состояние подтверждения получения
    resetConfirmationState() {
      this.confirmationSuccess = false;
    },
    
    // Получить ставки по конкретному лоту
    async fetchLotBids(lotId) {
      this.loading = true;
      this.error = null;
      try {
        const response = await bidsApi.getLotBids(lotId);
        this.bids = response.data;
        return response.data;
      } catch (error) {
        this.error = error.response?.data?.detail || 'Ошибка при получении ставок';
        console.error('Error fetching lot bids:', error);
        return null;
      } finally {
        this.loading = false;
      }
    },
    
    // Получить транзакцию по ID
    async fetchTransactionById(transactionId) {
      this.loading = true;
      this.error = null;
      
      try {
        console.log(`Fetching transaction ID=${transactionId}`);
        const response = await bidsApi.getTransactionById(transactionId);
        return response.data;
      } catch (error) {
        this.error = error.response?.data?.detail || 'Ошибка при получении транзакции';
        console.error('Error fetching transaction:', error);
        return null;
      } finally {
        this.loading = false;
      }
    },
    
    // Обновление выигрыша после оформления доставки
    updateWinningDeliveryStatus(transactionId, deliveryData) {
      // Находим транзакцию в списке выигрышей и обновляем данные о доставке
      const winning = this.winnings.find(w => w.id === transactionId);
      
      if (winning) {
        console.log('Обновляем данные о доставке для транзакции:', transactionId);
        
        // Обновляем данные о доставке
        winning.delivery = {
          ...winning.delivery,
          ...deliveryData
        };
        
        // Добавляем флаг, что доставка оформлена
        winning.has_delivery = true;
        
        // Если статус доставки не задан, устанавливаем pending
        if (!winning.delivery_status) {
          winning.delivery_status = 'pending';
        }
        
        console.log('Обновленные данные транзакции:', winning);
      }
    }
  }
});
