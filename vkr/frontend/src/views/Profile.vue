<template>
  <div class="profile-container">
    <h1>Личный кабинет</h1>
    
    <!-- Индикатор загрузки -->
    <loading-spinner v-if="authStore.loading" text="Загрузка данных профиля..." />
    
    <!-- Сообщение об ошибке -->
    <div v-if="error" class="error-message">
      {{ error }}
    </div>
    
    <!-- Данные пользователя -->
    <div v-if="authStore.user && !authStore.loading" class="profile-content">
      <div class="user-info">
        <div class="section">
          <h2>Основная информация</h2>
          
          <div class="info-row">
            <span class="label">Email:</span>
            <span class="value">{{ authStore.user.email }}</span>
            <span v-if="authStore.user.is_email_verified" class="badge verified">Подтвержден</span>
            <span v-else class="badge unverified">Не подтвержден</span>
          </div>
          
          <div class="info-row">
            <span class="label">Имя:</span>
            <span class="value">{{ authStore.user.first_name || 'Не указано' }}</span>
          </div>
          
          <div class="info-row">
            <span class="label">Фамилия:</span>
            <span class="value">{{ authStore.user.last_name || 'Не указана' }}</span>
          </div>
          
          <div class="info-row">
            <span class="label">Роль:</span>
            <span class="value">{{ getRoleName(authStore.user.role) }}</span>
          </div>
          
          <div class="info-row">
            <span class="label">Дата регистрации:</span>
            <span class="value">{{ formatDate(authStore.user.date_joined) }}</span>
          </div>
        </div>
         <!-- Блок подписки (только для покупателей) -->
<div class="section" v-if="authStore.user.role === 'buyer'">
  <h2>Премиум подписка</h2>
  
  <!-- Индикатор загрузки -->
  <loading-spinner v-if="subscriptionStore.loading" text="Загрузка информации о подписке..." />
  
  <!-- Сообщение об ошибке -->
  <div v-if="subscriptionStore.error" class="error-message-inline">
    {{ subscriptionStore.error }}
  </div>
  
  <!-- Активная подписка -->
  <div v-if="subscriptionStore.isActive" class="subscription-active">
    <div class="subscription-status">
      <div class="subscription-badge">Активна</div>
      <div class="subscription-info">
        <p>У вас активная премиум подписка до <strong>{{ subscriptionStore.formattedEndDate }}</strong></p>
        <p>Осталось дней: <strong>{{ subscriptionStore.remainingDays }}</strong></p>
      </div>
    </div>
    <div class="subscription-benefits">
      <h3>Преимущества вашей подписки:</h3>
      <ul>
        <li>Доступ ко всем платным аукционам без покупки билетов</li>
        <li>Неограниченное участие в течение всего срока подписки</li>
      </ul>
    </div>
    <button @click="cancelSubscription" class="cancel-subscription-btn" :disabled="subscriptionStore.loading">
      {{ subscriptionStore.loading ? 'Отмена подписки...' : 'Отменить автопродление' }}
    </button>
  </div>
  
  <!-- Нет подписки -->
  <div v-else-if="!subscriptionStore.loading" class="subscription-inactive">
    <div class="subscription-promo">
      <h3>Премиум доступ ко всем аукционам</h3>
      <div class="subscription-features">
        <div class="feature">
          <span class="feature-icon">✓</span>
          <span>Доступ ко всем платным аукционам без дополнительных платежей</span>
        </div>
        <div class="feature">
          <span class="feature-icon">✓</span>
          <span>Участвуйте в эксклюзивных аукционах для подписчиков</span>
        </div>
        <div class="feature">
          <span class="feature-icon">✓</span>
          <span>Автоматическое продление</span>
        </div>
      </div>
      <div class="subscription-pricing">
        <div class="price">{{ formatPrice(subscriptionStore.subscriptionPrice) }}/месяц</div>
        <button @click="showSubscribeModal" class="subscribe-btn">
          Оформить подписку
        </button>
      </div>
    </div>
  </div>
