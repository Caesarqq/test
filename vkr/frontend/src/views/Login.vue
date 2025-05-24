<template>
  <div class="auth-container">
    <h1>Вход</h1>
    <AlertMessage 
      :show="!!authStore.error" 
      :message="authStore.error" 
      type="error" 
      @close="authStore.error = null" 
    />
    <form class="auth-form" @submit.prevent="handleLogin">
      <div class="form-group">
        <label for="email">Email</label>
        <input 
          id="email" 
          v-model="credentials.email" 
          type="email" 
          placeholder="Введите ваш email" 
          required 
        />
      </div>
      
      <div class="form-group">
        <label for="password">Пароль</label>
        <input 
          id="password" 
          v-model="credentials.password" 
          type="password" 
          placeholder="Введите пароль" 
          required 
        />
      </div>
      
      <button type="submit" class="submit-btn" :disabled="authStore.loading">
        {{ authStore.loading ? 'Вход...' : 'Войти' }}
      </button>
      
      <div class="auth-redirect">
        Еще нет аккаунта? <router-link to="/register">Зарегистрироваться</router-link>
      </div>
    </form>
  </div>
</template>

<script>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../store/auth';
import AlertMessage from '../components/AlertMessage.vue';

export default {
  name: 'LoginView',
  components: {
    AlertMessage
  },
  setup() {
    const authStore = useAuthStore();
    const router = useRouter();
    const credentials = ref({
      email: '',
      password: ''
    });

    const handleLogin = async () => {
      const success = await authStore.login(credentials.value);
      if (success) {
        router.push('/profile');
      }
    };
    
    return {
      authStore,
      credentials,
      handleLogin
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

.auth-form input { 
  padding: 12px; 
  border: 1px solid #ddd; 
  border-radius: 6px;
  font-size: 16px;
  transition: border-color 0.2s;
}

.auth-form input:focus {
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