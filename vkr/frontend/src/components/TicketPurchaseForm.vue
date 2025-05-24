<template>
  <div class="ticket-purchase-form">
    <div v-if="loading" class="ticket-loading">
      <div class="spinner"></div>
      <p>Обработка покупки...</p>
    </div>
    
    <div v-else-if="success" class="ticket-success">
      <i class="success-icon">✓</i>
      <h2>Билет приобретен!</h2>
      <p>Теперь у вас есть доступ к аукциону <strong>{{ auctionName }}</strong>.</p>
      <button @click="onClose" class="btn-primary">Продолжить</button>
    </div>
    
    <div v-else-if="error" class="ticket-error">
      <i class="error-icon">✗</i>
      <h2>Ошибка при покупке билета</h2>
      <p>{{ error }}</p>
      <button @click="onClose" class="btn-secondary">Закрыть</button>
      <button @click="resetError" class="btn-primary">Попробовать снова</button>
    </div>
    
    <div v-else class="ticket-form-content">
      <h2>Покупка билета на аукцион</h2>
      <p>{{ auctionName }}</p>
      
      <div class="ticket-price">
        <span class="price-label">Стоимость билета:</span>
        <span class="price-value">{{ ticketPrice }} руб.</span>
      </div>
      
      <div class="user-balance">
        <span class="balance-label">Ваш текущий баланс:</span>
        <span class="balance-value" :class="{ 'insufficient': userBalance < ticketPrice }">
          {{ userBalance }} руб.
        </span>
      </div>
      
      <div v-if="userBalance < ticketPrice" class="insufficient-balance">
        <p>Недостаточно средств на балансе. Пожалуйста, пополните баланс.</p>
        <button @click="goToBalance" class="btn-secondary">Пополнить баланс</button>
      </div>
      
      <div v-else class="purchase-actions">
        <p>После покупки билета вы получите доступ ко всем лотам этого аукциона.</p>
        <div class="form-actions">
          <button @click="onClose" class="btn-secondary">Отмена</button>
          <button @click="purchaseTicket" class="btn-primary">Купить билет</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../store/auth';
import apiClient from '../api/axios';
import auctionsApi from '../api/auctionsApi';
import { useTicketsStore } from '../store/ticketsStore';

export default {
  name: 'TicketPurchaseForm',
  
  props: {
    auctionId: {
      type: [Number, String],
      required: true
    },
    auctionName: {
      type: String,
      default: 'Аукцион'
    },
    ticketPrice: {
      type: [Number, String],
      required: true
    },
    onClose: {
      type: Function,
      default: () => {}
    },
    onSuccess: {
      type: Function,
      default: () => {}
    }
  },
  
  setup(props) {
    const router = useRouter();
    const authStore = useAuthStore();
    
    const loading = ref(false);
    const error = ref(null);
    const success = ref(false);
    const userBalance = ref(0);
    const ticketsStore = useTicketsStore();

    // Загрузка баланса пользователя
    const fetchUserBalance = async () => {
      try {
        const response = await apiClient.get('/users/balance/');
        if (response.data && response.data.amount !== undefined) {
          userBalance.value = parseFloat(response.data.amount);
        }
      } catch (err) {
        console.error('Ошибка при получении баланса:', err);
        error.value = 'Не удалось получить информацию о вашем балансе';
      }
    };
    
    onMounted(async () => {
      if (!authStore.isAuthenticated) {
        router.push('/login?redirect=' + encodeURIComponent(router.currentRoute.value.fullPath));
        return;
      }
      
      await fetchUserBalance();
    });
    
    // Покупка билета
    const purchaseTicket = async () => {
      loading.value = true;
      error.value = null;
      
      try {
        // Исправленный URL - убираем дублирование /api/
        const response = await apiClient.post('/v1/auctions/tickets/purchase/', {
          auction: props.auctionId
        });
        
        if (response.status === 201) {
          success.value = true;
          ticketsStore.addTicket(response.data);
          // Обновляем баланс пользователя
          await fetchUserBalance();
          // Вызываем callback в случае успеха
          props.onSuccess();
        }
      } catch (err) {
        console.error('Ошибка при покупке билета:', err);
        
        if (err.response?.data?.error) {
          error.value = err.response.data.error;
        } else {
          error.value = 'Произошла ошибка при покупке билета';
        }
      } finally {
        loading.value = false;
      }
    };
    
    // Переход на страницу пополнения баланса
    const goToBalance = () => {
      router.push('/profile?tab=balance');
    };
    
    // Сброс ошибки
    const resetError = () => {
      error.value = null;
    };
    
    return {
      loading,
      error,
      success,
      userBalance,
      purchaseTicket,
      goToBalance,
      resetError
    };
  }
};
</script>

<style scoped>
.ticket-purchase-form {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  padding: 24px;
  max-width: 500px;
  width: 100%;
  margin: 0 auto;
}

h2 {
  margin-top: 0;
  margin-bottom: 16px;
  font-size: 24px;
  text-align: center;
}

.ticket-loading,
.ticket-success,
.ticket-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 24px;
  text-align: center;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  border-top-color: #3498db;
  animation: spin 1s ease-in-out infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.success-icon,
.error-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.success-icon {
  color: #27ae60;
}

.error-icon {
  color: #e74c3c;
}

.ticket-price,
.user-balance {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
  padding: 8px 0;
  border-bottom: 1px solid #eee;
}

.price-value,
.balance-value {
  font-weight: bold;
}

.insufficient {
  color: #e74c3c;
}

.insufficient-balance {
  padding: 12px;
  background-color: #fef2f2;
  border: 1px solid #fadcdc;
  border-radius: 4px;
  margin-bottom: 16px;
}

.purchase-actions {
  margin-top: 24px;
}

.form-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 16px;
}

.btn-primary,
.btn-secondary {
  padding: 10px 20px;
  border-radius: 4px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: background-color 0.2s;
}

.btn-primary {
  background-color: #3498db;
  color: white;
}

.btn-primary:hover {
  background-color: #2980b9;
}

.btn-secondary {
  background-color: #ecf0f1;
  color: #34495e;
}

.btn-secondary:hover {
  background-color: #bdc3c7;
}
</style>