</div>
<subscription-modal
  v-if="showSubscriptionModal"
  :loading="subscriptionStore.loading"
  :error="subscriptionStore.error"
  :success="subscriptionStore.success"
  :balance-amount="balanceStore.balance"
  :subscription-price="subscriptionStore.subscriptionPrice"
  :subscription-end-date="subscriptionStore.subscriptionEndDate"
  @close="closeSubscriptionModal"
  @subscribe="handleSubscribe"
/>
        <!-- Блок баланса -->
        <div class="section" v-if="authStore.user.role === 'buyer'">
          <h2>Баланс</h2>
          
          <!-- Индикатор загрузки баланса -->
          <loading-spinner v-if="balanceStore.loading" text="Загрузка баланса..." />
          
          <!-- Сообщение об ошибке -->
          <div v-if="balanceStore.error" class="error-message-inline">
            {{ balanceStore.error }}
          </div>
          
          <!-- Информация о балансе -->
          <div v-if="!balanceStore.loading && balanceStore.hasBalance" class="balance-info">
            <div class="info-row">
              <span class="label">Ваш баланс:</span>
              <span class="value balance-value">{{ balanceStore.formattedBalance }}</span>
              <button @click="refreshBalance" class="refresh-btn" title="Обновить баланс">
                <span>↻</span>
              </button>
            </div>
            
            <button @click="showTopUpModal = true" class="top-up-btn">
              Пополнить баланс
            </button>
          </div>
          
          <!-- Модальное окно пополнения баланса -->
          <top-up-modal 
            v-if="showTopUpModal" 
            :initial-amount="topUpAmount"
            :loading="balanceStore.loading"
            :success="balanceStore.topUpSuccess"
            :error="balanceStore.error"
            @close="showTopUpModal = false"
            @submit="handleTopUp"
          />
        </div>
        
        <div class="section">
          <h2>Уведомления</h2>
          <div v-if="authStore.user.unread_notifications_count > 0" class="notification-info">
            У вас {{ authStore.user.unread_notifications_count }} непрочитанных уведомлений
          </div>
          <div v-else class="notification-info">
            У вас нет новых уведомлений
          </div>
        </div>
      </div>
    
      <!-- Блок ставок пользователя -->
      <div class="section bids-section" v-if="authStore.user.role === 'buyer'">
        <h2>Мои ставки</h2>
        
        <!-- Индикатор загрузки ставок -->
        <loading-spinner v-if="bidStore.loading" text="Загрузка ставок..." />
        
        <!-- Сообщение об ошибке -->
        <div v-if="bidStore.error" class="error-message-inline">
          {{ bidStore.error }}
        </div>
        
        <!-- Список ставок -->
        <div v-if="!bidStore.loading && bidStore.bids.length === 0" class="empty-list">
          У вас пока нет ставок
        </div>
        
        <div v-else-if="!bidStore.loading" class="bids-list">
          <bid-card 
            v-for="bid in bidStore.sortedBids" 
            :key="bid.id" 
            :bid="bid"
            :format-price="formatPrice"
            :format-date="formatDate"
            @place-bid="placeBid"
          />
        </div>
      </div>
      
      <!-- Блок выигрышей пользователя -->
      <div class="section winnings-section" v-if="authStore.user.role === 'buyer'">
        <h2>Мои выигрыши</h2>
        
        <!-- Индикатор загрузки выигрышей -->
        <loading-spinner v-if="bidStore.loading" text="Загрузка выигрышей..." />
        
        <!-- Сообщение об ошибке -->
        <div v-if="bidStore.error" class="error-message-inline">
          {{ bidStore.error }}
        </div>
        
        <!-- Пустое состояние -->
        <div v-if="!bidStore.loading && bidStore.winnings.length === 0" class="empty-list">
          У вас пока нет выигрышей
        </div>
        
        <!-- Список выигрышей -->
        <div v-else-if="!bidStore.loading && bidStore.winnings.length > 0" class="winnings-list">
          <winning-card 
            v-for="winning in bidStore.winnings" 
            :key="winning.id" 
            :winning="winning"
            :format-price="formatPrice"
            :format-date="formatDate"
            :loading="bidStore.loading"
            @view-details="viewWinningDetails"
            @pay="payForWinning"
            @setup-delivery="setupDelivery"
            @confirm-delivery="confirmDelivery"
          />
        </div>
        
        <!-- Модальное окно оформления доставки -->
        <delivery-form 
          v-if="showDeliveryForm"
          :transaction-id="selectedTransaction"
          :loading="bidStore.loading"
          :error="bidStore.error"
          :success="bidStore.deliverySuccess"
          @close="closeDeliveryForm"
          @submit="handleDeliverySubmit"
        />
      </div>
      
      <!-- Кнопка выхода -->
      <button @click="logout" class="logout-btn">Выйти из аккаунта</button>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../store/auth';
