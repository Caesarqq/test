<template>
  <div class="winning-card" :class="`winning-card--${winning.status}`">
    <div class="winning-card__header">
      <div class="winning-card__title-wrapper">
        <router-link :to="{ name: 'lot', params: { id: winning.lot } }" class="winning-card__title">
          {{ winning.lot_title || `Лот №${winning.lot}` }}
        </router-link>
        <span class="winning-card__badge" :class="`badge-${winning.status}`">
          {{ getStatusText(winning.status) }}
        </span>
        <span v-if="winning.delivery_status" class="winning-card__badge badge-delivery" :class="`badge-delivery-${winning.delivery_status}`">
          {{ getDeliveryStatusText(winning.delivery_status) }}
        </span>
      </div>
      <span class="winning-card__amount">{{ formatPrice(winning.amount) }}</span>
    </div>
    
    <div class="winning-card__content">
      <div class="winning-card__detail">
        <span class="winning-card__label">Дата оплаты:</span>
        <span class="winning-card__value">{{ formatDate(winning.payment_time) }}</span>
      </div>
      
      <div v-if="winning.payment_method" class="winning-card__detail">
        <span class="winning-card__label">Способ оплаты:</span>
        <span class="winning-card__value">{{ getPaymentMethodText(winning.payment_method) }}</span>
      </div>
      
      <!-- Информация о доставке, если она оформлена -->
      <div v-if="hasDeliveryDetails" class="winning-card__detail">
        <span class="winning-card__label">Тип доставки:</span>
        <span class="winning-card__value">{{ getDeliveryTypeText(winning.delivery.delivery_type) }}</span>
      </div>
      
      <div v-if="hasDeliveryDetails" class="winning-card__detail">
        <span class="winning-card__label">Дата доставки:</span>
        <span class="winning-card__value">{{ formatDate(winning.delivery.delivery_date) }}</span>
      </div>
      
      <div v-if="hasDeliveryDetails && winning.delivery.delivery_type === 'courier'" class="winning-card__detail">
        <span class="winning-card__label">Адрес доставки:</span>
        <span class="winning-card__value">{{ winning.delivery.address }}</span>
      </div>
      
      <div v-if="hasDeliveryDetails && winning.delivery.delivery_type === 'pickup'" class="winning-card__detail">
        <span class="winning-card__label">Самовывоз:</span>
        <span class="winning-card__value">{{ winning.delivery.address || 'г. Москва, ул. Примерная, д. 123' }}</span>
      </div>
    </div>
    
    <div class="winning-card__footer">
      <!-- Кнопка оплаты - показывается, если статус "pending" -->
      <button 
        v-if="winning.status === 'pending'" 
        @click="$emit('pay', winning)" 
        class="btn-primary"
        :disabled="loading"
      >
        {{ loading ? 'Оплата...' : 'Оплатить' }}
      </button>
      
      <!-- Кнопка оформления доставки - показывается после оплаты если доставка не оформлена -->
      <router-link 
        v-if="winning.status === 'completed' && !hasDeliveryDetails" 
        :to="{ name: 'delivery', params: { id: winning.id } }" 
        class="btn-info"
      >
        Оформить доставку
      </router-link>
      
      <!-- Кнопка подтверждения получения - показывается, если статус доставки "shipped" -->
      <button 
        v-if="winning.delivery_status === 'shipped'" 
        @click="$emit('confirm-delivery', winning)" 
        class="btn-success"
        :disabled="loading"
      >
        {{ loading ? 'Обработка...' : 'Подтвердить получение' }}
      </button>
      
      <!-- Кнопка просмотра лота -->
      <button class="btn-view-lot">
        <router-link :to="{ name: 'lot', params: { id: winning.lot } }" class="link-no-style">
          Посмотреть лот
        </router-link>
      </button>
      
      <!-- Кнопка просмотра деталей -->
      <!-- <button @click="$emit('view-details', winning)" class="btn-view-details">
        Детали
      </button> -->
    </div>
  </div>
</template>

