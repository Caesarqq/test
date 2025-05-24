<template>
    <div class="modal-overlay" @click.self="close">
      <div class="modal-content">
        <div class="modal-header">
          <h2>Оформление подписки</h2>
          <button class="close-btn" @click="close">×</button>
        </div>
        
        <div class="modal-body">
          <div class="subscription-info">
            <h3>Премиум подписка</h3>
            <p>Получите доступ ко всем платным аукционам на 1 месяц</p>
            
            <div class="subscription-features">
              <div class="feature">
                <span class="feature-icon">✓</span>
                <span class="feature-text">Неограниченный доступ к платным аукционам</span>
              </div>
              <div class="feature">
                <span class="feature-icon">✓</span>
                <span class="feature-text">Без необходимости покупать билеты</span>
              </div>
              <div class="feature">
                <span class="feature-icon">✓</span>
                <span class="feature-text">Автоматическое продление</span>
              </div>
            </div>
            
            <div class="subscription-price">
              <span class="price">{{ formatPrice(subscriptionPrice) }}</span>
              <span class="period">/ месяц</span>
            </div>
          </div>
          
          <!-- Ошибка -->
          <div v-if="error" class="error-message">
            {{ error }}
          </div>
          
          <!-- Успех -->
          <div v-if="success" class="success-message">
            <div class="success-icon">✓</div>
            <h3>Подписка оформлена!</h3>
            <p>Теперь у вас есть доступ ко всем платным аукционам до {{ formatEndDate(subscriptionEndDate) }}</p>
          </div>
          
          <!-- Способ оплаты -->
          <div v-if="!success" class="payment-method">
            <h3>Способ оплаты</h3>
            <div class="payment-options">
              <label class="payment-option">
                <input type="radio" v-model="paymentMethod" value="balance" :disabled="insufficientFunds" />
                <span class="option-label">Баланс</span>
                <span v-if="balanceAmount !== null" class="balance-amount">
                  (Доступно: {{ formatPrice(balanceAmount) }})
                </span>
                <span v-if="insufficientFunds" class="error-hint">
                  Недостаточно средств
                </span>
              </label>
              <label class="payment-option">
                <input type="radio" v-model="paymentMethod" value="card" />
                <span class="option-label">Банковская карта</span>
              </label>
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button v-if="!success" @click="close" class="btn-secondary">Отмена</button>
          <button 
            v-if="!success" 
            @click="subscribe" 
            class="btn-primary" 
            :disabled="loading || insufficientFunds && paymentMethod === 'balance'">
            {{ loading ? 'Оформление...' : 'Оформить подписку' }}
          </button>
          <button v-if="success" @click="close" class="btn-primary">Закрыть</button>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'SubscriptionModal',
    
    props: {
      loading: {
        type: Boolean,
        default: false
      },
      error: {
        type: String,
        default: ''
      },
      success: {
        type: Boolean,
        default: false
      },
      balanceAmount: {
        type: Number,
        default: null
      },
      subscriptionPrice: {
        type: Number,
        default: 599
      },
      subscriptionEndDate: {
        type: String,
        default: null
      }
    },
    
    data() {
      return {
        paymentMethod: 'balance'
      };
    },
    
    computed: {
      insufficientFunds() {
        return this.balanceAmount !== null && this.balanceAmount < this.subscriptionPrice;
      }
    },
    
    mounted() {
      // Если недостаточно средств для оплаты с баланса, выбираем оплату картой по умолчанию
      if (this.insufficientFunds) {
        this.paymentMethod = 'card';
      }
      
      // Блокируем прокрутку страницы
      document.body.style.overflow = 'hidden';
    },
    
    beforeUnmount() {
      // Разблокируем прокрутку страницы
      document.body.style.overflow = 'auto';
    },
    
    methods: {
      close() {
        this.$emit('close');
      },
      
      subscribe() {
        this.$emit('subscribe', {
          paymentMethod: this.paymentMethod
        });
      },
      
      formatPrice(price) {
        return new Intl.NumberFormat('ru-RU', {
          style: 'currency',
          currency: 'RUB',
          minimumFractionDigits: 0
        }).format(price);
      },
      
      formatEndDate(dateString) {
        if (!dateString) return '';
        
        const date = new Date(dateString);
        return new Intl.DateTimeFormat('ru-RU', {
          day: '2-digit',
          month: 'long',
          year: 'numeric'
        }).format(date);
      }
    }
  };
  </script>
  
  <style scoped>
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
    z-index: 1000;
  }
  
  .modal-content {
    background-color: white;
    border-radius: 8px;
    width: 500px;
    max-width: 90vw;
    max-height: 90vh;
    overflow-y: auto;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  }
  
  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 20px;
    border-bottom: 1px solid #eee;
  }
  
  .modal-header h2 {
    margin: 0;
    font-size: 1.4rem;
    color: #333;
  }
  
  .close-btn {
    background: none;
    border: none;
    font-size: 24px;
    color: #999;
    cursor: pointer;
  }
  
  .close-btn:hover {
    color: #555;
  }
  
  .modal-body {
    padding: 20px;
  }
  
  .subscription-info {
    margin-bottom: 24px;
    padding: 16px;
    background-color: #f8f9fa;
    border-radius: 8px;
    text-align: center;
  }
  
  .subscription-info h3 {
    margin-top: 0;
    margin-bottom: 12px;
    color: #333;
    font-size: 1.3rem;
  }
  
  .subscription-info p {
    margin-bottom: 16px;
    color: #555;
  }
  
  .subscription-features {
    margin-bottom: 20px;
    text-align: left;
  }
  
  .feature {
    display: flex;
    align-items: center;
    margin-bottom: 8px;
  }
  
  .feature-icon {
    color: #28a745;
    font-weight: bold;
    margin-right: 10px;
  }
  
  .feature-text {
    color: #444;
  }
  
  .subscription-price {
    margin-top: 20px;
    font-size: 1.8rem;
    font-weight: bold;
    color: #007bff;
  }
  
  .subscription-price .period {
    font-size: 1rem;
    color: #777;
    font-weight: normal;
  }
  
  .payment-method {
    margin-top: 20px;
  }
  
  .payment-method h3 {
    margin-bottom: 16px;
    font-size: 1.1rem;
    color: #555;
  }
  
  .payment-options {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
  
  .payment-option {
    display: flex;
    align-items: center;
    cursor: pointer;
    padding: 12px;
    border: 1px solid #ddd;
    border-radius: 6px;
    transition: border-color 0.2s, background-color 0.2s;
  }
  
  .payment-option:hover {
    border-color: #aad;
    background-color: #f9f9ff;
  }
  
  .payment-option input {
    margin-right: 12px;
  }
  
  .option-label {
    font-weight: 500;
    color: #333;
  }
  
  .balance-amount {
    margin-left: 8px;
    color: #666;
    font-size: 0.9rem;
  }
  
  .error-hint {
    margin-left: auto;
    color: #dc3545;
    font-size: 0.85rem;
  }
  
  .modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    padding: 16px 20px;
    border-top: 1px solid #eee;
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
  
  .btn-primary:hover:not(:disabled) {
    background-color: #0069d9;
  }
  
  .btn-primary:disabled {
    background-color: #b3d7ff;
    cursor: not-allowed;
  }
  
  .btn-secondary {
    background-color: #6c757d;
    color: white;
  }
  
  .btn-secondary:hover {
    background-color: #5a6268;
  }
  
  .error-message {
    background-color: #f8d7da;
    color: #721c24;
    padding: 12px;
    border-radius: 4px;
    margin-bottom: 20px;
  }
  
  .success-message {
    text-align: center;
    padding: 24px 16px;
  }
  
  .success-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 60px;
    height: 60px;
    background-color: #d4edda;
    color: #155724;
    font-size: 32px;
    border-radius: 50%;
    margin: 0 auto 16px;
  }
  
  .success-message h3 {
    color: #155724;
    margin-bottom: 8px;
  }
  
  .success-message p {
    color: #444;
  }
  
  @media (max-width: 576px) {
    .modal-content {
      width: 95vw;
    }
    
    .subscription-price {
      font-size: 1.5rem;
    }
    
    .payment-option {
      flex-wrap: wrap;
    }
    
    .error-hint {
      margin-left: 30px;
      margin-top: 4px;
    }
  }
  </style>