import { useBalanceStore } from '../store/balanceStore';
import { useBidStore } from '../store/bidStore';
import BidCard from '../components/BidCard.vue';
import WinningCard from '../components/WinningCard.vue';
import TopUpModal from '../components/TopUpModal.vue';
import LoadingSpinner from '../components/LoadingSpinner.vue';
import DeliveryForm from '../components/DeliveryForm.vue';
import { useSubscriptionStore } from '../store/subscriptionStore';
import SubscriptionModal from '../components/SubscriptionModal.vue';
export default {
  name: 'ProfileView',
  components: {
    BidCard,
    WinningCard,
    TopUpModal,
    LoadingSpinner,
    DeliveryForm,
    SubscriptionModal
  },
  setup() {
    const authStore = useAuthStore();
    const balanceStore = useBalanceStore();
    const bidStore = useBidStore();
    const subscriptionStore = useSubscriptionStore();
    const router = useRouter();
    const error = ref(null);
    
    // Состояние модального окна подписки
    const showSubscriptionModal = ref(false); 
    
    // Состояние модального окна пополнения баланса
    const showTopUpModal = ref(false);
    const topUpAmount = ref(100);
    
    // Состояние формы доставки
    const showDeliveryForm = ref(false);
    const selectedTransaction = ref(null);
    
    // Функция для форматирования даты
    const formatDate = (dateString) => {
      if (!dateString) return 'Нет данных';
      
      const date = new Date(dateString);
      return new Intl.DateTimeFormat('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      }).format(date);
    };
    
    // Функция для форматирования цены
    const formatPrice = (price) => {
      if (price === null || price === undefined) return 'Нет данных';
      return new Intl.NumberFormat('ru-RU', {
        style: 'currency',
        currency: 'RUB',
        minimumFractionDigits: 0
      }).format(price);
    };
    
    // Функция для показа модального окна подписки
    const showSubscribeModal = () => {
      showSubscriptionModal.value = true;
    };
    
    // Функция для закрытия модального окна подписки
    const closeSubscriptionModal = () => {
      // Если подписка была успешно оформлена, то сбрасываем флаг успеха
      if (subscriptionStore.success) {
        subscriptionStore.resetSuccessState();
      }
      showSubscriptionModal.value = false;
    };
    
    // Функция для оформления подписки
    const handleSubscribe = async (data) => {
      try {
        await subscriptionStore.createSubscription(data.paymentMethod);
        
        // Если подписка была успешно оформлена, то обновляем баланс пользователя
        if (subscriptionStore.success) {
          await balanceStore.fetchBalance();
          
          // Проверяем, есть ли редирект после подписки
          const redirectUrl = localStorage.getItem('redirect_after_subscription');
          
          // Закрываем модальное окно через 3 секунды и выполняем редирект, если нужно
          setTimeout(() => {
            showSubscriptionModal.value = false;
            subscriptionStore.resetSuccessState();
            
            if (redirectUrl) {
              localStorage.removeItem('redirect_after_subscription');
              router.push(redirectUrl);
            }
          }, 3000);
        }
      } catch (err) {
        console.error('Error creating subscription:', err);
      }
    };
    
    // Функция для отмены подписки
    const cancelSubscription = async () => {
      try {
        const confirmed = window.confirm('Вы уверены, что хотите отменить автопродление подписки? Вы сможете пользоваться подпиской до окончания оплаченного периода.');
        
        if (confirmed) {
          await subscriptionStore.cancelSubscription();
          
          if (!subscriptionStore.error) {
            alert('Автопродление подписки отменено. Вы сможете пользоваться подпиской до окончания оплаченного периода.');
          }
        }
      } catch (err) {
        console.error('Error canceling subscription:', err);
      }
    };
    
    // Функция для получения названия роли на русском
    const getRoleName = (role) => {
      const roles = {
        buyer: 'Покупатель',
        donor: 'Донор',
        charity: 'Благотворительная организация',
        admin: 'Администратор'
      };
      
      return roles[role] || role;
    };
    
    // Функция для получения класса статуса
    const getStatusClass = (status) => {
      const statusClasses = {
        'pending': 'pending',
        'completed': 'completed',
        'failed': 'failed',
        'shipped': 'shipped',
        'delivered': 'delivered'
      };
      
      return statusClasses[status] || 'default';
    };
    
    // Функция для получения названия статуса на русском
    const getStatusName = (status) => {
      const statuses = {
        'pending': 'В обработке',
        'completed': 'Завершен',
        'failed': 'Ошибка',
        'shipped': 'Отправлен',
        'delivered': 'Доставлен'
      };
      
      return statuses[status] || status;
    };
    
    // Функция для выхода из аккаунта
    const logout = () => {
      authStore.logout();
      router.push('/login');
    };
    
    // Функция для пополнения баланса
    const handleTopUp = async (amount) => {
      if (amount <= 0) return;
      
      const result = await balanceStore.topUpBalance(amount);
      
      if (result) {
        // Закрываем модальное окно через 2 секунды
        setTimeout(() => {
          showTopUpModal.value = false;
          balanceStore.resetTopUpSuccess();
        }, 2000);
      }
    };
    
    // Функция для размещения новой ставки
    const placeBid = (lotId) => {
      router.push({ name: 'lot', params: { id: lotId } });
    };
    
    // Функция для просмотра деталей выигрыша
    const viewWinningDetails = (winning) => {
      // Здесь может быть показано модальное окно с подробной информацией
      console.log('View winning details:', winning);
    };
    
    // Функция для оплаты выигрыша
    const payForWinning = async (winning) => {
      try {
        const result = await bidStore.payForWinning(winning.bid_id);
        
        if (result) {
          // Если оплата прошла успешно, показываем форму доставки
          selectedTransaction.value = result.id;
          showDeliveryForm.value = true;
        }
      } catch (err) {
        console.error('Error paying for winning:', err);
      }
    };
    
    // Функция для отображения формы доставки
    const setupDelivery = (winning) => {
      router.push({ name: 'delivery', params: { id: winning.id } });
    };
    
    // Функция для закрытия формы доставки
    const closeDeliveryForm = () => {
      if (bidStore.deliverySuccess) {
        // Если доставка успешно оформлена, обновляем список выигрышей
        bidStore.fetchUserWinnings();
        bidStore.resetDeliveryState();
      }
      
      showDeliveryForm.value = false;
      selectedTransaction.value = null;
    };
    
    // Функция для отправки формы доставки
    const handleDeliverySubmit = async (deliveryData) => {
      try {
        await bidStore.saveDeliveryDetails(selectedTransaction.value, deliveryData);
        
        // Задержка перед закрытием формы
        if (bidStore.deliverySuccess) {
          setTimeout(() => {
            showDeliveryForm.value = false;
            selectedTransaction.value = null;
            bidStore.resetDeliveryState();
            bidStore.fetchUserWinnings();
          }, 2000);
        }
      } catch (err) {
        console.error('Error submitting delivery form:', err);
      }
    };
    
    // Функция для подтверждения получения
    const confirmDelivery = async (winning) => {
      try {
        await bidStore.confirmDelivery(winning.bid_id);
        
        if (bidStore.confirmationSuccess) {
          // Обновляем данные
          bidStore.fetchUserWinnings();
          bidStore.resetConfirmationState();
        }
      } catch (err) {
        console.error('Error confirming delivery:', err);
      }
    };
    
    // Функция для загрузки данных профиля
    const loadProfile = async () => {
      // Если пользователь не авторизован, перенаправляем на страницу входа
      if (!authStore.isAuthenticated) {
        router.push('/login');
        return;
      }
      
      error.value = null;
      
      try {
        // Загружаем профиль пользователя
        await authStore.fetchUserProfile();
        
        // Если после запроса пользователь не загружен, значит была ошибка авторизации
        if (!authStore.user) {
          router.push('/login');
          return;
        }
        
        // Если пользователь - покупатель, загружаем баланс, ставки и статус подписки
        if (authStore.user.role === 'buyer') {
          try {
            await balanceStore.fetchBalance();
          } catch (err) {
            console.error('Error loading balance:', err);
            // Не прерываем выполнение, чтобы остальной интерфейс мог загрузиться
          }
          
          try {
            await subscriptionStore.fetchSubscriptionStatus();
          } catch (err) {
            console.error('Error loading subscription status:', err);
            // Не прерываем выполнение
          }
          
          try {
            await Promise.all([
              bidStore.fetchUserBids(),
              bidStore.fetchUserWinnings()
            ]);
          } catch (err) {
            console.error('Error loading bids or winnings:', err);
          }
          
          // Проверяем, есть ли запрос на показ модального окна подписки из URL
          if (router.currentRoute.value.query.showSubscription === 'true') {
            // Запускаем с небольшой задержкой, чтобы все данные успели загрузиться
            setTimeout(() => {
              showSubscribeModal();
            }, 500);
          }
        }
      } catch (err) {
        error.value = 'Не удалось загрузить данные профиля';
        console.error('Error loading profile:', err);
      }
    };
    
    // Функция для обновления баланса
    const refreshBalance = async () => {
      if (authStore.user?.role === 'buyer') {
        try {
          await balanceStore.fetchBalance();
        } catch (err) {
          console.error('Error refreshing balance:', err);
        }
      }
    };
    
    // Загружаем данные при монтировании компонента
    onMounted(loadProfile);
    
    return {
      authStore,
      balanceStore,
      bidStore,
      subscriptionStore,
      error,
      showTopUpModal,
      topUpAmount,
      showSubscriptionModal,
      showDeliveryForm,
      selectedTransaction,
      formatDate,
      formatPrice,
      getRoleName,
      getStatusClass,
      getStatusName,
      logout,
      handleTopUp,
      placeBid,
      viewWinningDetails,
      payForWinning,
      setupDelivery,
      closeDeliveryForm,
      handleDeliverySubmit,
      confirmDelivery,
      refreshBalance,
      showSubscribeModal,
      closeSubscriptionModal,
      handleSubscribe,
      cancelSubscription
    };
  }
}
</script>

<style scoped>
.profile-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 32px 24px;
}

