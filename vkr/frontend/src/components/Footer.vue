<template>
  <footer class="footer">
    <div class="container">
      <div class="footer-content">
        <div class="footer-logo">
          <router-link to="/" class="logo">
            <span class="logo-icon">
              <img src="../assets/img/icon.png" alt="ДоброАукцион" class="logo-img">
            </span>
            <span class="logo-text">ДоброАукцион</span>
          </router-link>
          <p class="footer-slogan">Вместе делаем мир лучше</p>
        </div>
        
        <div class="footer-links">
          <div class="footer-column">
            <h3 class="footer-heading">Навигация</h3>
            <ul>
              <li><router-link to="/">Главная</router-link></li>
              <li><router-link to="/auctions">Аукционы</router-link></li>
              <li><router-link to="/charity">Благотворительность</router-link></li>
              <li><router-link to="/stories">Истории</router-link></li>
            </ul>
          </div>
          
          <div class="footer-column">
            <h3 class="footer-heading">Информация</h3>
            <ul>
              <li><router-link to="/about">О нас</router-link></li>
              <li><router-link to="/faq">FAQ</router-link></li>
              <li><router-link to="/terms">Правила</router-link></li>
              <li><router-link to="/privacy">Конфиденциальность</router-link></li>
            </ul>
          </div>
          
          <div class="footer-column">
            <h3 class="footer-heading">Контакты</h3>
            <ul>
              <li><a href="mailto:info@dobroauction.ru">info@dobroauction.ru</a></li>
              <li><a href="tel:+78001234567">8 (800) 123-45-67</a></li>
              <li class="social-icons">
                <a href="#" class="social-icon">YT</a>
                <a href="#" class="social-icon">VK</a>
                <a href="#" class="social-icon">TG</a>
              </li>
            </ul>
          </div>
        </div>
      </div>
      
      <div class="footer-bottom">
        <p>&copy; 2025 ДоброАукцион. Все права защищены.</p>
      </div>
    </div>
  </footer>
</template>

<script>
export default {
  name: 'Footer'
}
</script>

<style scoped>
.footer {
  background-color: #f8f8f8;
  padding: 60px 0 30px;
}

.footer-content {
  display: flex;
  flex-wrap: wrap;
  gap: 40px;
  margin-bottom: 40px;
}

.footer-logo {
  flex: 1;
  min-width: 250px;
}

.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 10px;
}
.logo-text{
  color: var(--primary-color);
  font-weight: 700;
}
.footer-slogan {
  color: #777;
  margin-top: 10px;
  margin-left: 110px;
}

.footer-links {
  flex: 2;
  display: flex;
  flex-wrap: wrap;
  gap: 30px;
}

.footer-column {
  flex: 1;
  min-width: 150px;
}

.footer-heading {
  font-size: 1.1rem;
  color: var(--primary-color);
  margin-bottom: 15px;
  font-weight: 600;
}

.footer-column ul {
  list-style: none;
  padding: 0;
}

.footer-column li {
  margin-bottom: 10px;
}

.footer-column a {
  text-decoration: none;
  color: #555;
  transition: color 0.2s;
}

.footer-column a:hover {
  color: var(--primary-color);
}

.social-icons {
  display: flex;
  gap: 10px;
}

.social-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background-color: #eee;
  border-radius: 50%;
  color: #555;
  transition: all 0.2s;
}
/* 
.social-icon:hover {
  background-color: var(--primary-color);
  color: white;
} */

.footer-bottom {
  border-top: 1px solid #a7a7a7;
  padding-top: 20px;
  text-align: center;
  color: #777;
  font-size: 0.9rem;
}

@media (max-width: 992px) {
  .footer-content {
    flex-direction: column;
    gap: 30px;
  }
  
  .footer-links {
    width: 100%;
  }
}

@media (max-width: 768px) {
  .footer {
    padding: 40px 0 20px;
    margin-top: 40px;
  }
  
  .footer-links {
    flex-direction: column;
    gap: 20px;
  }
  
  .footer-column {
    width: 100%;
  }
} 

.logo-icon {
  /* background-color: var(--primary-color);
  color: white; */
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.logo-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
</style>