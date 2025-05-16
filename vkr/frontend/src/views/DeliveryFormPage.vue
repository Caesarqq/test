<template>
  <div class="delivery-page-container">
    <h1>Оформление доставки</h1>
    
    <!-- Компонент уведомлений -->
    <alert-message 
      :show="alertShow" 
      :message="alertMessage" 
      :type="alertType" 
      :auto-hide="true" 
      :duration="5000"
      @close="hideAlert"
    />
    
    <!-- Индикатор загрузки -->
    <loading-spinner v-if="loading" text="Загрузка данных..." />
    
    <!-- Содержимое страницы -->
    <div v-if="!loading" class="delivery-content">
      <!-- Данные о лоте -->
      <div v-if="transactionData" class="lot-info">
        <h2>Информация о покупке</h2>
        <div class="info-row">
          <span class="label">Лот:</span>
          <span class="value">{{ transactionData.lot_title || `Лот №${transactionData.lot}` }}</span>
        </div>
        <div class="info-row">
          <span class="label">Сумма:</span>
          <span class="value">{{ formatPrice(transactionData.amount) }}</span>
        </div>
        <div class="info-row">
          <span class="label">Дата оплаты:</span>
          <span class="value">{{ formatDate(transactionData.payment_time) }}</span>
        </div>
      </div>
      
      <!-- Ошибка при загрузке транзакции -->
      <div v-if="error" class="error-message">
        {{ error }}
      </div>
      
      <!-- Форма доставки -->
      <div class="form-container">
        <form v-if="!success" @submit.prevent="submitForm" class="delivery-form">
          <div class="form-group">
            <label for="recipient_name">ФИО получателя*</label>
            <input 
              type="text" 
              id="recipient_name" 
              v-model="form.recipient_name" 
              required 
              :class="{ 'is-invalid': validation.recipient_name }"
            />
            <div v-if="validation.recipient_name" class="invalid-feedback">
              {{ validation.recipient_name }}
            </div>
          </div>
          
          <div class="form-group">
            <label>Тип доставки*</label>
            <div class="delivery-type-options">
              <label class="delivery-option">
                <input 
                  type="radio" 
                  v-model="form.delivery_type" 
                  value="courier" 
                  name="delivery_type"
                  :class="{ 'is-invalid': validation.delivery_type }"
                />
                <span class="delivery-option-label">Курьером</span>
              </label>
              <label class="delivery-option">
                <input 
                  type="radio" 
                  v-model="form.delivery_type" 
                  value="pickup" 
                  name="delivery_type"
                  :class="{ 'is-invalid': validation.delivery_type }"
                />
                <span class="delivery-option-label">Самовывоз</span>
              </label>
            </div>
            <div v-if="validation.delivery_type" class="invalid-feedback">
              {{ validation.delivery_type }}
            </div>
            <div v-if="form.delivery_type === 'pickup'" class="pickup-info">
               <p class="pickup-address">
                <strong>Адрес самовывоза:</strong> г. Москва, ул. Примерная, д. 123
              </p>
              <p class="pickup-hours">
                <strong>Время работы:</strong> Пн-Пт с 10:00 до 19:00, Сб с 11:00 до 17:00
              </p>
            </div>
          </div>
          
          <div class="form-group" v-if="form.delivery_type === 'courier'">
            <label for="address">Адрес доставки*</label>
            <textarea 
              id="address" 
              v-model="form.address" 
              required 
              rows="3"
              :class="{ 'is-invalid': validation.address }"
            ></textarea>
            <div v-if="validation.address" class="invalid-feedback">
              {{ validation.address }}
            </div>
          </div>
          
          <div class="form-group">
            <label for="delivery_date">Дата доставки*</label>
            <input 
              type="date" 
              id="delivery_date" 
              v-model="form.delivery_date" 
              required
              :min="minDeliveryDate"
              :class="{ 'is-invalid': validation.delivery_date }"
            />
            <div v-if="validation.delivery_date" class="invalid-feedback">
              {{ validation.delivery_date }}
            </div>
            <div class="delivery-date-hint" v-if="form.delivery_type === 'courier'">
              Доставка курьером осуществляется в течение 3-7 рабочих дней
            </div>
            <div class="delivery-date-hint" v-if="form.delivery_type === 'pickup'">
              Самовывоз доступен с указанной даты из пункта выдачи
            </div>
          </div>
          
          <div class="form-group">
            <label for="phone">Телефон*</label>
            <input 
              type="tel" 
              id="phone" 
              v-model="form.phone" 
              required 
              placeholder="+7 (___) ___-__-__"
              :class="{ 'is-invalid': validation.phone }"
            />
            <div v-if="validation.phone" class="invalid-feedback">
              {{ validation.phone }}
            </div>
          </div>
          
          <div class="form-group">
            <label for="comments">Дополнительная информация</label>
            <textarea 
              id="comments" 
              v-model="form.comments" 
              rows="2"
              placeholder="Комментарии к доставке, время получения и т.д."
            ></textarea>
          </div>
          
          <div class="form-actions">
            <button type="button" @click="goBack" class="btn-secondary">
              Отмена
            </button>
            <button type="submit" class="btn-primary" :disabled="loading">
              {{ loading ? 'Сохранение...' : 'Сохранить' }}
            </button>
          </div>
        </form>
        
        <!-- Сообщение об успешном сохранении -->
        <div v-if="success" class="success-message">
          <h3>Данные доставки сохранены</h3>
          <p>Информация о доставке успешно сохранена. Вы получите уведомление, когда лот будет отправлен.</p>
          <button @click="goToProfile" class="btn-primary">Вернуться в профиль</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { reactive, ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useBidStore } from '../store/bidStore';
