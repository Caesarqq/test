import { defineStore } from 'pinia';
import { jwtDecode } from 'jwt-decode';
import authApi from '../api/authApi';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    // Токены
    accessToken: localStorage.getItem('access_token') || null,
    refreshToken: localStorage.getItem('refresh_token') || null,
    
    // Информация о пользователе
    user: null,
    userCharity: null,
    
    // Состояние загрузки и ошибок
    loading: false,
    error: null,
    
    // Состояние регистрации
    registerSuccess: false,
    registerMessage: ''
  }),
  
  getters: {
    // Проверка авторизации пользователя
    isAuthenticated: (state) => !!state.accessToken,
    
    // Получение данных из токена
    tokenData: (state) => {
      if (!state.accessToken) return null;
      try {
        return jwtDecode(state.accessToken);
      } catch (error) {
        return null;
      }
    },
    
    // Получение роли пользователя
    userRole: (state) => state.user?.role || null,
    
    // Получение имени пользователя для отображения
    userName: (state) => {
      if (!state.user) return '';
      return state.user.first_name || state.user.email.split('@')[0];
    },
    
    // Проверка, является ли токен просроченным
    isTokenExpired: (state, getters) => {
      const tokenData = getters.tokenData;
      if (!tokenData) return true;
      
      const expirationTime = tokenData.exp * 1000; // в миллисекундах
      const currentTime = Date.now();
      
      return currentTime >= expirationTime;
    }
  },
  
  actions: {
    // Инициализация состояния при загрузке приложения
    async init() {
      if (this.accessToken) {
        await this.fetchUserProfile();
        
        // Если пользователь с ролью charity, получаем информацию о его организации
        if (this.user?.role === 'charity') {
          await this.fetchUserCharity();
        }
      }
    },
    
    // Регистрация пользователя
    async register(userData) {
      this.loading = true;
      this.error = null;
      this.registerSuccess = false;
      this.registerMessage = '';
      
      try {
        const response = await authApi.register(userData);
        this.registerSuccess = true;
        this.registerMessage = response.data.message || 'Регистрация успешна! Проверьте вашу почту для подтверждения аккаунта.';
        return true;
      } catch (error) {
        this.error = error.response?.data?.detail || 'Ошибка при регистрации';
        console.error('Registration error:', error);
        return false;
      } finally {
        this.loading = false;
      }
    },
    
    // Авторизация пользователя
    async login(credentials) {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await authApi.login(credentials);
        
        // Сохраняем токены
        const { access, refresh } = response.data;
        this.accessToken = access;
        this.refreshToken = refresh;
        
        // Сохраняем токены в localStorage
        localStorage.setItem('access_token', access);
        localStorage.setItem('refresh_token', refresh);
        
        // Получаем информацию о пользователе
        await this.fetchUserProfile();
        
        // Если пользователь с ролью charity, получаем информацию о его организации
        if (this.user?.role === 'charity') {
          await this.fetchUserCharity();
        }
        
        return true;
      } catch (error) {
        this.error = error.response?.data?.detail || 'Неверный логин или пароль';
        console.error('Login error:', error);
        return false;
      } finally {
        this.loading = false;
      }
    },
    
    // Получение информации о пользователе
    async fetchUserProfile() {
      if (!this.accessToken) return;
      
      this.loading = true;
      
      try {
        const response = await authApi.getProfile();
        this.user = response.data;
        console.log('Получен профиль пользователя:', this.user);
        
        // Если пользователь с ролью charity, получаем информацию о его организации
        if (this.user?.role === 'charity') {
          await this.fetchUserCharity();
        }
      } catch (error) {
        console.error('Error fetching user profile:', error);
        
        // Если при получении профиля произошла ошибка авторизации,
        // и токен не удалось обновить, выполняем выход
        if (error.response?.status === 401) {
          this.logout();
        }
      } finally {
        this.loading = false;
      }
    },
    
    // Получение информации о благотворительной организации пользователя
    async fetchUserCharity() {
      if (!this.accessToken || this.user?.role !== 'charity') return;
      
      this.loading = true;
      
      try {
        console.log('Запрос данных о charity пользователя...');
        const response = await authApi.getUserCharity();
        this.userCharity = response.data;
        console.log('Получены данные организации:', this.userCharity);
        
        // Обновляем данные пользователя, добавляя информацию о charity
        if (this.user && this.userCharity) {
          this.user.charity = this.userCharity;
          console.log('Обновлены данные пользователя с charity:', this.user);
        }
        
        return this.userCharity;
      } catch (error) {
        console.error('Error fetching user charity:', error);
        
        // Проверяем, существует ли уже организация для этого пользователя
        try {
          // Запрашиваем список всех организаций
          const charitiesResponse = await authApi.getCharities();
          const charities = charitiesResponse.data;
          
          if (charities && Array.isArray(charities)) {
            // Ищем организацию, связанную с текущим пользователем
            const userCharity = charities.find(c => c.user && c.user.id === this.user.id);
            
            if (userCharity) {
              this.userCharity = userCharity;
              this.user.charity = userCharity;
              console.log('Найдена организация из общего списка:', userCharity);
              return userCharity;
            }
          }
        } catch (err) {
          console.error('Error fetching charities list:', err);
        }
        
        return null;
      } finally {
        this.loading = false;
      }
    },
    
    // Выход из системы
    logout() {
      this.accessToken = null;
      this.refreshToken = null;
      this.user = null;
      this.userCharity = null;
      
      // Удаляем токены из localStorage
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    },
    
    // Обновление состояния хранилища при обновлении токена из interceptor
    updateTokens(accessToken, refreshToken = null) {
      this.accessToken = accessToken;
      
      if (refreshToken) {
        this.refreshToken = refreshToken;
        localStorage.setItem('refresh_token', refreshToken);
      }
      
      localStorage.setItem('access_token', accessToken);
    },
    
    // Сброс состояния регистрации
    resetRegisterState() {
      this.registerSuccess = false;
      this.registerMessage = '';
    }
  }
}); 