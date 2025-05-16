<template>
  <div class="auth-container">
    <h1>Регистрация</h1>
    
    <!-- Уведомления -->
    <AlertMessage 
      :show="authStore.registerSuccess" 
      :message="authStore.registerMessage" 
      type="success" 
      @close="authStore.resetRegisterState()" 
    />
    
    <AlertMessage 
      :show="!!authStore.error" 
      :message="authStore.error" 
      type="error" 
      @close="authStore.error = null" 
    />
    
    <!-- Форма регистрации -->
    <form class="auth-form" @submit.prevent="handleRegister">
      <div class="form-group">
        <label for="first_name">
          {{ formData.role === 'charity' ? 'Название организации' : 'Имя' }}
        </label>
        <input 
          id="first_name" 
          v-model="formData.first_name" 
          type="text" 
          :placeholder="formData.role === 'charity' ? 'Введите название организации' : 'Введите ваше имя'" 
          required 
        />
      </div>
      
      <div v-if="formData.role === 'charity'" class="form-group">
        <label for="ogrn">ОГРН</label>
        <input
          id="ogrn"
          v-model="formData.ogrn"
          type="text"
          placeholder="Введите ОГРН организации"
          required
          pattern="\d{13}"
          maxlength="13"
          minlength="13"
        />
      </div>
      <div v-else class="form-group">
        <label for="last_name">Фамилия</label>
        <input
          id="last_name"
          v-model="formData.last_name"
          type="text"
          placeholder="Введите вашу фамилию"
          required
        />
      </div>
      
      <div class="form-group">
        <label for="email">Email</label>
        <input 
          id="email" 
          v-model="formData.email" 
          type="email" 
          placeholder="Введите ваш email" 
          required 
        />
      </div>
      
      <div class="form-group">
        <label for="role">Роль</label>
        <select id="role" v-model="formData.role" required>
          <option value="buyer">Покупатель</option>
          <option value="donor">Донор</option>
          <option value="charity">Благотворительная организация</option>
        </select>
      </div>
      
      <div class="form-group">
        <label for="password">Пароль</label>
        <input 
          id="password" 
          v-model="formData.password" 
          type="password" 
          placeholder="Введите пароль" 
          required 
          minlength="8"
        />
      </div>
      
      <div class="form-group">
        <label for="password_confirm">Подтверждение пароля</label>
        <input 
          id="password_confirm" 
          v-model="formData.password_confirm" 
          type="password" 
          placeholder="Подтвердите пароль" 
          required 
          minlength="8"
        />
      </div>
      
      <button type="submit" class="submit-btn" :disabled="authStore.loading">
        {{ authStore.loading ? 'Регистрация...' : 'Зарегистрироваться' }}
      </button>
      
      <div class="auth-redirect">
        Уже есть аккаунт? <router-link to="/login">Войти</router-link>
      </div>
    </form>
  </div>
</template>

<script>
import { ref } from 'vue';
import { useAuthStore } from '../store/auth';
import AlertMessage from '../components/AlertMessage.vue';

export default {
  name: 'RegisterView',
  components: {
    AlertMessage
  },
  setup() {
    const authStore = useAuthStore();
    
    // Состояние формы
    const formData = ref({
      first_name: '',
      last_name: '',
      email: '',
      role: 'buyer', // По умолчанию покупатель
      password: '',
      password_confirm: '',
      ogrn: '',
    });
    
    // Обработчик отправки формы
    const handleRegister = async () => {
      // Валидация паролей
      if (formData.value.password !== formData.value.password_confirm) {
        authStore.error = 'Пароли не совпадают';
        return;
      }
      
      // Валидация ОГРН для charity
      if (formData.value.role === 'charity') {
        if (!/^\d{13}$/.test(formData.value.ogrn)) {
          authStore.error = 'ОГРН должен содержать ровно 13 цифр';
          return;
        }
      }
      
      // Отправка данных на сервер
      const payload = { ...formData.value };
      if (payload.role !== 'charity') {
        delete payload.ogrn;
      } else {
        delete payload.last_name;
      }
      await authStore.register(payload);
      
      // Если регистрация успешна, очищаем форму
      if (authStore.registerSuccess) {
        formData.value = {
          first_name: '',
          last_name: '',
          email: '',
          role: 'buyer',
          password: '',
          password_confirm: '',
          ogrn: '',
        };
      }
    };
    
    return {
      authStore,
      formData,
      handleRegister
    };
  }
}
</script>

<style scoped>
.auth-container { 
  max-width: 460px; 
  margin: 0 auto; 
  padding: 32px 24px;
  background-color: #fff;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.auth-container h1 {
  margin-bottom: 24px;
  text-align: center;
  color: #333;
}

.auth-form { 
  display: flex; 
  flex-direction: column; 
  gap: 16px; 
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  color: #555;
}

.auth-form input,
.auth-form select { 
  padding: 12px; 
  border: 1px solid #ddd; 
  border-radius: 6px;
  font-size: 16px;
  transition: border-color 0.2s;
}

.auth-form input:focus,
.auth-form select:focus {
  border-color: #7c4dbe;
  outline: none;
}

.submit-btn { 
  padding: 12px; 
  margin-top: 8px;
  background: #7c4dbe; 
  color: #fff; 
  border: none; 
  border-radius: 6px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.submit-btn:hover {
  background: #6b3da8;
}

.submit-btn:disabled {
  background: #a98bd0;
  cursor: not-allowed;
}

.auth-redirect {
  margin-top: 12px;
  text-align: center;
  font-size: 14px;
  color: #666;
}

.auth-redirect a {
  color: #7c4dbe;
  text-decoration: none;
  font-weight: 500;
}

.auth-redirect a:hover {
  text-decoration: underline;
}

@media (max-width: 600px) {
  .auth-container { 
    padding: 24px 16px;
    box-shadow: none;
    border-radius: 0;
  }
}
</style> 