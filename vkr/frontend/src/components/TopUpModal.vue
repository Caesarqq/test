<template>
  <div class="modal" @click.self="$emit('close')">
    <div class="modal-content">
      <span class="close" @click="$emit('close')">&times;</span>
      <h3>Пополнение баланса</h3>
      
      <!-- Форма пополнения баланса -->
      <form @submit.prevent="handleSubmit" class="top-up-form">
        <div class="form-group">
          <label for="amount">Сумма пополнения (₽):</label>
          <input
            type="number"
            id="amount"
            v-model="amount"
            min="1"
            step="0.01"
            placeholder="Введите сумму"
            required
          />
        </div>
        
        <div v-if="success" class="success-message">
          Баланс успешно пополнен!
        </div>
        
        <div v-if="error" class="error-message">
          {{ error }}
        </div>
        
        <div class="form-actions">
          <button type="button" @click="$emit('close')" class="cancel-btn">
            Отмена
          </button>
          <button type="submit" class="submit-btn" :disabled="loading">
            {{ loading ? 'Обработка...' : 'Пополнить' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue';

export default {
  name: 'TopUpModal',
  
  props: {
    initialAmount: {
      type: Number,
      default: 100
    },
    loading: {
      type: Boolean,
      default: false
    },
    success: {
      type: Boolean,
      default: false
    },
    error: {
      type: String,
      default: ''
    }
  },
  
  emits: ['close', 'submit'],
  
  setup(props, { emit }) {
    const amount = ref(props.initialAmount);
    
    const handleSubmit = () => {
      // Проверяем, что сумма больше нуля
      if (amount.value <= 0) return;
      
      // Отправляем событие submit с суммой
      emit('submit', amount.value);
    };
    
    return {
      amount,
      handleSubmit
    };
  }
}
</script>

<style scoped>
.modal {
  position: fixed;
  z-index: 999;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-content {
  background-color: #fefefe;
  padding: 24px;
  border-radius: 8px;
  max-width: 400px;
  width: 90%;
  position: relative;
}

h3 {
  margin-bottom: 16px;
  color: #333;
  font-size: 1.1rem;
}

.close {
  position: absolute;
  top: 10px;
  right: 16px;
  font-size: 24px;
  cursor: pointer;
  color: #aaa;
}

.close:hover {
  color: #333;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
}

.form-group input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 16px;
}

.success-message {
  background-color: #d4edda;
  color: #155724;
  padding: 10px;
  border-radius: 6px;
  margin-bottom: 15px;
  text-align: center;
}

.error-message {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
  padding: 10px;
  border-radius: 6px;
  margin-bottom: 15px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 20px;
}

.cancel-btn {
  padding: 8px 16px;
  background-color: #f8f9fa;
  color: #6c757d;
  border: 1px solid #ced4da;
  border-radius: 4px;
  cursor: pointer;
}

.submit-btn {
  padding: 8px 16px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.submit-btn:hover {
  background-color: #0069d9;
}

.submit-btn:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}
</style> 