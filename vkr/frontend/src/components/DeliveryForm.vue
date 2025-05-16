<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-container">
      <div class="modal-header">
        <h2>Оформление доставки</h2>
        <button class="close-button" @click="$emit('close')">×</button>
      </div>
      
      <div class="modal-content">
        <div v-if="success" class="success-message">
          <h3>Данные доставки сохранены</h3>
          <p>Информация о доставке успешно сохранена. Вы получите уведомление, когда лот будет отправлен.</p>
          <button @click="$emit('close')" class="btn-primary">Закрыть</button>
        </div>
        
        <form v-else @submit.prevent="submitForm" class="delivery-form">
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
            <button type="button" @click="$emit('close')" class="btn-secondary">
              Отмена
            </button>
            <button type="submit" class="btn-primary" :disabled="loading">
              {{ loading ? 'Сохранение...' : 'Сохранить' }}
            </button>
          </div>
        </form>
      </div>
      
      <!-- Сообщение об ошибке -->
      <div v-if="error" class="error-message">
        {{ error }}
      </div>
    </div>
  </div>
</template>

<script>
import { reactive, ref, watch } from 'vue';
import { useBidStore } from '../store/bidStore';

export default {
  name: 'DeliveryForm',
  
  props: {
    transactionId: {
      type: [Number, String],
      required: true
    },
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
    }
  },
  
  emits: ['close', 'submit'],
  
  setup(props, { emit }) {
    const bidStore = useBidStore();
    
    // Форма данных доставки
    const form = reactive({
      recipient_name: '',
      address: '',
      phone: '',
      comments: ''
    });
    
    // Валидация формы
    const validation = reactive({
      recipient_name: '',
      address: '',
      phone: ''
    });
    
    // Загрузка существующих данных доставки (если есть)
    const loadDeliveryDetails = async () => {
      try {
        const deliveryData = await bidStore.getDeliveryDetails(props.transactionId);
        if (deliveryData) {
          form.recipient_name = deliveryData.recipient_name || '';
          form.address = deliveryData.address || '';
          form.phone = deliveryData.phone || '';
          form.comments = deliveryData.comments || '';
        }
      } catch (err) {
        console.error('Error loading delivery details:', err);
      }
    };
    
    // Загружаем данные, если есть ID транзакции
    if (props.transactionId) {
      loadDeliveryDetails();
    }
    
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
      
      // Проверка адреса
      if (!form.address.trim()) {
        validation.address = 'Адрес доставки обязателен';
        isValid = false;
      } else if (form.address.length < 10) {
        validation.address = 'Адрес должен содержать не менее 10 символов';
        isValid = false;
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
    const submitForm = () => {
      if (!validateForm()) return;
      
      emit('submit', {
        transaction: props.transactionId,
        recipient_name: form.recipient_name,
        address: form.address,
        phone: form.phone,
        comments: form.comments
      });
    };
    
    return {
      form,
      validation,
      submitForm
    };
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-container {
  background-color: #fff;
  border-radius: 8px;
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
  position: relative;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid #e9ecef;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.25rem;
  color: #333;
}

.close-button {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #6c757d;
}

.modal-content {
  padding: 24px;
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

.error-message {
  padding: 12px 24px;
  background-color: #f8d7da;
  color: #721c24;
  margin-top: 0;
  text-align: center;
  border-top: 1px solid #f5c6cb;
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
  .form-actions {
    flex-direction: column-reverse;
  }
  
  .btn-primary,
  .btn-secondary {
    width: 100%;
  }
}
</style> 