h1 {
  margin-bottom: 24px;
  color: #333;
  text-align: center;
}

h2 {
  margin-bottom: 16px;
  color: #555;
  font-size: 1.2rem;
}

h3 {
  margin-bottom: 16px;
  color: #333;
  font-size: 1.1rem;
}

.error-message {
  text-align: center;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.error-message-inline {
  padding: 10px;
  border-radius: 6px;
  margin-bottom: 15px;
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.success-message {
  background-color: #d4edda;
  color: #155724;
  padding: 10px;
  border-radius: 6px;
  margin-bottom: 15px;
  text-align: center;
}

.profile-content {
  background-color: #fff;
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  padding: 24px;
}

.section {
  margin-bottom: 32px;
  border-bottom: 1px solid #eee;
  padding-bottom: 24px;
}

.section:last-of-type {
  border-bottom: none;
  padding-bottom: 0;
}

.info-row {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.label {
  font-weight: 500;
  color: #666;
  width: 160px;
  padding-right: 16px;
}

.value {
  color: #333;
  flex-grow: 1;
}

.balance-value {
  font-size: 1.2rem;
  font-weight: bold;
  color: #28a745;
}

.badge {
  font-size: 0.75rem;
  padding: 2px 8px;
  border-radius: 12px;
  margin-left: 8px;
}

.verified {
  background-color: #d4edda;
  color: #155724;
}

.unverified {
  background-color: #f8d7da;
  color: #721c24;
}

.top-up-btn {
  padding: 8px 16px;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 12px;
  font-size: 14px;
  transition: background-color 0.3s;
}

.top-up-btn:hover {
  background-color: #218838;
}

.notification-info {
  padding: 12px;
  background-color: #f8f9fa;
  border-radius: 6px;
}

.empty-list {
  padding: 16px;
  text-align: center;
  color: #6c757d;
  background-color: #f8f9fa;
  border-radius: 6px;
}

.bids-list, .winnings-list {
  margin-top: 16px;
}

.logout-btn {
  display: block;
  margin: 32px auto 0;
  padding: 10px 20px;
  background-color: #dc3545;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.3s;
}

.logout-btn:hover {
  background-color: #c82333;
}

.refresh-btn {
  background: none;
  border: none;
  cursor: pointer;
  margin-left: 8px;
  font-size: 20px;
  color: #007bff;
  transition: transform 0.2s;
}

.refresh-btn:hover {
  transform: rotate(180deg);
}
.subscription-active {
  padding: 16px;
  background-color: #f0f9ff;
  border-radius: 8px;
  border: 1px solid #b8daff;
  margin-bottom: 20px;
}

.subscription-status {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.subscription-badge {
  display: inline-block;
  background-color: #007bff;
  color: white;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: bold;
  margin-right: 16px;
}

.subscription-info {
  flex-grow: 1;
}

.subscription-info p {
  margin: 4px 0;
  color: #333;
}

.subscription-benefits {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e2e9f3;
}

.subscription-benefits h3 {
  font-size: 16px;
  margin-bottom: 12px;
  color: #333;
}

.subscription-benefits ul {
  padding-left: 24px;
  margin: 0;
}

.subscription-benefits li {
  margin-bottom: 8px;
  color: #444;
}

.cancel-subscription-btn {
  display: block;
  margin-top: 16px;
  padding: 8px 16px;
  background-color: #e9ecef;
  color: #495057;
  border: 1px solid #ced4da;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.cancel-subscription-btn:hover:not(:disabled) {
  background-color: #dee2e6;
}

.cancel-subscription-btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.subscription-inactive {
  border: 1px solid #e9ecef;
  border-radius: 8px;
  overflow: hidden;
}

.subscription-promo {
  padding: 20px;
  background-color: #f8f9fa;
}

.subscription-promo h3 {
  font-size: 18px;
  color: #333;
  margin-top: 0;
  margin-bottom: 16px;
  text-align: center;
}

.subscription-features {
  margin-bottom: 20px;
}

.subscription-features .feature {
  display: flex;
  align-items: flex-start;
  margin-bottom: 12px;
}

.subscription-features .feature-icon {
  color: #28a745;
  font-weight: bold;
  margin-right: 12px;
}

.subscription-pricing {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #dee2e6;
}

.subscription-pricing .price {
  font-size: 24px;
  font-weight: bold;
  color: #007bff;
}

.subscribe-btn {
  padding: 10px 20px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 15px;
  transition: background-color 0.3s;
}

.subscribe-btn:hover {
  background-color: #0069d9;
}

@media (max-width: 600px) {
  .subscription-pricing {
    flex-direction: column;
    gap: 12px;
  }
  
  .subscribe-btn {
    width: 100%;
  }
}
@media (max-width: 600px) {
  .profile-container {
    padding: 16px;
  }
  
  .info-row {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .label {
    width: 100%;
    margin-bottom: 4px;
  }
  
  .badge {
    margin-left: 0;
    margin-top: 4px;
  }
}
</style>
