
<template>
  <div class="auction-detail-container">
    <!-- Индикатор загрузки -->
    <loading-spinner v-if="loading" text="Загрузка данных аукциона..." />
    
    <!-- Сообщение об ошибке -->
    <div v-if="error" class="error-message">
      {{ error }}
    </div>
    
    <!-- Модальное окно для покупки билета -->
    <div v-if="showTicketForm" class="modal-overlay" @click.self="closeTicketForm">
      <div class="modal-content">
        <ticket-purchase-form
          :auction-id="auctionId"
          :auction-name="auction.title || auction.name"
          :ticket-price="auction.ticket_price"
          :on-close="closeTicketForm"
          :on-success="handleTicketPurchased"
        />
      </div>
    </div>
    
    <div v-if="!loading && auction" class="auction-content">
      <!-- Хлебные крошки -->
      <div class="breadcrumbs">
        <router-link :to="{ name: 'auctions' }">Аукционы</router-link>
        <span>/</span>
        <span>{{ auction.title }}</span>
      </div>
      
      <!-- Шапка аукциона -->
      <div class="auction-header">
        <div class="auction-image-container">
          <img 
            v-if="auction.image" 
            :src="auction.image" 
            :alt="auction.title" 
            class="auction-image"
          />
          <div v-else class="no-image">
            Нет изображения
          </div>
        </div>
        
        <div class="auction-info">
          <h1 class="auction-title">{{ auction.title }}</h1>
          
          <!-- Платный аукцион -->
          <div v-if="auction.is_paid" class="auction-paid-badge">
            <span class="paid-icon">🎟️</span>
            <span class="paid-text">Платный аукцион</span>
            <span class="ticket-price">{{ formatPrice(auction.ticket_price) }}</span>
            
            <!-- Значок подписки -->
            <span v-if="hasSubscription" class="subscription-badge">
              <span class="subscription-icon">✓</span>
              <span class="subscription-text">Доступно по подписке</span>
            </span>
          </div>
          
          <div v-if="auction.category" class="auction-category">
            Категория: {{ auction.category }}
          </div>
          
          <div class="auction-dates">
            <div class="date-row">
              <span class="date-label">Начало:</span>
              <span class="date-value">{{ formatDate(auction.start_time || auction.start_date) }}</span>
            </div>
            <div class="date-row">
              <span class="date-label">Окончание:</span>
              <span class="date-value">{{ formatDate(auction.end_time || auction.end_date) }}</span>
            </div>
          </div>
          
          <div class="auction-status" :class="getStatusClass">
            {{ getStatusText }}
          </div>
          
          <div v-if="auction.description" class="auction-description">
            <h3>Описание</h3>
            <p>{{ auction.description }}</p>
          </div>
          
          <div v-if="auction.charity" class="auction-charity">
            <h3>Создатель:</h3>
            <p>{{ getCharityName }}</p>
            <p v-if="auction.charity.description">{{ auction.charity.description }}</p>
          </div>
        </div>
      </div>
      
      <!-- Секция с лотами -->
      <div v-if="!needsTicket" class="lots-section">
        <div class="section-header">
          <h2>Лоты аукциона</h2>
          
          <!-- Кнопка создания лота (только для доноров) -->
          <button 
            v-if="authStore.isAuthenticated && authStore.user.role === 'donor'" 
            @click="navigateToCreateLot" 
            class="create-lot-btn"
          >
            Создать новый лот
          </button>
        </div>
        
        <!-- Индикатор загрузки лотов -->
        <loading-spinner v-if="lotsStore.loading" text="Загрузка лотов..." />
        
        <!-- Ошибка при загрузке лотов -->
        <div v-if="lotsStore.error" class="error-message">
          {{ lotsStore.error }}
        </div>
        
        <!-- Нет лотов -->
        <div v-if="!lotsStore.loading && !lotsStore.lots.length" class="empty-lots">
          <p>У этого аукциона пока нет лотов</p>
        </div>
        
        <!-- Сетка лотов -->
        <div v-if="!lotsStore.loading && filteredLots.length > 0" class="lots-grid">
          <lot-card 
            v-for="lot in filteredLots" 
            :key="lot.id" 
            :lot="lot"
          />
        </div>
      </div>
      
      <!-- Сообщение, если требуется билет -->
      <div v-else class="access-restricted">
        <div class="restricted-icon">🔒</div>
        <h3>Доступ ограничен</h3>
        
        <!-- Информация о платной подписке -->
        <div class="subscription-info" v-if="authStore.isAuthenticated && authStore.user.role === 'buyer'">
          <p>Для просмотра лотов этого аукциона необходимо приобрести билет или оформить премиум-подписку</p>
          <div class="access-options">
            <button @click="showTicketForm = true" class="buy-ticket-btn">
              Купить билет ({{ formatPrice(auction.ticket_price) }})
            </button>
            <button @click="goToSubscription" class="subscribe-btn">
              Оформить подписку ({{ formatPrice(599) }}/месяц)
            </button>
          </div>
          <div class="subscription-benefits">
            <p>Преимущества подписки:</p>
            <ul>
              <li>Доступ ко всем платным аукционам без покупки билетов</li>
              <li>Неограниченное участие в течение месяца</li>
            </ul>
          </div>
        </div>
        
        <!-- Информация для неавторизованных пользователей -->
        <div v-else>
          <p>Для просмотра лотов этого аукциона необходимо приобрести билет</p>
          <div class="access-options">
            <button @click="showTicketForm = true" class="buy-ticket-btn">
              Купить билет ({{ formatPrice(auction.ticket_price) }})
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuctionsStore } from '../store/auctionsStore';
import { useLotsStore } from '../store/lotsStore';
import { useAuthStore } from '../store/auth';
import LotCard from '../components/LotCard.vue';
import LoadingSpinner from '../components/LoadingSpinner.vue';
import TicketPurchaseForm from '../components/TicketPurchaseForm.vue';
import apiClient from '../api/axios';
import { useTicketsStore } from '../store/ticketsStore';
import { useSubscriptionStore } from '../store/subscriptionStore';
export default {
  name: 'AuctionDetailView',
  
  components: {
    LotCard,
    LoadingSpinner,
    TicketPurchaseForm
  },
  
  setup() {
    const route = useRoute();
    const router = useRouter();
    const auctionsStore = useAuctionsStore();
    const lotsStore = useLotsStore();
    const authStore = useAuthStore();
    
    const loading = ref(false);
    const error = ref(null);
    const showTicketForm = ref(false);
    const hasTicket = ref(false);
    const needsTicket = ref(false);
    const ticketsStore = useTicketsStore();
    const subscriptionStore = useSubscriptionStore();
    // Вычисляемое свойство для проверки наличия активной подписки
    const hasSubscription = computed(() => subscriptionStore.isActive);
    // Получение ID аукциона из параметров маршрута
    const auctionId = computed(() => route.params.id);
    
    // Данные аукциона
    const auction = computed(() => auctionsStore.currentAuction);

    const formatPrice = (price) => {
    if (!price) return '0 ₽';
    return new Intl.NumberFormat('ru-RU', {
      style: 'currency',
      currency: 'RUB',
      minimumFractionDigits: 0
    }).format(price);
  };
   // Переход на страницу профиля для оформления подписки
   const goToSubscription = () => {
    // Сохраняем текущий URL аукциона, чтобы вернуться после оформления подписки
    localStorage.setItem('redirect_after_subscription', router.currentRoute.value.fullPath);
    
    // Перенаправляем на страницу профиля с параметром для автоматического открытия модального окна подписки
    router.push('/profile?showSubscription=true');
  };
    // Отфильтрованные лоты данного аукциона
    const filteredLots = computed(() => {
  if (!lotsStore.lots || !auction.value) return [];
  
  // Сначала фильтруем по аукциону
  let lots = lotsStore.lots.filter(lot => lot.auction === parseInt(auctionId.value));
  
  // Дополнительная фильтрация в зависимости от роли пользователя
  if (authStore.isAuthenticated) {
    if (authStore.user.role === 'donor') {
      // Доноры видят все свои лоты (в любом статусе) и одобренные лоты других доноров
      lots = lots.filter(lot => 
        ['approved', 'sold'].includes(lot.status) || 
        lot.donor === authStore.user.id || 
        lot.donor_username === authStore.user.username
      );
    } else if (authStore.user.role === 'charity' && auction.value.charity === authStore.user.charity?.id) {
      // Владельцы аукциона видят все лоты
      // Не фильтруем
    } else {
      // Покупатели видят только одобренные и проданные лоты
      lots = lots.filter(lot => ['approved', 'sold'].includes(lot.status));
    }
  } else {
    // Неавторизованные пользователи видят только одобренные и проданные лоты
    lots = lots.filter(lot => ['approved', 'sold'].includes(lot.status));
  }
  
  return lots;
});
    
    // Загрузка данных аукциона
    const fetchAuctionData = async () => {
      loading.value = true;
      error.value = null;
      
      try {
        await auctionsStore.fetchAuctionById(auctionId.value);
        
        // Если аукцион платный, проверяем наличие билета
        if (auction.value?.is_paid) {
          if (auction.value?.needs_ticket) {
            needsTicket.value = true;
          } else {
            await checkTicket();
          }
        }
        
        // Если у пользователя есть доступ, загружаем лоты
        if (!needsTicket.value) {
          await lotsStore.fetchLotsByAuction(auctionId.value);
        }
      } catch (err) {
        console.error('Ошибка при загрузке данных аукциона:', err);
        error.value = 'Не удалось загрузить данные аукциона';
      } finally {
        loading.value = false;
      }
    };
    
    // Проверка наличия билета
    // Проверка наличия билета
// Проверка наличия билета
const checkTicket = async () => {
  if (!authStore.isAuthenticated || !auction.value?.is_paid) {
    needsTicket.value = false;
    return;
  }
  
  // Владельцы аукциона всегда имеют доступ
  if (authStore.user.role === 'charity' && 
      auction.value?.charity === authStore.user.charity?.id) {
    needsTicket.value = false;
    return;
  }
  
  // Доноры всегда имеют доступ
  if (authStore.user.role === 'donor') {
    needsTicket.value = false;
    return;
  }
  try {
    await subscriptionStore.fetchSubscriptionStatus();
    
    // Если есть активная подписка, предоставляем доступ
    if (subscriptionStore.isActive) {
      needsTicket.value = false;
      hasTicket.value = true;
      return;
    }
  } catch (err) {
    console.error('Ошибка при проверке подписки:', err);
    // Продолжаем проверку наличия билета
  }
  // Проверяем сначала в localStorage
  try {
    // Получаем сохраненные билеты из localStorage
    const storedTickets = localStorage.getItem('user_tickets');
    
    if (storedTickets) {
      const tickets = JSON.parse(storedTickets);
      // Проверяем, есть ли билет на текущий аукцион
      const hasStoredTicket = tickets.some(ticket => 
        ticket.auction == auctionId.value || 
        ticket.auction_id == auctionId.value
      );
      
      if (hasStoredTicket) {
        console.log('Найден билет в localStorage для аукциона:', auctionId.value);
        hasTicket.value = true;
        needsTicket.value = false;
        return;
      }
    }
  } catch (err) {
    console.error('Ошибка при проверке билетов в localStorage:', err);
    // Продолжаем выполнение и проверяем через API
  }
  
  // Если в localStorage нет билета, проверяем через API
  try {
    const response = await apiClient.get(`/auctions/tickets/check-access/?auction_id=${auctionId.value}`);
    hasTicket.value = response.data?.has_ticket || false;
    
    // Если API подтвердил наличие билета, сохраняем его в localStorage для будущих сеансов
    if (hasTicket.value && response.data?.ticket) {
      try {
        // Получаем существующие билеты или создаем новый массив
        const existingTickets = localStorage.getItem('user_tickets') 
          ? JSON.parse(localStorage.getItem('user_tickets')) 
          : [];
        
        // Проверяем, нет ли уже такого билета в хранилище
        const ticketExists = existingTickets.some(t => 
          t.id === response.data.ticket.id || 
          (t.auction == auctionId.value && t.user == authStore.user.id)
        );
        
        if (!ticketExists) {
          // Добавляем новый билет
          existingTickets.push(response.data.ticket);
          localStorage.setItem('user_tickets', JSON.stringify(existingTickets));
          console.log('Билет сохранен в localStorage:', response.data.ticket);
        }
      } catch (storageErr) {
        console.error('Ошибка при сохранении билета в localStorage:', storageErr);
      }
    }
    
    needsTicket.value = !hasTicket.value;
  } catch (err) {
    console.error('Ошибка при проверке билета через API:', err);
    // Если не удалось проверить билет, предполагаем что он нужен
    needsTicket.value = true;
  }
};
    
    // Обработка успешной покупки билета
// Обработка успешной покупки билета
const handleTicketPurchased = async (ticketData) => {
  // Сохраняем купленный билет в localStorage
  try {
    // Получаем существующие билеты или создаем новый массив
    const existingTickets = localStorage.getItem('user_tickets') 
      ? JSON.parse(localStorage.getItem('user_tickets')) 
      : [];
    
    // Формируем информацию о билете, если она не передана в ticketData
    const newTicket = ticketData || {
      id: Date.now(), // временный ID если нет настоящего
      auction: parseInt(auctionId.value),
      auction_name: auction.value?.name || auction.value?.title,
      user: authStore.user.id,
      user_email: authStore.user.email,
      purchase_date: new Date().toISOString(),
      is_used: false
    };
    
    // Добавляем новый билет
    existingTickets.push(newTicket);
    localStorage.setItem('user_tickets', JSON.stringify(existingTickets));
    console.log('Билет добавлен в localStorage после покупки:', newTicket);
  } catch (err) {
    console.error('Ошибка при сохранении купленного билета в localStorage:', err);
  }
  
  // Ждем чтобы пользователь увидел сообщение об успехе
  setTimeout(async () => {
    showTicketForm.value = false;
    hasTicket.value = true;
    needsTicket.value = false;
    await lotsStore.fetchLotsByAuction(auctionId.value);
  }, 2000);
};
    
    // Закрытие формы покупки билета
    const closeTicketForm = () => {
      showTicketForm.value = false;
    };
    
    // Переход на страницу создания лота
    const navigateToCreateLot = () => {
    router.push(`/create-lot?auctionId=${auctionId.value}`);
    };
    onMounted(() => {
      fetchAuctionData();
    });
    
    // При изменении ID аукциона, загружаем новые данные
    watch(() => route.params.id, () => {
      if (route.params.id) {
        fetchAuctionData();
      }
    });
    
    // Функция для форматирования даты
    const formatDate = (dateString) => {
      if (!dateString) return 'Не указано';
      
      const date = new Date(dateString);
      return new Intl.DateTimeFormat('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      }).format(date);
    };
    
    // Определение статуса аукциона
    const getStatusClass = computed(() => {
      if (!auction.value) return '';
      
      const now = new Date();
      const startDate = new Date(auction.value.start_time || auction.value.start_date);
      const endDate = new Date(auction.value.end_time || auction.value.end_date);
      
      if (now < startDate) return 'upcoming';
      if (now > endDate) return 'ended';
      return 'active';
    });
    
    // Текст статуса аукциона
    const getStatusText = computed(() => {
      switch (getStatusClass.value) {
        case 'upcoming': return 'Ожидается';
        case 'active': return 'Активен';
        case 'ended': return 'Завершен';
        default: return 'Неизвестно';
      }
    });
    
    // Получение имени благотворительной организации
    const getCharityName = computed(() => {
      if (!auction.value || !auction.value.charity) return 'Не указано';
      
      // Проверяем различные варианты структуры данных
      if (typeof auction.value.charity === 'object') {
        return auction.value.charity.name || auction.value.charity_name || auction.value.charity.title || 'Не указано';
      }
      
      // Используем поле charity_name, если оно есть в данных аукциона
      if (auction.value.charity_name) {
        return auction.value.charity_name;
      }
      
      // Если charity - это ID, то возвращаем строку с ID
      if (typeof auction.value.charity === 'number') {
        return `Организация #${auction.value.charity}`;
      }
      
      // Если это строка, то возвращаем ее
      if (typeof auction.value.charity === 'string') {
        return auction.value.charity;
      }
      
      return 'Не указано';
    });
    
    return {
      loading,
    error,
    auction,
    auctionId,
    filteredLots,
    formatDate,
    formatPrice,
    getStatusClass,
    getStatusText,
    getCharityName,
    navigateToCreateLot,
    showTicketForm,
    hasTicket,
    needsTicket,
    closeTicketForm,
    handleTicketPurchased,
    goToSubscription,
    authStore,
    lotsStore,
    subscriptionStore,
    hasSubscription: computed(() => subscriptionStore.isActive) 
    };
  }
};
</script>

<style scoped>
.auction-detail-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
  background: linear-gradient(135deg, #EDE7F6 0%, #E3F2FD 100%);
}

.breadcrumbs {
  margin-bottom: 20px;
  color: #6c757d;
  font-size: 14px;
}

.breadcrumbs a {
  color: #007bff;
  text-decoration: none;
}

.breadcrumbs a:hover {
  text-decoration: underline;
}

.breadcrumbs span {
  margin: 0 8px;
}

.auction-header {
  display: flex;
  gap: 32px;
  margin-bottom: 40px;
}

.auction-image-container {
  flex: 0 0 400px;
  height: 300px;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 24px;
  padding: 25px 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #fafafa;
  box-shadow: inset 0 0 8px rgba(0, 0, 0, 0.03);
}

.auction-image {
  width: 100%;
  max-height: 350px;
  object-fit: contain;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.no-image {
  width: 100%;
  height: 100%;
  background-color: #f8f9fa;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6c757d;
}

.auction-info {
  flex: 1;
}

.auction-title {
  margin: 0 0 16px;
  font-size: 32px;
  color: #333;
}

.auction-category {
  margin-bottom: 16px;
  color: #6c757d;
  font-size: 14px;
}

.auction-dates {
  margin-bottom: 16px;
}

.date-row {
  margin-bottom: 8px;
}

.date-label {
  color: black;
  margin-right: 8px;
}

.date-value {
  font-weight: 500;
}

.auction-status {
  display: inline-block;
  padding: 6px 12px;
  border-radius: 4px;
  font-weight: bold;
  font-size: 14px;
  margin-bottom: 24px;
}

.auction-status.upcoming {
  background-color: #e2f0fd;
  color: #0d6efd;
}

.auction-status.active {
  background-color: #d4edda;
  color: #198754;
}

.auction-status.ended {
  background-color: #f8d7da;
  color: #dc3545;
}

.auction-description {
  margin-bottom: 24px;
  background-color: #f5f7fa;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
}

.auction-charity {
  background-color: #f0f8ff;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 24px;
  border-left: 4px solid var(--primary-color);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
}

.auction-description h3,
.auction-charity h3 {
  font-size: 18px;
  margin-bottom: 12px;
  color: #444;
  font-weight: 600;
}

.auction-description p,
.auction-charity p {
  color: #555;
  line-height: 1.5;
  background-color: rgba(255, 255, 255, 0.6);
  padding: 10px;
  border-radius: 6px;
  border: 1px solid #eef1f6;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.section-header h2 {
  margin: 0;
  font-size: 24px;
  color: #333;
}

.create-lot-btn {
  padding: 8px 16px;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.create-lot-btn:hover {
  background-color: #218838;
}

.lots-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
}

.empty-lots {
  text-align: center;
  padding: 48px 0;
  background-color: #f8f9fa;
  border-radius: 8px;
  color: #6c757d;
}

.error-message {
  background-color: #f8d7da;
  color: #721c24;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 24px;
  text-align: center;
}

.access-restricted {
  text-align: center;
  padding: 48px 0;
  background-color: #f8f9fa;
  border-radius: 8px;
  color: #6c757d;
}

.restricted-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.access-restricted h3 {
  font-size: 24px;
  margin-bottom: 16px;
}

.access-restricted p {
  margin-bottom: 24px;
}

.buy-ticket-btn {
  padding: 8px 16px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.buy-ticket-btn:hover {
  background-color: #0056b3;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal-content {
  background-color: white;
  padding: 24px;
  border-radius: 8px;
  max-width: 400px;
  width: 100%;
}

.auction-paid-badge {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.paid-icon {
  margin-right: 8px;
}

.paid-text {
  margin-right: 8px;
}

.ticket-price {
  font-weight: 500;
}

.ticket-required {
  margin-bottom: 24px;
}
.access-restricted {
  text-align: center;
  padding: 32px 24px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #dee2e6;
  margin: 20px 0;
}

.restricted-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.access-restricted h3 {
  font-size: 24px;
  margin-bottom: 16px;
  color: #343a40;
}

.access-restricted p {
  margin-bottom: 24px;
  color: #495057;
}

.access-options {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-bottom: 24px;
}

.buy-ticket-btn, .subscribe-btn {
  padding: 10px 18px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 15px;
  font-weight: 500;
  border: none;
  transition: background-color 0.3s, transform 0.1s;
}

.buy-ticket-btn {
  background-color: #007bff;
  color: white;
}

.buy-ticket-btn:hover {
  background-color: #0069d9;
  transform: translateY(-2px);
}

.subscribe-btn {
  background-color: #28a745;
  color: white;
}

.subscribe-btn:hover {
  background-color: #218838;
  transform: translateY(-2px);
}

.subscription-benefits {
  text-align: left;
  background-color: #e9f7ef;
  padding: 16px;
  border-radius: 6px;
  max-width: 500px;
  margin: 0 auto;
}

.subscription-benefits p {
  font-weight: 500;
  margin-bottom: 8px;
  color: #2c3e50;
}

.subscription-benefits ul {
  margin: 0;
  padding-left: 20px;
}

.subscription-benefits li {
  margin-bottom: 8px;
  color: #4a6072;
}

@media (max-width: 576px) {
  .access-options {
    flex-direction: column;
    gap: 12px;
  }
  
  .buy-ticket-btn, .subscribe-btn {
    width: 100%;
  }
}

@media (max-width: 992px) {
  .auction-header {
    flex-direction: column;
    gap: 24px;
  }
  
  .auction-image-container {
    flex: none;
    width: 100%;
    max-width: 100%;
  }
}

@media (max-width: 768px) {
  .auction-detail-container {
    padding: 16px;
  }
  
  .auction-title {
    font-size: 24px;
  }
  
  .lots-grid {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  }
}
</style> 