<script>
export default {
  name: 'WinningCard',
  props: {
    winning: {
      type: Object,
      required: true
    },
    formatPrice: {
      type: Function,
      required: true
    },
    formatDate: {
      type: Function,
      required: true
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    // Проверяем, есть ли данные о доставке
    hasDeliveryDetails() {
      return this.winning.delivery && typeof this.winning.delivery === 'object';
    }
  },
  emits: ['view-details', 'pay', 'setup-delivery', 'confirm-delivery'],
  methods: {
    getStatusText(status) {
      const statuses = {
        'pending': 'Ожидает оплаты',
        'completed': 'Оплачен',
        'failed': 'Ошибка'
      };
      
      return statuses[status] || status;
    },
    getPaymentMethodText(method) {
      const methods = {
        'balance': 'Баланс',
        'card': 'Банковская карта',
        'transfer': 'Перевод',
        'cash': 'Наличные'
      };
      
      return methods[method] || method;
    },
    getDeliveryStatusText(status) {
      const statuses = {
        'pending': 'Ожидает отправки',
        'shipped': 'Отправлен',
        'delivered': 'Доставлен',
        'failed': 'Ошибка доставки'
      };
      
      return statuses[status] || status;
    },
    getDeliveryTypeText(type) {
      const types = {
        'courier': 'Курьерская доставка',
        'pickup': 'Самовывоз'
      };
      
      return types[type] || type;
    },
    getDeliveryText(delivery) {
      if (typeof delivery === 'object') {
        const deliveryType = this.getDeliveryTypeText(delivery.delivery_type);
        const deliveryDate = this.formatDate(delivery.delivery_date);
        return `${deliveryType}, ${deliveryDate}`;
      } else if (delivery === true) {
        return 'Оформлена';
      } else {
        return 'Не оформлена';
      }
    }
  }
}
</script>

<style scoped>
.winning-card {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 16px;
  margin-bottom: 16px;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  background-color: #fff;
  border-left: 4px solid #e9ecef;
}

.winning-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.winning-card--completed {
  border-left-color: #28a745;
}

.winning-card--pending {
  border-left-color: #ffc107;
}

.winning-card--failed {
  border-left-color: #dc3545;
}

.winning-card__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.winning-card__title-wrapper {
  display: flex;
  flex-direction: column;
}

.winning-card__title {
  font-weight: 600;
  font-size: 1.1rem;
  color: #2c3e50;
  text-decoration: none;
  margin-bottom: 6px;
}

.winning-card__title:hover {
  color: #007bff;
  text-decoration: underline;
}

.winning-card__badge {
  font-size: 0.75rem;
  padding: 2px 8px;
  border-radius: 12px;
  display: inline-block;
  align-self: flex-start;
  margin-bottom: 4px;
}

.badge-completed {
  background-color: #d4edda;
  color: #155724;
}

.badge-pending {
  background-color: #fff3cd;
  color: #856404;
}

.badge-failed {
  background-color: #f8d7da;
  color: #721c24;
}

.badge-delivery {
  margin-left: 6px;
}

.badge-delivery-shipped {
  background-color: #d1ecf1;
  color: #0c5460;
}

.badge-delivery-delivered {
  background-color: #d1e7dd;
  color: #0f5132;
}

.badge-delivery-pending {
  background-color: #e2e3e5;
  color: #383d41;
}

.badge-delivery-failed {
  background-color: #f8d7da;
  color: #721c24;
}

.winning-card__amount {
  font-weight: 700;
  font-size: 1.2rem;
  color: #28a745;
}

.winning-card__content {
  margin-bottom: 16px;
}

.winning-card__detail {
  display: flex;
  margin-bottom: 6px;
}

.winning-card__label {
  font-weight: 500;
  color: #6c757d;
  min-width: 140px;
  margin-right: 12px;
}

.winning-card__value {
  color: #212529;
}

.winning-card__footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  flex-wrap: wrap;
}

.btn-primary,
.btn-info,
.btn-success,
.btn-view-details,
.btn-view-lot {
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  text-align: center;
  border: none;
  transition: background-color 0.2s ease;
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

.btn-info {
  background-color: #7950c1;
  color: white;
}

.btn-info:hover {
  background-color: #ff7b54;
}

.btn-info:disabled {
  background-color: black;
  cursor: not-allowed;
}

.btn-success {
  background-color: #28a745;
  color: white;
}

.btn-success:hover {
  background-color: #218838;
}

.btn-success:disabled {
  background-color: #86c895;
  cursor: not-allowed;
}

.btn-view-details {
  background-color: #6c757d;
  color: white;
}

.btn-view-details:hover {
  background-color: #5a6268;
}

.btn-view-lot {
  background-color: #6c757d;
  color: white;
}

.btn-view-lot:hover {
  background-color: #5a6268;
}

.link-no-style {
  color: inherit;
  text-decoration: none;
}

@media (max-width: 576px) {
  .winning-card__header {
    flex-direction: column;
  }
  
  .winning-card__amount {
    margin-top: 8px;
  }
  
  .winning-card__footer {
    flex-direction: column;
  }
  
  .btn-primary,
  .btn-info,
  .btn-success,
  .btn-view-details,
  .btn-view-lot {
    width: 100%;
  }
}
</style> 