import { useAuthStore } from '../store/auth';
import LoadingSpinner from '../components/LoadingSpinner.vue';
import AlertMessage from '../components/AlertMessage.vue';

export default {
  name: 'DeliveryFormPage',
  
  components: {
    LoadingSpinner,
    AlertMessage
  },
  
  setup() {
    const route = useRoute();
    const router = useRouter();
    const bidStore = useBidStore();
    const authStore = useAuthStore();
    
    // Состояние загрузки
    const loading = ref(false);
    const error = ref('');
    const success = ref(false);
    
    // Состояние уведомлений
    const alertShow = ref(false);
    const alertMessage = ref('');
    const alertType = ref('info');
    
    // Данные транзакции
    const transactionData = ref(null);
    
    // Получаем параметры из маршрута
    const transactionId = ref(route.params.id);
    const bidId = ref(route.query.bidId || route.params.bidId || localStorage.getItem('winningBidId'));
    const lotId = ref(route.query.lotId || route.params.lotId || localStorage.getItem('lotId'));
    
    // Очищаем localStorage после получения параметров
    if (bidId.value && lotId.value) {
      localStorage.removeItem('winningBidId');
      localStorage.removeItem('lotId');
    }
    
    // Форма данных доставки
    const form = reactive({
      recipient_name: '',
      address: '',
      phone: '',
      comments: '',
      delivery_type: 'courier',
      delivery_date: ''
    });
    
    // Валидация формы
    const validation = reactive({
      recipient_name: '',
      address: '',
      phone: '',
      delivery_type: '',
      delivery_date: ''
    });
    
    // Проверка авторизации
    const checkAuth = () => {
      if (!authStore.isAuthenticated) {
        router.push({ name: 'login' });
        return false;
      }
      return true;
    };
    
    // Показ уведомления
    const showAlert = (message, type = 'info') => {
      alertMessage.value = message;
      alertType.value = type;
      alertShow.value = true;
    };
    
    // Скрытие уведомления
    const hideAlert = () => {
      alertShow.value = false;
    };
    
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
        minimumFractionDigits: 2
      }).format(price);
    };
    
    // Минимальная дата доставки (завтра)
    const minDeliveryDate = computed(() => {
      const today = new Date();
      const tomorrow = new Date(today);
      tomorrow.setDate(today.getDate() + 1); // минимум завтра
      return tomorrow.toISOString().split('T')[0]; // формат YYYY-MM-DD
    });
    
    // Установка текущей даты по умолчанию
    onMounted(() => {
      const today = new Date();
      const defaultDate = new Date(today);
      defaultDate.setDate(today.getDate() + 3); // по умолчанию через 3 дня
      form.delivery_date = defaultDate.toISOString().split('T')[0];
    });
    
    // Проверка корректности транзакции
    const validateTransactionId = () => {
      // Если параметр id существует, проверяем его
      if (transactionId.value) {
        // Для симулированной транзакции (начинается с 'sim-') пропускаем проверку
        if (String(transactionId.value).startsWith('sim-')) {
          return true;
        }
        
        // Валидация, что transactionId - число
        if (isNaN(parseInt(transactionId.value))) {
          showAlert('Некорректный идентификатор транзакции', 'error');
          return false;
        }
        
        return true;
      }
      
      // Если нет transactionId, получаем из localStorage
      const storedTransactionId = localStorage.getItem('transactionId');
      if (storedTransactionId) {
        transactionId.value = storedTransactionId;
        localStorage.removeItem('transactionId');
        return validateTransactionId(); // Рекурсивно вызываем проверку теперь уже с значением
      }
      
      // Если оба способа не дали результата
      showAlert('Не указан идентификатор транзакции', 'error');
      return false;
    };
    
    // Загрузка данных транзакции и текущих данных доставки, если есть
    const loadTransactionData = async () => {
      // Проверка авторизации
      if (!checkAuth()) return;
      
      loading.value = true;
      
      // Проверяем, есть ли симулированные данные платежа
      const simulatedPaymentData = localStorage.getItem('simulatedPayment');
      
      // Если это эмулированный платеж
      if ((route.query.simulated === 'true' || transactionId.value && String(transactionId.value).startsWith('sim-')) && simulatedPaymentData) {
        try {
          const paymentData = JSON.parse(simulatedPaymentData);
          
          // Создаем объект с данными транзакции на основе симуляции
          transactionData.value = {
            id: paymentData.id || ('sim-' + Date.now()),
            lot: paymentData.lotId,
            lot_title: lotId.value ? `Лот №${lotId.value}` : (bidId.value ? `Лот ставки №${bidId.value}` : 'Лот'),
            amount: paymentData.amount || 0,
            payment_time: paymentData.date || new Date().toISOString(),
            status: 'completed',
            simulated: true
          };
          
          localStorage.removeItem('simulatedPayment');
          loading.value = false;
          return;
        } catch (err) {
          console.error('Ошибка при разборе симулированных данных:', err);
          // Продолжаем обычную загрузку
        }
      }
      
      // Проверка параметров
      if (!transactionId.value && (bidId.value || lotId.value)) {
        // У нас нет идентификатора транзакции, но есть bidId или lotId
        // В этом случае попробуем найти транзакцию по выигрышам пользователя
        try {
          console.log('Поиск транзакции по', bidId.value ? `bidId=${bidId.value}` : `lotId=${lotId.value}`);
          
          // Получаем данные о выигрышах пользователя
          const winnings = await bidStore.fetchUserWinnings();
          console.log('Получены выигрыши пользователя:', winnings);
          
          // Находим нужную транзакцию по bidId или lotId
          if (winnings && winnings.length > 0) {
            let transaction;
            
            if (bidId.value) {
              // Находим по связанной ставке
              // Предполагаем, что у транзакции есть поле bid_id или каким-то образом можно связать транзакцию с ставкой
              transaction = winnings.find(t => {
                console.log('Проверяем транзакцию:', t);
                // Проверяем наличие bid_id в транзакции или другие возможные связи
                return (t.bid_id == bidId.value) || 
                       (t.bid && t.bid.id == bidId.value) || 
                       (t.bid == bidId.value);
              });
            } else if (lotId.value) {
              // Находим по лоту
              transaction = winnings.find(t => {
                console.log('Проверяем транзакцию по лоту:', t);
                return t.lot == lotId.value;
              });
            }
            
            if (transaction) {
              console.log('Найдена транзакция по параметрам:', transaction);
              transactionId.value = transaction.id;
              transactionData.value = transaction;
              loading.value = false;
              return;
            } else {
              console.log('Транзакция не найдена по указанным параметрам');
            }
          } else {
            console.log('У пользователя нет выигрышей или список пуст');
          }
        } catch (err) {
          console.error('Ошибка при поиске транзакции:', err);
        }
      }
      
      // Проверка валидности ID транзакции
      if (!validateTransactionId()) {
        loading.value = false;
        return;
      }
      
      try {
        console.log('Загрузка данных транзакции с ID:', transactionId.value);
        
        // Если у нас уже есть transactionId, но нет transactionData (или мы хотим обновить данные)
        // Получаем данные о транзакции
        if (transactionId.value && !String(transactionId.value).startsWith('sim-')) {
          const response = await bidStore.fetchTransactionById(transactionId.value);
          console.log('Получены данные о транзакции:', response);
          
          if (response) {
            transactionData.value = response;
            console.log('Данные о транзакции успешно загружены и сохранены');
          } else {
            console.warn('Не удалось получить данные о транзакции по ID:', transactionId.value);
            error.value = 'Не удалось загрузить данные о транзакции';
          }
        }
      } catch (err) {
        console.error('Ошибка при загрузке данных транзакции:', err);
        error.value = 'Ошибка при загрузке данных транзакции. Пожалуйста, попробуйте еще раз.';
      } finally {
        loading.value = false;
      }
    };
    
    // Валидация формы
    const validateForm = () => {
      let isValid = true;
      
      // Очистка предыдущих ошибок
      Object.keys(validation).forEach(key => {
        validation[key] = '';
      });
      
      // Проверка ФИО
      if (!form.recipient_name.trim()) {
        validation.recipient_name = 'ФИО получателя обязательно';
        isValid = false;
      } else if (form.recipient_name.length < 3) {
        validation.recipient_name = 'ФИО должно содержать не менее 3 символов';
        isValid = false;
      }
      
      // Проверка типа доставки
      if (!form.delivery_type) {
        validation.delivery_type = 'Выберите тип доставки';
        isValid = false;
      }
      
      // Проверка адреса (только для курьерской доставки)
      if (form.delivery_type === 'courier') {
        if (!form.address.trim()) {
          validation.address = 'Адрес доставки обязателен';
          isValid = false;
        } else if (form.address.length < 10) {
          validation.address = 'Адрес должен содержать не менее 10 символов';
          isValid = false;
        }
      }
      
      // Проверка даты доставки
      if (!form.delivery_date) {
        validation.delivery_date = 'Дата доставки обязательна';
        isValid = false;
      } else {
        const today = new Date();
        const selectedDate = new Date(form.delivery_date);
        today.setHours(0, 0, 0, 0);
        
        // Проверка, что дата не в прошлом
        if (selectedDate < today) {
          validation.delivery_date = 'Дата доставки не может быть в прошлом';
          isValid = false;
        }
      }
      
      // Проверка телефона
      if (!form.phone.trim()) {
        validation.phone = 'Телефон обязателен';
        isValid = false;
      } else {
        // Простая проверка формата телефона
        const phoneRegex = /^(\+7|8)[\s\-]?\(?[0-9]{3}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$/;
        if (!phoneRegex.test(form.phone)) {
          validation.phone = 'Неверный формат телефона';
          isValid = false;
        }
      }
      
      return isValid;
    };
    
    // Отправка формы
    const submitForm = async () => {
      if (!validateForm()) return;
      
      loading.value = true;
      error.value = '';
      
      try {
        // Если это эмулированный платеж, создаем симуляцию успешной доставки
        if (transactionData.value && transactionData.value.simulated) {
          console.log('Эмуляция сохранения данных доставки для симулированной транзакции');
          
          // Симулируем успешное сохранение данных
          setTimeout(() => {
            success.value = true;
            showAlert('Данные доставки успешно сохранены!', 'success');
            loading.value = false;
          }, 1000);
          
          return;
        }
        
        // Проверяем ID транзакции
        if (!transactionId.value || String(transactionId.value).startsWith('sim-')) {
          error.value = 'Не удается идентифицировать транзакцию для сохранения доставки';
          loading.value = false;
          return;
        }
        
        // Формируем объект с данными доставки
        const deliveryData = {
          transaction: transactionId.value, // Важно добавить ID транзакции
          recipient_name: form.recipient_name,
          phone: form.phone,
          delivery_type: form.delivery_type,
          delivery_date: form.delivery_date,
          comments: form.comments || ''
        };
        
        // Добавляем адрес только для курьерской доставки
        if (form.delivery_type === 'courier') {
          deliveryData.address = form.address;
        } else {
          deliveryData.address = 'Самовывоз из офиса: г. Москва, ул. Примерная, д. 123';
        }
        
        console.log('Отправка данных доставки для транзакции ID:', transactionId.value);
        console.log('Данные доставки:', deliveryData);
        
        // Сохраняем данные доставки
        const response = await bidStore.saveDeliveryDetails(transactionId.value, deliveryData);
        
        if (response) {
          console.log('Данные доставки успешно сохранены:', response);
          
          // Обновляем данные о доставке в store
          bidStore.updateWinningDeliveryStatus(transactionId.value, deliveryData);
          
          success.value = true;
          showAlert('Данные доставки успешно сохранены!', 'success');
          
          // Обновляем список выигрышей через 2 секунды
          setTimeout(() => {
            bidStore.fetchUserWinnings();
          }, 2000);
        } else {
          error.value = bidStore.error || 'Ошибка при сохранении данных доставки';
        }
      } catch (err) {
        console.error('Ошибка при сохранении данных доставки:', err);
        error.value = err.message || 'Произошла ошибка при сохранении данных доставки';
      } finally {
        loading.value = false;
      }
    };
    
    // Функция для возврата на предыдущую страницу
    const goBack = () => {
      router.back();
    };
    
    // Функция для перехода в профиль
    const goToProfile = () => {
      router.push('/profile');
    };
    
    // Загрузка данных при монтировании компонента
    onMounted(() => {
      // Отладочное логирование
      console.log('DeliveryFormPage mounted');
      console.log('Route params:', route.params);
      console.log('Route query:', route.query);
      console.log('bidId:', bidId.value);
      console.log('lotId:', lotId.value);
      console.log('transactionId:', transactionId.value);
      
      // Проверяем localStorage при инициализации
      console.log('Данные в localStorage при инициализации страницы доставки:');
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        console.log(`${key}: ${localStorage.getItem(key)}`);
      }
      
      // Определяем сценарий работы компонента
      if (bidId.value && lotId.value) {
        // Сценарий оформления доставки - без автоматической оплаты
        console.log('Starting delivery form without payment processing...');
        
        // Предзаполняем форму данными пользователя
        if (authStore.user) {
          form.recipient_name = authStore.user.first_name && authStore.user.last_name ? 
            `${authStore.user.first_name} ${authStore.user.last_name}` : 
            authStore.user.username || '';
        }
        
        // Пытаемся найти транзакцию
        loadTransactionData();
      } else if (transactionId.value) {
        // Сценарий только оформления доставки для уже оплаченного лота
        console.log('Loading transaction data for existing transaction...');
        loadTransactionData();
      } else {
        // Нет достаточных данных
        console.log('Insufficient data for delivery processing');
        showAlert('Недостаточно данных для оформления доставки', 'error');
        router.push('/profile');
      }
    });
    
    return {
      loading,
      error,
      success,
      alertShow,
      alertMessage,
      alertType,
      transactionData,
      form,
      validation,
      formatDate,
      formatPrice,
      submitForm,
      goBack,
      goToProfile,
      hideAlert
    };
  }
}
</script>

