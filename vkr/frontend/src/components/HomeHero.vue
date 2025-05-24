<template>
  <section class="hero">
    <div class="hero-content">
      <h1 class="hero-title">Вместе мы можем больше</h1>
      <p class="hero-subtitle">
        Приобретайте уникальные лоты и помогайте тем, кто нуждается в вашей
        поддержке. Каждая ставка - это шаг к лучшему миру.
      </p>
      <router-link to="/auctions" class="btn hero-cta">Участвовать сейчас</router-link>
    </div>
    
    <div class="stats-container">
      <div class="stats-card">
        <div class="stats-row">
          <div class="stat-item">
            <div class="stat-value">7 777 777 ₽</div>
            <div class="stat-label">собрано средств</div>
            <div class="progress-bar">
              <div class="progress" style="width: 70%"></div>
            </div>
          </div>
          
          <div class="stat-item">
            <div class="stat-value">99</div>
            <div class="stat-label">реализованных проекта</div>
          </div>
          
          <div class="stat-item">
            <div class="stat-value">1337</div>
            <div class="stat-label">участников</div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'HomeHero'
}
</script>

<style scoped>
.hero {
  background-color: white;
  background-image: linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)), url('/src/assets/img/backheart.svg');
  background-size: cover;
  background-position: center;
  color: white;
  padding: 80px 0 0;
  text-align: center;
  position: relative;
  height: 100vh;
}

.hero-content {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 20px;
}

.hero-title {
  font-size: 3rem;
  margin-bottom: 20px;
  font-weight: 700;
}

.hero-subtitle {
  font-size: 1.2rem;
  margin-bottom: 30px;
  line-height: 1.6;
}

.hero-cta {
  font-size: 1.1rem;
  padding: 14px 30px;
}

.stats-container {
  width: 100%;
  max-width: 1000px;
  margin: 50px auto -40px;
  padding: 0 20px;
  position: relative;
  z-index: 2;
}

.stats-card {
  background: white;
  border-radius: var(--border-radius);
  box-shadow: var(--box-shadow);
  padding: 30px;
}

.stats-row {
  display: flex;
  justify-content: space-around;
}

.stat-item {
  text-align: center;
  color: var(--text-color);
}

.stat-value {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--primary-color);
  margin-bottom: 5px;
}

.stat-label {
  font-size: 1rem;
  color: #777;
}

.progress-bar {
  height: 6px;
  background-color: #eee;
  border-radius: 3px;
  width: 100%;
  margin-top: 15px;
}

.progress {
  height: 100%;
  background-color: var(--secondary-color);
  border-radius: 3px;
}

@media (max-width: 992px) {
  .hero-title {
    font-size: 2.5rem;
  }
  
  .stat-value {
    font-size: 2rem;
  }
}

@media (max-width: 768px) {
  .hero {
    padding: 60px 0 40px;
  }
  
  .hero-title {
    font-size: 2rem;
  }
  
  .hero-subtitle {
    font-size: 1rem;
  }
  
  .stats-row {
    flex-direction: column;
    gap: 30px;
  }
  
  .stat-item {
    margin-bottom: 15px;
  }
}

@media (max-width: 480px) {
  .hero-title {
    font-size: 1.8rem;
  }
  
  .stats-card {
    padding: 20px 15px;
  }
}
</style>