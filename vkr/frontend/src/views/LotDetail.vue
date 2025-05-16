<template>
  <div class="lot-detail-container">
    <!-- Хлебные крошки -->
    <div class="breadcrumbs">
      <router-link :to="{ name: 'home' }">Главная</router-link>
      <span>/</span>
      <router-link :to="{ name: 'auctions' }">Аукционы</router-link>
      <span>/</span>
      <router-link v-if="lot?.auction" :to="{ name: 'auction-detail', params: { id: lot.auction } }">Аукцион</router-link>
      <span>/</span>
      <span>{{ lot?.title || 'Лот' }}</span>
    </div>

    <!-- Индикатор загрузки -->
    <loading-spinner v-if="loading" text="Загрузка информации о лоте..." />

    <!-- Сообщение об ошибке -->
    <div v-if="error" class="error-message">
      {{ error }}
    </div>

    <!-- Содержимое лота -->
    <div v-if="!loading && lot && canViewLot" class="lot-content">
      <div class="lot-header">
        <h1>{{ lot.title }}</h1>
        <div class="lot-status" :class="getStatusClass">
          {{ getStatusText }}
        </div>
      </div>

      <!-- Кнопки редактирования и удаления (только для донора и статуса pending) -->
      <div v-if="isDonorOwner && lot.status === 'pending'" class="lot-actions">
        <button @click="editLot" class="btn-edit">Редактировать</button>
        <button @click="showDeleteConfirmation = true" class="btn-delete">Удалить</button>
      </div>

      <!-- Кнопки одобрения и отклонения (только для благотворительной организации и статуса pending) -->
      <div v-if="isCharity && lot.status === 'pending'" class="lot-actions charity-actions">
        <button @click="approveLot" class="btn-approve" :disabled="processing">
          {{ processing && approving ? 'Одобрение...' : 'Одобрить' }}
        </button>
        <button @click="showRejectConfirmation = true" class="btn-reject" :disabled="processing">
          {{ processing && rejecting ? 'Отклонение...' : 'Отклонить' }}
        </button>
      </div>

      <div class="lot-grid">
        <!-- Левая колонка - изображение и информация о доноре -->
        <div class="lot-left">
          <div class="lot-image">
            <img v-if="getImageUrl" :src="getImageUrl" :alt="lot.title" />
            <div v-else class="no-image">Нет изображения</div>
          </div>
          <div class="lot-donor">
            <h3>Донор:</h3>
            <p>{{ getDonorName }}</p>
          </div>
        </div>

        <!-- Правая колонка - детали и описание -->
        <div class="lot-right">
          <div class="lot-details">
            <div class="lot-price">
              <h3>Стартовая цена:</h3>
              <p>{{ formatPrice(lot.starting_price) }}</p>
            </div>
          </div>

          <div class="lot-description">
            <h3>Описание:</h3>
            <p>{{ lot.description || 'Описание отсутствует' }}</p>
          </div>
        </div>
      </div>

      <div class="lot-comments-section">
        <h3>Комментарии</h3>
        <CommentsList :lotId="lotId" />
        <template v-if="canBidOrComment">
          <CommentForm v-if="lot.status === 'approved' && isAuthenticated" :lotId="lotId" />
        </template>
        <template v-else>
          <div class="bid-error" style="margin: 12px 0;">Комментирование будет доступно после начала аукциона</div>
        </template>
      </div>

      <template v-if="canBidOrComment">
        <div v-if="lot.status === 'approved' && isBuyer" class="bid-form-section">
          <h3>Сделать ставку</h3>
          <div class="bid-form-row">
            <input type="number" v-model="bidAmount" :min="minBid" :placeholder="`Минимум ${minBid} ₽`" class="bid-input" :disabled="bidStore.loading" />
            <button @click="placeBid" :disabled="bidStore.loading || !bidAmount" class="btn-make-bid">Сделать ставку</button>
          </div>
          <div v-if="bidError" class="bid-error">{{ bidError }}</div>
          <div v-if="bidSuccess" class="bid-success">Ставка успешно создана!</div>
        </div>
      </template>
      <template v-else>
        <div class="bid-form-section">
          <div class="bid-error" style="margin: 12px 0;">Ставки будут доступны после начала аукциона</div>
        </div>
      </template>

      <div class="lot-bids-section">
        <h3>Ставки</h3>
        <div v-if="bidStore.loading && lotBids.length === 0" class="bids-loading">
          <loading-spinner text="Загрузка ставок..." />
        </div>
        <div v-else-if="lotBids.length === 0" class="bids-empty">Ставок пока нет</div>
        <div v-else>
          <BidCard 
            v-for="bid in lotBids" 
            :key="bid.id" 
            :bid="bid" 
            :formatPrice="formatPrice" 
            :formatDate="(d) => new Date(d).toLocaleString('ru-RU', {day: '2-digit', month: '2-digit', year: '2-digit', hour: '2-digit', minute: '2-digit'})" 
            :highestAmount="Math.max(...lotBids.map(b => Number(b.amount)))"
            :isWinner="(String(lot.status).toLowerCase() === 'sold' || String(lot.status).toLowerCase() === 'продан') && Number(bid.amount) === Math.max(...lotBids.map(b => Number(b.amount)))"
          />
          
          <!-- Кнопка "Оплатить" для покупателя-победителя -->
          <div v-if="isWinner && (String(lot.status).toLowerCase() === 'sold' || String(lot.status).toLowerCase() === 'продан') && !lot.is_paid" class="winner-action">
            <button @click="payForLot" class="btn-pay">Оплатить</button>
          </div>
        </div>
      </div>
    </div>
    <div v-else-if="!loading && lot && !canViewLot" class="lot-no-access">
      <p>У вас нет доступа к этому лоту.</p>
    </div>

    <!-- Форма редактирования (показывается при редактировании) -->
    <div v-if="isEditing" class="edit-form-overlay">
      <div class="edit-form">
        <h2>Редактирование лота</h2>
        
        <div class="form-group">
          <label for="title">Название:</label>
          <input type="text" id="title" v-model="editForm.title" class="form-control">
          <div v-if="validation.title" class="validation-error">{{ validation.title }}</div>
        </div>
        
        <div class="form-group">
          <label for="description">Описание:</label>
          <textarea id="description" v-model="editForm.description" class="form-control" rows="4"></textarea>
          <div v-if="validation.description" class="validation-error">{{ validation.description }}</div>
        </div>
        
        <div class="form-group">
          <label for="starting_price">Стартовая цена (руб.):</label>
          <input type="number" id="starting_price" v-model="editForm.starting_price" class="form-control">
          <div v-if="validation.starting_price" class="validation-error">{{ validation.starting_price }}</div>
        </div>
        
        <div class="form-actions">
          <button @click="cancelEdit" class="btn-cancel">Отмена</button>
          <button @click="saveEdit" class="btn-save" :disabled="submitting">
            {{ submitting ? 'Сохранение...' : 'Сохранить' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Модальное окно подтверждения удаления -->
    <div v-if="showDeleteConfirmation" class="delete-confirmation-overlay">
      <div class="delete-confirmation">
        <h2>Подтверждение удаления</h2>
        <p>Вы уверены, что хотите удалить лот "{{ lot?.title }}"?</p>
        <p>Это действие нельзя отменить.</p>
        
        <div class="confirmation-actions">
          <button @click="showDeleteConfirmation = false" class="btn-cancel">Отмена</button>
          <button @click="deleteLot" class="btn-delete" :disabled="submitting">
            {{ submitting ? 'Удаление...' : 'Удалить' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Окно подтверждения отклонения (встроенное, не всплывающее) -->
    <div v-if="showRejectConfirmation" class="reject-confirmation-inline">
      <div class="reject-confirmation">
        <h2>Подтверждение отклонения</h2>
        <p>Вы уверены, что хотите отклонить лот "{{ lot?.title }}"?</p>
        <p>Это действие нельзя отменить.</p>
        <div v-if="rejectionError" class="error-message">
          {{ rejectionError }}
        </div>
        <div class="confirmation-actions">
          <button @click="showRejectConfirmation = false" class="btn-cancel">Отмена</button>
          <button @click="rejectLot" class="btn-reject" :disabled="processing">
            {{ processing && rejecting ? 'Отклонение...' : 'Отклонить' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, reactive } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useLotsStore } from '../store/lotsStore';
import { useAuthStore } from '../store/auth';
import LoadingSpinner from '../components/LoadingSpinner.vue';
import CommentsList from '../components/CommentsList.vue';
import CommentForm from '../components/CommentForm.vue';
import BidCard from '../components/BidCard.vue';
import { useBidStore } from '../store/bidStore';
import { useAuctionsStore } from '../store/auctionsStore';

export default {
  name: 'LotDetailView',
  
  components: {
    LoadingSpinner,
    CommentsList,
    CommentForm,
    BidCard
  },
  
  props: {
    id: {
      type: [String, Number],
      required: true
    }
  },
  
  setup(props) {
    const route = useRoute();
    const router = useRouter();
    const lotsStore = useLotsStore();
    const authStore = useAuthStore();
    const bidStore = useBidStore();
    const auctionsStore = useAuctionsStore();
    
    // Состояние
    const loading = ref(true);
    const error = ref(null);
    const submitting = ref(false);
    const isEditing = ref(false);
    const showDeleteConfirmation = ref(false);
    
    // Состояние для одобрения/отклонения
    const showRejectConfirmation = ref(false);
    const processing = ref(false);
    const approving = ref(false);
    const rejecting = ref(false);
    const rejectionError = ref('');
    
    // Получение ID лота из параметров маршрута или пропсов
    const lotId = computed(() => props.id || route.params.id);
    
    // Данные лота
    const lot = computed(() => lotsStore.currentLot);
    
    // Данные аукциона
    const auction = ref(null);
    const auctionStatus = computed(() => {
      if (!auction.value) return null;
      // Можно использовать поле status, либо вычислять по времени
      if (auction.value.status) return auction.value.status;
      // Если нет статуса, вычисляем по времени
      const now = new Date();
      const start = new Date(auction.value.start_time || auction.value.start_date);
      const end = new Date(auction.value.end_time || auction.value.end_date);
      if (now < start) return 'upcoming';
      if (now > end) return 'ended';
      return 'active';
    });
    
    // Форма редактирования
    const editForm = reactive({
      title: '',
      description: '',
      starting_price: 0
    });
    
    // Валидация формы
    const validation = reactive({
      title: '',
      description: '',
      starting_price: ''
    });
    
    // Проверка, является ли текущий пользователь донором этого лота
    const isDonorOwner = computed(() => {
      if (!authStore.isAuthenticated || !lot.value) return false;
      if (authStore.user.role !== 'donor') return false;
      
      // Проверяем, является ли пользователь владельцем лота
      // (может отличаться в зависимости от структуры данных API)
      return lot.value.donor === authStore.user.id || 
             lot.value.donor_username === authStore.user.username;
    });
    
    // Проверка, является ли текущий пользователь благотворительной организацией
    const isCharity = computed(() => {
      if (!authStore.isAuthenticated) return false;
      return authStore.user.role === 'charity';
    });
    
    // Получение URL изображения
    const getImageUrl = computed(() => {
      // Добавляем параметр времени для предотвращения кэширования
      const timestamp = lot.value?.images && lot.value.images[0] ? `?v=${lot.value.images[0].id}` : `?v=${Date.now()}`;
      if (lot.value?.images && lot.value.images.length > 0) {
        if (lot.value.images[0].image_url) {
          return `${lot.value.images[0].image_url}${timestamp}`;
        }
        if (lot.value.images[0].image) {
          if (lot.value.images[0].image.startsWith('http')) {
            return `${lot.value.images[0].image}${timestamp}`;
          } else {
            return `http://localhost:8000${lot.value.images[0].image}${timestamp}`;
          }
        }
      }
      if (lot.value?.image) {
        if (lot.value.image.startsWith('http')) {
          return `${lot.value.image}${timestamp}`;
        } else {
          return `http://localhost:8000${lot.value.image}${timestamp}`;
        }
      }
      return null;
    });
    
    // Класс статуса лота
    const getStatusClass = computed(() => {
      if (!lot.value) return '';
      
      const status = lot.value.status;
      
      switch (status) {
        case 'pending': return 'pending';
        case 'approved': return 'approved';
        case 'rejected': return 'rejected';
        case 'active': return 'active';
        case 'sold': return 'sold';
        case 'not_sold': return 'not-sold';
        default: return 'default';
      }
    });
    
    // Текст статуса лота
    const getStatusText = computed(() => {
      if (!lot.value) return '';
      
      const statusTexts = {
        'pending': 'На рассмотрении',
        'approved': 'Доступен для торга',
        'rejected': 'Отклонен',
        'active': 'Активен',
        'sold': 'Продан',
        'not_sold': 'Не продан'
      };
      
      return statusTexts[lot.value.status] || 'Неизвестно';
    });
    
    // Имя донора
    const getDonorName = computed(() => {
      if (!lot.value?.donor && !lot.value?.donor_username) return 'Неизвестный донор';
      
      // Если есть поля donor_first_name и donor_last_name, используем их
      if (lot.value?.donor_first_name || lot.value?.donor_last_name) {
        if (lot.value.donor_first_name && lot.value.donor_last_name) {
          return `${lot.value.donor_first_name} ${lot.value.donor_last_name}`;
        } else if (lot.value.donor_first_name) {
          return lot.value.donor_first_name;
        } else if (lot.value.donor_last_name) {
          return lot.value.donor_last_name;
        }
      }
      
      // Проверяем объект donor
      if (typeof lot.value.donor === 'object') {
        const donor = lot.value.donor;
        
        // Приоритизируем имя и фамилию
        if (donor.first_name && donor.last_name) {
          return `${donor.first_name} ${donor.last_name}`;
        } else if (donor.first_name) {
          return donor.first_name;
        } else if (donor.last_name) {
          return donor.last_name;
        } else if (donor.username) {
          return donor.username;
        } else if (donor.email) {
          // Отображаем имя пользователя из email
          const emailParts = donor.email.split('@');
          return emailParts[0];
        } else {
          return 'Неизвестный донор';
        }
      }
      
      // Если в лоте есть поле donor_username, используем его
      if (lot.value.donor_username) {
        return lot.value.donor_username;
      }
      
      // Если donor - это ID, то возвращаем строку с ID
      if (typeof lot.value.donor === 'number') {
        return `Донор #${lot.value.donor}`;
      }
      
      return 'Неизвестный донор';
    });
    
    // Функция для форматирования цены
    const formatPrice = (price) => {
      if (price === null || price === undefined) return 'Не указана';
      return new Intl.NumberFormat('ru-RU', {
        style: 'currency',
        currency: 'RUB',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
      }).format(price);
    };
    
    // Можно ли оставлять комментарии и делать ставки
    const canBidOrComment = computed(() => auctionStatus.value === 'active');
    
    // Загрузка данных лота и аукциона
    const loadLot = async () => {
      loading.value = true;
      error.value = null;
      try {
        const data = await lotsStore.fetchLotById(lotId.value);
        if (!data) {
          error.value = 'Не удалось загрузить информацию о лоте';
        } else {
          // Загружаем аукцион
          if (data.auction) {
            auction.value = await auctionsStore.fetchAuctionById(data.auction);
          }
          forceImageReload();
        }
      } catch (err) {
        error.value = 'Ошибка при загрузке лота';
        console.error('Error loading lot:', err);
      } finally {
        loading.value = false;
      }
    };
    
    // Функция принудительного обновления изображения
    const forceImageReload = () => {
      // Добавляем случайный параметр времени к URL изображения для сброса кэша браузера
      if (lot.value?.images && lot.value.images.length > 0) {
        // Генерируем уникальный ключ для URL
        const timestamp = new Date().getTime();
        
        // Добавляем параметр к URL или обновляем существующий
        if (lot.value.images[0].image_url) {
          lot.value.images[0].image_url = updateUrlWithTimestamp(lot.value.images[0].image_url, timestamp);
        }
        
        if (lot.value.images[0].image) {
          lot.value.images[0].image = updateUrlWithTimestamp(lot.value.images[0].image, timestamp);
        }
      }
    };
    
    // Обновление URL с добавлением или обновлением параметра времени
    const updateUrlWithTimestamp = (url, timestamp) => {
      // Если URL уже содержит параметры
      if (url.includes('?')) {
        // Если уже есть параметр t, заменяем его
        if (url.includes('t=')) {
          return url.replace(/t=\d+/, `t=${timestamp}`);
        } else {
          // Иначе добавляем новый параметр
          return `${url}&t=${timestamp}`;
        }
      } else {
        // Если нет параметров, добавляем первый
        return `${url}?t=${timestamp}`;
      }
    };
    
    // Инициализация формы редактирования
    const initEditForm = () => {
      if (!lot.value) return;
      
      editForm.title = lot.value.title || '';
      editForm.description = lot.value.description || '';
      editForm.starting_price = lot.value.starting_price || 0;
    };
    
    // Переход в режим редактирования
    const editLot = () => {
      router.push({ 
        name: 'create-lot', 
        query: { 
          auctionId: lot.value.auction,
          lotId: lotId.value,
          edit: 'true'
        } 
      });
    };
    
    // Отмена редактирования
    const cancelEdit = () => {
      isEditing.value = false;
    };
    
    // Проверка валидности формы
    const validateForm = () => {
      let isValid = true;
      
      // Сброс ошибок валидации
      validation.title = '';
      validation.description = '';
      validation.starting_price = '';
      
      // Проверка названия
      if (!editForm.title.trim()) {
        validation.title = 'Название лота не может быть пустым';
        isValid = false;
      }
      
      // Проверка стартовой цены
      if (!editForm.starting_price || editForm.starting_price <= 0) {
        validation.starting_price = 'Стартовая цена должна быть больше нуля';
        isValid = false;
      }
      
      return isValid;
    };
    
    // Сохранение изменений
    const saveEdit = async () => {
      if (!validateForm()) return;
      
      submitting.value = true;
      
      try {
        const updatedLot = await lotsStore.updateLot(lotId.value, {
          title: editForm.title,
          description: editForm.description,
          starting_price: editForm.starting_price
        });
        
        if (updatedLot) {
          isEditing.value = false;
          // Обновление данных в компоненте
          await loadLot();
        } else {
          error.value = 'Не удалось обновить лот';
        }
      } catch (err) {
        error.value = 'Ошибка при обновлении лота';
        console.error('Error updating lot:', err);
      } finally {
        submitting.value = false;
      }
    };
    
    // Удаление лота
    const deleteLot = async () => {
      submitting.value = true;
      
      try {
        const success = await lotsStore.deleteLot(lotId.value);
        
        if (success) {
          // Перенаправление на страницу аукциона после удаления
          router.push({ 
            name: 'auction-detail', 
            params: { id: lot.value.auction } 
          });
        } else {
          error.value = 'Не удалось удалить лот';
          showDeleteConfirmation.value = false;
        }
      } catch (err) {
        error.value = 'Ошибка при удалении лота';
        console.error('Error deleting lot:', err);
        showDeleteConfirmation.value = false;
      } finally {
        submitting.value = false;
      }
    };
    
    // Функция одобрения лота
    const approveLot = async () => {
      processing.value = true;
      approving.value = true;
      
      try {
        console.log(`Попытка одобрить лот с ID ${lotId.value}`);
        const response = await lotsStore.approveLot(lotId.value);
        console.log('Результат одобрения:', response);
        // Перезагрузка данных лота
        await loadLot();
      } catch (err) {
        error.value = 'Ошибка при одобрении лота';
        console.error('Error approving lot:', err);
      } finally {
        processing.value = false;
        approving.value = false;
      }
    };
    
    // Функция отклонения лота
    const rejectLot = async () => {
      processing.value = true;
      rejecting.value = true;
      rejectionError.value = '';
      
      try {
        console.log(`Попытка отклонить лот с ID ${lotId.value}`);
        const response = await lotsStore.rejectLot(lotId.value);
        console.log('Результат отклонения:', response);
        showRejectConfirmation.value = false;
        // Перезагрузка данных лота
        await loadLot();
      } catch (err) {
        console.error('Error rejecting lot:', err);
        rejectionError.value = err.message || 'Ошибка при отклонении лота';
      } finally {
        processing.value = false;
        rejecting.value = false;
      }
    };
    
    // Проверка, может ли пользователь видеть не одобренный лот
    const canViewLot = computed(() => {
      if (!lot.value) return false;
      
      const status = String(lot.value.status).toLowerCase();
      if (status === 'approved' || status === 'доступен для торга') return true;
      if (status === 'sold' || status === 'продан' || status === 'not_sold' || status === 'не продан') return true;
      
      if (!authStore.isAuthenticated) return false;
      // Донор-владелец
      if (authStore.user.role === 'donor' && (lot.value.donor === authStore.user.id || lot.value.donor_username === authStore.user.username)) return true;
      // Владелец аукциона (charity)
      if (authStore.user.role === 'charity' && lot.value.auction_charity_id === authStore.user.charity?.id) return true;
      // Покупатель не видит не одобренные лоты
      return false;
    });
    
    // Покупатель
    const isBuyer = computed(() => authStore.isAuthenticated && authStore.user.role === 'buyer');
    const isAuthenticated = computed(() => authStore.isAuthenticated);
    
    const lotBids = computed(() => bidStore.sortedBids);
    
    const bidAmount = ref('');
    const bidError = ref('');
    const bidSuccess = ref(false);
    const minBid = computed(() => {
      // Минимальная ставка — стартовая цена или максимальная из существующих + 1
      if (!lot.value) return 1;
      const maxBid = lotBids.value.length > 0 ? Math.max(...lotBids.value.map(b => Number(b.amount))) : 0;
      return Math.max(Number(lot.value.starting_price), maxBid + 1);
    });
    const placeBid = async () => {
      bidError.value = '';
      bidSuccess.value = false;
      const amount = Number(bidAmount.value);
      if (!amount || amount < minBid.value) {
        bidError.value = `Минимальная ставка: ${minBid.value} ₽`;
        return;
      }
      const res = await bidStore.createBid(lotId.value, amount);
      if (res) {
        bidSuccess.value = true;
        bidAmount.value = '';
        await bidStore.fetchLotBids(lotId.value);
        setTimeout(() => bidSuccess.value = false, 1500);
      } else {
        bidError.value = bidStore.error || 'Ошибка при создании ставки';
      }
    };
    
    // Проверка, является ли текущий пользователь победителем
    const isWinner = computed(() => {
      if (!lot.value) return false;
      if (!authStore.isAuthenticated) return false;
      
      // Проверяем статус лота (может быть "sold" или "Продан")
      const lotStatusLower = String(lot.value.status).toLowerCase();
      if (lotStatusLower !== 'sold' && lotStatusLower !== 'продан') return false;
      
      if (lotBids.value.length === 0) return false;
      
      // Находим максимальную ставку
      const maxBid = Math.max(...lotBids.value.map(b => Number(b.amount)));
      
      // Находим ставку с максимальной суммой
      const winningBid = lotBids.value.find(b => Number(b.amount) === maxBid);
      
      // Проверяем, принадлежит ли выигрышная ставка текущему пользователю
      return winningBid && winningBid.user === authStore.user.id;
    });
    
    // Функция оплаты лота
    const payForLot = async () => {
      if (!isWinner.value) return;
      
      try {
        console.log('Starting payment process for lot:', lotId.value);
        
        // Находим максимальную ставку текущего пользователя для этого лота
        const winningBid = lotBids.value.find(b => 
          Number(b.amount) === Math.max(...lotBids.value.map(b => Number(b.amount))) && 
          b.user === authStore.user.id
        );
        
        if (!winningBid) {
          error.value = 'Не найдена выигрышная ставка';
          console.error('Winning bid not found');
          return;
        }
        
        console.log('Found winning bid:', winningBid.id, 'with amount:', winningBid.amount);
        
        // Сохраняем ID ставки в localStorage для надежности
        localStorage.setItem('winningBidId', winningBid.id);
        localStorage.setItem('lotId', lotId.value);
        
        // Перенаправление на страницу оплаты
        console.log('Navigating to payment page with bid ID:', winningBid.id);
        router.push({ 
          path: '/payment',
          query: { 
            bidId: winningBid.id,
            lotId: lotId.value
          }
        });
      } catch (err) {
        error.value = 'Ошибка при обработке запроса';
        console.error('Error in payForLot function:', err);
      }
    };
    
    onMounted(() => {
      loadLot();
      bidStore.fetchLotBids(lotId.value);
    });
    
    return {
      lot,
      loading,
      error,
      lotId,
      isDonorOwner,
      isCharity,
      getImageUrl,
      getStatusClass,
      getStatusText,
      getDonorName,
      formatPrice,
      isEditing,
      editForm,
      validation,
      editLot,
      cancelEdit,
      saveEdit,
      showDeleteConfirmation,
      submitting,
      deleteLot,
      forceImageReload,
      updateUrlWithTimestamp,
      approveLot,
      rejectLot,
      showRejectConfirmation,
      processing,
      approving,
      rejecting,
      rejectionError,
      canViewLot,
      isBuyer,
      isAuthenticated,
      lotBids,
      bidStore,
      bidAmount,
      bidError,
      bidSuccess,
      minBid,
      placeBid,
      isWinner,
      payForLot,
      auction,
      auctionStatus,
      canBidOrComment
    };
  }
}
</script>

<style scoped>
.lot-detail-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

.breadcrumbs {
  margin-bottom: 20px;
  color: #007bff;
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

.error-message {
  background-color: #f8d7da;
  color: #721c24;
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 20px;
}

.lot-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.lot-header h1 {
  margin: 0;
  font-size: 28px;
  color: #333;
}

.lot-status {
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 14px;
  font-weight: bold;
}

.lot-status.pending {
  background-color: #fff3cd;
  color: #856404;
}

.lot-status.approved {
  background-color: #d4edda;
  color: #155724;
}

.lot-status.rejected {
  background-color: #f8d7da;
  color: #721c24;
}

.lot-status.active {
  background-color: #d1ecf1;
  color: #0c5460;
}

.lot-status.sold {
  background-color: #e2e3e5;
  color: #383d41;
}

.lot-status.not-sold {
  background-color: #f8f9fa;
  color: #6c757d;
}

.lot-actions {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}

.btn-edit, .btn-delete, .btn-save, .btn-cancel {
  padding: 8px 16px;
  border-radius: 4px;
  font-weight: bold;
  cursor: pointer;
  border: none;
  transition: background-color 0.3s;
}

.btn-edit {
  background-color: #007bff;
  color: white;
}

.btn-edit:hover {
  background-color: #0069d9;
}

.btn-delete {
  background-color: #dc3545;
  color: white;
}

.btn-delete:hover {
  background-color: #c82333;
}

.btn-save {
  background-color: #28a745;
  color: white;
}

.btn-save:hover {
  background-color: #218838;
}

.btn-cancel {
  background-color: #6c757d;
  color: white;
}

.btn-cancel:hover {
  background-color: #5a6268;
}

.btn-edit:disabled, .btn-delete:disabled, .btn-save:disabled, .btn-cancel:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.lot-grid {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 32px;
}

.lot-left, .lot-right {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.lot-image {
  width: 100%;
  max-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  border-radius: 8px;
  margin-bottom: 24px;
  padding: 25px 20px;
  background-color: #fafafa;
  box-shadow: inset 0 0 8px rgba(0, 0, 0, 0.03);
}

.lot-image img {
  max-width: 100%;
  max-height: 350px;
  object-fit: contain;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.no-image {
  width: 100%;
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f8f9fa;
  color: #6c757d;
  font-size: 16px;
}

.lot-donor {
  background-color: #f0f8ff;
  padding: 18px;
  border-radius: 8px;
  margin-bottom: 24px;
  border-left: 4px solid var(--primary-color);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
}

.lot-donor h3 {
  margin-bottom: 10px;
  color: var(--primary-color);
  font-weight: 600;
}

.lot-donor p {
  color: #555;
  font-weight: 500;
  background-color: rgba(255, 255, 255, 0.6);
  padding: 6px 10px;
  border-radius: 4px;
}

.lot-details, .lot-description {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 20px;
  margin-bottom: 20px;
}

.lot-details h3, .lot-description h3 {
  margin-top: 0;
  margin-bottom: 12px;
  color: #495057;
  font-size: 18px;
}

.lot-details {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.categories-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.category-chip {
  background-color: #e9ecef;
  color: #495057;
  padding: 4px 10px;
  border-radius: 16px;
  font-size: 14px;
}

.edit-form-overlay, .delete-confirmation-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.edit-form, .delete-confirmation {
  background-color: white;
  border-radius: 8px;
  padding: 24px;
  max-width: 500px;
  width: 100%;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.edit-form h2, .delete-confirmation h2 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #333;
  font-size: 20px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
  color: #495057;
}

.form-control {
  width: 100%;
  padding: 10px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 16px;
}

.form-control:focus {
  border-color: #80bdff;
  outline: 0;
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
}

.validation-error {
  color: #dc3545;
  font-size: 14px;
  margin-top: 6px;
}

.form-actions, .confirmation-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}

.btn-approve {
  background-color: #28a745;
  color: white;
  padding: 8px 16px;
  border-radius: 4px;
  font-weight: bold;
  cursor: pointer;
  border: none;
  transition: background-color 0.3s;
}

.btn-approve:hover {
  background-color: #218838;
}

.btn-reject {
  background-color: #dc3545;
  color: white;
  padding: 8px 16px;
  border-radius: 4px;
  font-weight: bold;
  cursor: pointer;
  border: none;
  transition: background-color 0.3s;
}

.btn-reject:hover {
  background-color: #c82333;
}

.charity-actions {
  margin-bottom: 24px;
}

@media (max-width: 768px) {
  .lot-grid {
    grid-template-columns: 1fr;
  }
  
  .lot-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .lot-status {
    align-self: flex-start;
  }
}

.reject-confirmation-inline {
  margin: 32px auto;
  max-width: 500px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.12);
  padding: 24px;
}

.lot-no-access {
  color: #888;
  text-align: center;
  margin: 40px 0;
  font-size: 20px;
}

.lot-bids-section {
  margin: 32px 0 0 0;
}
.bids-loading {
  display: flex;
  justify-content: center;
  margin: 12px 0;
}
.bids-empty {
  color: #888;
  text-align: center;
  margin: 18px 0;
}

.bid-form-section {
  margin: 32px 0 16px 0;
  background: #f8f9fa;
  border-radius: 8px;
  padding: 18px 20px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.bid-form-row {
  display: flex;
  gap: 12px;
  align-items: center;
}
.bid-input {
  width: auto;
  padding: 6px 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 16px;
}
.btn-make-bid {
  background: #007bff;
  color: #fff;
  border: none;
  padding: 7px 18px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 15px;
  transition: background 0.2s;
}
.btn-make-bid:disabled {
  background: #b3d1fa;
  cursor: not-allowed;
}
.bid-error {
  color: #dc3545;
  margin-top: 8px;
}
.bid-success {
  color: #198754;
  margin-top: 8px;
}

.winner-action {
  margin-top: 16px;
  text-align: right;
}

.btn-pay {
  background-color: #28a745;
  color: white;
  padding: 8px 16px;
  border-radius: 4px;
  font-weight: bold;
  cursor: pointer;
  border: none;
  transition: background-color 0.3s;
}

.btn-pay:hover {
  background-color: #218838;
}

.lot-description {
  background-color: #f7f7fa;
  padding: 18px;
  border-radius: 8px;
  margin-bottom: 24px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
}

.lot-description h3 {
  margin-bottom: 12px;
  color: #444;
  font-weight: 600;
}

.lot-description p {
  white-space: pre-line;
  color: #555;
  background-color: rgba(255, 255, 255, 0.6);
  padding: 10px;
  border-radius: 6px;
  border: 1px solid #eef1f6;
}
</style> 