<style scoped>
.delivery-page-container {
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

.delivery-content {
  background-color: #fff;
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  padding: 24px;
}

.lot-info {
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
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
  width: 140px;
  padding-right: 16px;
}

.value {
  color: #333;
  flex-grow: 1;
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

.form-container {
  padding: 10px 0;
}

.delivery-form {
  display: flex;
  flex-direction: column;
}

.form-group {
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}

input,
textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 16px;
  transition: border-color 0.3s;
}

input:focus,
textarea:focus {
  border-color: #007bff;
  outline: none;
}

.is-invalid {
  border-color: #dc3545;
}

.invalid-feedback {
  color: #dc3545;
  font-size: 14px;
  margin-top: 5px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}

.btn-primary,
.btn-secondary {
  padding: 10px 20px;
  border-radius: 4px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: background-color 0.3s;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-primary:hover {
  background-color: #0069d9;
}

.btn-primary:disabled {
  background-color: #6c9bd9;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background-color: #5a6268;
}

.success-message {
  text-align: center;
  padding: 16px;
}

.success-message h3 {
  color: #28a745;
  margin-bottom: 16px;
}

.success-message p {
  margin-bottom: 24px;
  color: #495057;
}

@media (max-width: 576px) {
  .delivery-page-container {
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
  
  .form-actions {
    flex-direction: column-reverse;
  }
  
  .btn-primary,
  .btn-secondary {
    width: 100%;
  }
}

.delivery-type-options {
  display: flex;
  gap: 24px;
  margin-top: 8px;
}

.delivery-option {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 8px 0;
}

.delivery-option-label {
  margin-left: 8px;
}

.pickup-info {
  background-color: #f8f9fa;
  padding: 12px 16px;
  border-radius: 4px;
  margin-top: 12px;
  border-left: 3px solid #007bff;
}

.pickup-address, .pickup-hours {
  margin: 6px 0;
  font-size: 14px;
}

.delivery-date-hint {
  font-size: 13px;
  color: #6c757d;
  margin-top: 4px;
}

input[type="date"] {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 16px;
}
</style> 