<template>
  <div class="lot-card">
    <div class="lot-image" @click="navigateToLot">
      <img v-if="getImageUrl" :src="getImageUrl" :alt="lot.title" />
      <div v-else class="no-image">Нет изображения</div>
    </div>
    <div class="lot-content">
      <h3 class="lot-title" @click="navigateToLot">{{ lot.title }}</h3>
      <div class="lot-category" v-if="lot.category">
        {{ lot.category }}
      </div>
      <div class="lot-price">
        <span class="price-label">Стартовая цена:</span>
        <span class="price-value">{{ formatPrice(lot.starting_price) }}</span>
      </div>
      <div class="lot-donor" v-if="lot.donor">
        <span>Донор: {{ getDonorName }}</span>
      </div>
      <div class="lot-status" :class="getStatusClass">
        {{ getStatusText }}
      </div>
      <div class="lot-bids" v-if="lot.bids_count !== undefined">
        <span>{{ getBidsText }}</span>
      </div>
      
      <!-- Кнопки редактирования и удаления для донора (только для лотов со статусом "на рассмотрении") -->
      <div v-if="showDonorControls" class="lot-donor-controls">
        <button @click.stop="editLot" class="btn-edit">Редактировать</button>
        <button @click.stop="deleteLot" class="btn-delete" :disabled="deleting">
          {{ deleting ? 'Удаление...' : 'Удалить' }}
        </button>
      </div>
      
      <!-- Кнопки одобрения и отклонения для благотворительной организации -->
      <div v-if="showCharityControls" class="lot-charity-controls">
        <button @click.stop="approveLot" class="btn-approve" :disabled="processing">
          {{ processing && approving ? 'Одобрение...' : 'Одобрить' }}
        </button>
        <button @click.stop="rejectLot" class="btn-reject" :disabled="processing || rejecting">
          {{ processing && rejecting ? 'Отклонение...' : 'Отклонить' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../store/auth';
import { useLotsStore } from '../store/lotsStore';

export default {
  name: 'LotCard',
  
  props: {
    lot: {
      type: Object,
      required: true
    }
  },
  
  setup(props) {
    const router = useRouter();
    const authStore = useAuthStore();
    const lotsStore = useLotsStore();
    
    // Состояние для удаления
    const showDeleteConfirmation = ref(false);
    const deleting = ref(false);
    
    // Состояние для одобрения/отклонения
    const processing = ref(false);
    const approving = ref(false);
    const rejecting = ref(false);
    
    // Получение URL изображения
    const getImageUrl = computed(() => {
      // Добавляем параметр времени для предотвращения кэширования
      const timestamp = `?v=${props.lot.images && props.lot.images[0] ? props.lot.images[0].id || Date.now() : Date.now()}`;
      if (props.lot.images && props.lot.images.length > 0) {
        if (props.lot.images[0].image_url) {
          return `${props.lot.images[0].image_url}${timestamp}`;
        }
        if (props.lot.images[0].image) {
          if (props.lot.images[0].image.startsWith('http')) {
            return `${props.lot.images[0].image}${timestamp}`;
          } else {
            return `http://localhost:8000${props.lot.images[0].image}${timestamp}`;
          }
        }
      }
      if (props.lot.image) {
        if (props.lot.image.startsWith('http')) {
          return `${props.lot.image}${timestamp}`;
        } else {
          return `http://localhost:8000${props.lot.image}${timestamp}`;
        }
      }
      return null;
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
    
    // Определение статуса лота
    const getStatusClass = computed(() => {
      const status = props.lot.status;
      
      switch (status) {
        case 'pending': return 'pending';
        case 'approved': return 'approved';
        case 'rejected': return 'rejected';
        case 'active': return 'active';
        case 'sold': return 'sold';
        default: return 'default';
      }
    });
    
    // Текст статуса лота
    const getStatusText = computed(() => {
      const statusTexts = {
        'pending': 'На рассмотрении',
        'approved': 'Доступен для торга',
        'rejected': 'Отклонен',
        'active': 'Активен',
        'sold': 'Продан'
      };
      
      return statusTexts[props.lot.status] || 'Неизвестно';
    });
    
    // Текст о ставках
    const getBidsText = computed(() => {
      const count = props.lot.bids_count || 0;
      
      if (count === 0) {
        return 'Нет ставок';
      } else if (count === 1) {
        return '1 ставка';
      } else {
        return `${count} ставок`;
      }
    });
    
    // Имя донора
    const getDonorName = computed(() => {
      if (!props.lot.donor && !props.lot.donor_username) return 'Неизвестный донор';
      
      // Если есть поля donor_first_name и donor_last_name, используем их
      if (props.lot.donor_first_name || props.lot.donor_last_name) {
        if (props.lot.donor_first_name && props.lot.donor_last_name) {
          return `${props.lot.donor_first_name} ${props.lot.donor_last_name}`;
        } else if (props.lot.donor_first_name) {
          return props.lot.donor_first_name;
        } else if (props.lot.donor_last_name) {
          return props.lot.donor_last_name;
        }
      }
      
      // Проверяем объект donor
      if (typeof props.lot.donor === 'object') {
        const donor = props.lot.donor;
        
        // Приоритет: имя и фамилия, если они есть
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
      if (props.lot.donor_username) {
        return props.lot.donor_username;
      }
      
      // Если donor - это ID, то возвращаем строку с ID
      if (typeof props.lot.donor === 'number') {
        return `Донор #${props.lot.donor}`;
      }
      
      return 'Неизвестный донор';
    });
    
    // Проверка, показывать ли элементы управления донора
    const showDonorControls = computed(() => {
      // Проверяем аутентификацию и роль пользователя
      if (!authStore.isAuthenticated || authStore.user.role !== 'donor') return false;
      
      // Проверяем, является ли пользователь донором этого лота
      const isDonorOwner = props.lot.donor === authStore.user.id || 
                          props.lot.donor_username === authStore.user.username;
      
      // Проверяем статус лота (должен быть "pending")
      const isPending = props.lot.status === 'pending';
      
      return isDonorOwner && isPending;
    });
    
    // Проверка, показывать ли элементы управления благотворительной организации
    const showCharityControls = computed(() => {
      // Проверяем аутентификацию и роль пользователя (должен быть charity)
      if (!authStore.isAuthenticated || authStore.user.role !== 'charity') return false;
      
      // Проверяем статус лота (должен быть "pending")
      const isPending = props.lot.status === 'pending';
      
      return isPending;
    });
    
    // Функция перехода на страницу лота
    const navigateToLot = () => {
      router.push({ name: 'lot', params: { id: props.lot.id } });
    };
    
    // Функция редактирования лота
    const editLot = () => {
      router.push({ 
        name: 'create-lot', 
        query: { 
          auctionId: props.lot.auction,
          lotId: props.lot.id,
          edit: 'true'
        } 
      });
    };
    
    // Функция удаления лота
    const deleteLot = async () => {
      deleting.value = true;
      
      try {
        const success = await lotsStore.deleteLot(props.lot.id);
        
        if (success) {
          // Обновляем список лотов (можно использовать emit для уведомления родительского компонента)
          window.location.reload(); // Временное решение, лучше использовать более элегантный подход
        }
      } catch (err) {
        console.error('Error deleting lot:', err);
      } finally {
        deleting.value = false;
      }
    };
    
    // Функция одобрения лота
    const approveLot = async () => {
      processing.value = true;
      approving.value = true;
      
      try {
        console.log(`Попытка одобрить лот с ID ${props.lot.id}`);
        const response = await lotsStore.approveLot(props.lot.id);
        console.log('Результат одобрения:', response);
        // Обновляем страницу для отображения изменений
        setTimeout(() => window.location.reload(), 500);
      } catch (err) {
        console.error('Error approving lot:', err);
        alert(`Ошибка при одобрении лота: ${err.message || 'Неизвестная ошибка'}`);
      } finally {
        processing.value = false;
        approving.value = false;
      }
    };
    
    // Функция отклонения лота
    const rejectLot = async () => {
      processing.value = true;
      rejecting.value = true;
      try {
        const response = await lotsStore.rejectLot(props.lot.id);
        setTimeout(() => window.location.reload(), 500);
      } catch (err) {
        console.error('Error rejecting lot:', err);
        alert(`Ошибка при отклонении лота: ${err.message || 'Неизвестная ошибка'}`);
      } finally {
        processing.value = false;
        rejecting.value = false;
      }
    };
    
    return {
      formatPrice,
      getStatusClass,
      getStatusText,
      getBidsText,
      getDonorName,
      navigateToLot,
      getImageUrl,
      showDonorControls,
      showCharityControls,
      editLot,
      deleting,
      deleteLot,
      approveLot,
      rejectLot
    };
  }
}
</script>

<style scoped>
.lot-card {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: transform 0.3s, box-shadow 0.3s;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  height: 100%;
  position: relative;
}

.lot-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.lot-image {
  height: 200px;
  overflow: hidden;
  position: relative;
  padding: 20px 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #fafafa;
}

.lot-image img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: #fff;
  border-radius: 6px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
}

.no-image {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  background-color: #f8f9fa;
  color: #6c757d;
  font-size: 14px;
}

.lot-content {
  padding: 16px;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.lot-title {
  margin: 0 0 8px;
  font-size: 18px;
  color: #333;
  line-height: 1.3;
}

.lot-category {
  font-size: 14px;
  color: #6c757d;
  margin-bottom: 12px;
}

.lot-price {
  margin-top: 8px;
  margin-bottom: 8px;
  font-size: 14px;
}

.price-label {
  color: #6c757d;
  margin-right: 6px;
}

.price-value {
  color: #333;
  font-weight: 700;
  font-size: 16px;
}

.lot-description {
  margin-top: 10px;
  font-size: 14px;
  color: #666;
  background-color: #f5f7fa;
  padding: 10px 12px;
  border-radius: 6px;
  margin-bottom: 12px;
  box-shadow: inset 0 0 3px rgba(0, 0, 0, 0.05);
  border: 1px solid #eef1f6;
}

.lot-donor {
  font-size: 14px;
  color: #6c757d;
  margin-bottom: 12px;
  margin-top: auto;
  background-color: #f0f8ff;
  padding: 10px 12px;
  border-radius: 6px;
  border-left: 3px solid var(--primary-color);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.lot-status {
  margin-top: 12px;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
  text-align: center;
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

.lot-bids {
  margin-top: 8px;
  font-size: 12px;
  color: #6c757d;
  text-align: center;
}

.lot-donor-controls {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}

.btn-edit, .btn-delete, .btn-cancel {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 14px;
  font-weight: bold;
  cursor: pointer;
  border: none;
  transition: background-color 0.3s;
  flex: 1;
  text-align: center;
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

.btn-cancel {
  background-color: #6c757d;
  color: white;
}

.btn-cancel:hover {
  background-color: #5a6268;
}

/* Стили для кнопок благотворительной организации */
.lot-charity-controls {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}

.btn-approve {
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 6px 12px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.3s;
  flex: 1;
}

.btn-approve:hover {
  background-color: #218838;
}

.btn-reject {
  background-color: #dc3545;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 6px 12px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.3s;
  flex: 1;
}

.btn-reject:hover {
  background-color: #c82333;
}
</style> 