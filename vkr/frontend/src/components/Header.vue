<template>
  <header class="header">
    <div class="container header-container">
      <router-link to="/" class="logo">
        <img src="../assets/img/icon.png" alt="ДоброАукцион" class="logo-img">
        <span class="logo-text">ДоброАукцион</span>
      </router-link>
      
      <nav class="main-nav" :class="{ 'active': mobileMenuOpen }">
        <ul class="nav-list">
          <li><router-link to="/auctions">Аукционы</router-link></li>
          <li><router-link to="/charity">Благотворительность</router-link></li>
          <li><router-link to="/stories">Истории</router-link></li>
          <li><router-link to="/about">О нас</router-link></li>
          <li><router-link to="/contacts">Контакты</router-link></li>
        </ul>
      </nav>
      
      <div class="auth-buttons" v-if="!authStore.isAuthenticated">
        <router-link to="/login" class="login-btn">Войти</router-link>
        <router-link to="/register" class="register-btn">Регистрация</router-link>
      </div>

      <div class="user-profile" v-else>
        <div class="profile-dropdown">
          <button class="profile-btn" @click="toggleProfileMenu">
            {{ authStore.userName }}
            <span class="profile-arrow" :class="{ 'active': profileMenuOpen }">▼</span>
          </button>
          
          <div class="profile-menu" v-if="profileMenuOpen">
            <router-link to="/profile" class="profile-link">Личный кабинет</router-link>
            <button class="logout-link" @click="logout">Выйти</button>
          </div>
        </div>
      </div>
      
      <button class="mobile-menu-toggle" @click="toggleMobileMenu">
        <span></span>
        <span></span>
        <span></span>
      </button>
    </div>
  </header>
</template>

<script>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../store/auth';

export default {
  name: 'Header',
  setup() {
    const authStore = useAuthStore();
    const router = useRouter();
    const mobileMenuOpen = ref(false);
    const profileMenuOpen = ref(false);

    const toggleMobileMenu = () => {
      mobileMenuOpen.value = !mobileMenuOpen.value;
      if (mobileMenuOpen.value && profileMenuOpen.value) {
        profileMenuOpen.value = false;
      }
    };

    const toggleProfileMenu = () => {
      profileMenuOpen.value = !profileMenuOpen.value;
    };

    const logout = () => {
      authStore.logout();
      profileMenuOpen.value = false;
      router.push('/');
    };

    const closeProfileMenu = (event) => {
      if (profileMenuOpen.value && !event.target.closest('.profile-dropdown')) {
        profileMenuOpen.value = false;
      }
    };

    if (typeof window !== 'undefined') {
      window.addEventListener('click', closeProfileMenu);
    }
    
    return {
      authStore,
      mobileMenuOpen,
      profileMenuOpen,
      toggleMobileMenu,
      toggleProfileMenu,
      logout
    };
  }
}
</script>

<style scoped>
.header {
  background-color: white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
  padding: 15px 0;
}

.header-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  display: flex;
  align-items: center;
  text-decoration: none;
  color: var(--primary-color);
  font-weight: 700;
  font-size: 20px;
}

.logo-img {
  width: 32px;
  height: 32px;
  margin-right: 10px;
  object-fit: contain;
}

.nav-list {
  display: flex;
  list-style: none;
  gap: 25px;
}

.nav-list a {
  text-decoration: none;
  color: var(--text-color);
  font-weight: 500;
  transition: color 0.2s;
}

.nav-list a:hover,
.nav-list a.router-link-active {
  color: var(--primary-color);
}

.auth-buttons {
  display: flex;
  align-items: center;
  gap: 15px;
}

.login-btn {
  text-decoration: none;
  color: var(--primary-color);
  font-weight: 500;
}

.register-btn {
  padding: 8px 16px;
  background-color: var(--primary-color);
  color: white;
  border-radius: var(--border-radius);
  text-decoration: none;
  font-weight: 500;
}

.user-profile {
  position: relative;
}

.profile-dropdown {
  position: relative;
}

.profile-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  background: transparent;
  border: none;
  font-weight: 500;
  color: var(--text-color);
  cursor: pointer;
  padding: 8px 12px;
  border-radius: var(--border-radius);
}

.profile-btn:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.profile-arrow {
  font-size: 10px;
  transition: transform 0.3s;
}

.profile-arrow.active {
  transform: rotate(180deg);
}

.profile-menu {
  position: absolute;
  top: 100%;
  right: 0;
  background-color: #efefef;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  border-radius: var(--border-radius);
  padding: 10px 0;
  margin-top: 5px;
  min-width: 180px;
  z-index: 10;
}

.profile-link,
.logout-link {
  display: block;
  width: 100%;
  text-align: left;
  padding: 8px 16px;
  text-decoration: none;
  color: var(--text-color);
  background: transparent;
  border: none;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
}

.profile-link:hover,
.logout-link:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.logout-link {
  color: #dc3545;
}

.mobile-menu-toggle {
  display: none;
  flex-direction: column;
  justify-content: space-between;
  width: 30px;
  height: 21px;
  background: transparent;
  border: none;
  cursor: pointer;
}

.mobile-menu-toggle span {
  display: block;
  height: 3px;
  width: 100%;
  background-color: var(--primary-color);
  border-radius: 3px;
}

@media (max-width: 992px) {
  .main-nav {
    position: fixed;
    top: 66px;
    left: 0;
    right: 0;
    background: white;
    height: 0;
    overflow: hidden;
    transition: height 0.3s ease;
    box-shadow: 0 5px 10px rgba(0, 0, 0, 0.1);
  }
  
  .main-nav.active {
    height: auto;
    padding: 20px 0;
  }
  
  .nav-list {
    flex-direction: column;
    align-items: center;
    gap: 15px;
  }
  
  .mobile-menu-toggle {
    display: flex;
  }
}

@media (max-width: 768px) {
  .auth-buttons,
  .user-profile {
    display: none;
  }
  
  .main-nav.active .nav-list {
    padding-bottom: 15px;
  }
  
  .main-nav.active .nav-list::after {
    content: '';
    display: flex;
    margin-top: 15px;
    width: 80%;
    height: 1px;
    background-color: #eee;
  }
  
  .main-nav.active::after {
    content: '';
    display: flex;
    justify-content: center;
    gap: 15px;
    padding: 0 20px;
  }
  
  .logo-text {
    display: none;
  }
}

@media (min-width: 769px) and (max-width: 992px) {
  .auth-buttons,
  .user-profile {
    display: none;
  }
  
  .main-nav.active {
    display: flex;
    flex-direction: column;
  }
  
  .main-nav.active::after {
    content: '';
    display: flex;
    justify-content: center;
    gap: 15px;
    margin-top: 15px;
  }
}
</style>