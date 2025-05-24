<template>
  <div class="home">
    <section class="auctions-section">
      <div class="container">
        <div class="section-grid">
          <div class="winners-column">
            <div class="winners-card">
              <h2 class="section-title">
                <span class="trophy-icon">🏆</span> Победители аукционов
              </h2>
              <div class="winners-list">
                <div class="winner-item" v-for="(winner, index) in winners" :key="index">
                  <div class="winner-number">{{ index + 1 }}</div>
                  <div class="winner-avatar">
                    <img src="../assets/img/icon.png" alt="Аватар" />
                  </div>
                  <div class="winner-info">
                    <div class="winner-name">{{ winner.name }}</div>
                    <div class="winner-lot">{{ winner.lot }}</div>
                  </div>
                  <div class="winner-amount">{{ winner.amount }} ₽</div>
                </div>
              </div>
            </div>
            
            <div class="premium-promo-card">
            <h2 class="section-title">
              <span class="crown-icon">👑</span> Премиум доступ
            </h2>
            <div class="premium-content">
              <div class="premium-header">
                <h3>Откройте для себя эксклюзивные аукционы</h3>
                <p>Участвуйте в торгах за уникальные лоты, доступные только для премиум-участников</p>
              </div>
              
              <div class="premium-features">
                <div class="feature-item">
                  <span class="feature-icon">✓</span>
                  <span class="feature-text">Неограниченное участие в платных аукционах</span>
                </div>
                <div class="feature-item">
                  <span class="feature-icon">✓</span>
                  <span class="feature-text">Ранний доступ к новым лотам</span>
                </div>
                <div class="feature-item">
                  <span class="feature-icon">✓</span>
                  <span class="feature-text">Особый статус благотворителя</span>
                </div>
              </div>
              
              <div class="premium-cta">
                <div class="premium-price">999 ₽/месяц</div>
                <button class="premium-button">Активировать премиум</button>
              </div>
              
              <div class="premium-special">
                <div class="special-badge">Специальное предложение</div>
                <p>Оформите подписку сегодня и получите доступ к закрытому аукциону редких предметов искусства!</p>
              </div>
            </div>
          </div>

          </div>
          
          <div class="current-auctions-column">
            <div class="auctions-card">
              <h2 class="section-title">Актуальные аукционы</h2>
              
              <div class="auction-slider">
                <div class="auction-slide" v-for="(auction, index) in auctions" :key="index">
                  <div class="auction-image">
                    <img :src="auction.image" :alt="auction.title">
                    <!-- <div class="auction-nav">
                      <button class="nav-button prev" @click="prevSlide">&lt;</button>
                      <button class="nav-button next" @click="nextSlide">&gt;</button>
                    </div> -->
                  </div>
                  
                  <div class="auction-category">{{ auction.category }}</div>
                  <h3 class="auction-title">{{ auction.title }}</h3>
                  <p class="auction-description">{{ auction.description }}</p>
                  
                  <div class="auction-details">
                    <div class="current-bid">
                      <span>Текущая ставка:</span> {{ auction.currentBid }} ₽
                    </div>
                    <div class="auction-time">
                      <span>⏱️</span> {{ auction.timeLeft }}
                    </div>
                  </div>
                  
                  <button class="btn make-bid-btn">Сделать ставку</button>
                </div>
              </div>
              
              <div class="pagination-dots">
                <span 
                  v-for="(_, i) in auctions" 
                  :key="i" 
                  class="dot" 
                  :class="{ active: i === currentSlide }"
                  @click="currentSlide = i">
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
export default {
  name: 'HomeView',
  data() {
    return {
      currentSlide: 0,
      winners: [
        { 
          name: 'Иван И.', 
          lot: 'Компьютерная мышь', 
          amount: '1000' 
        },
        { 
          name: 'Марина В.', 
          lot: '101 Чёрная роза', 
          amount: '1000000' 
        },
        { 
          name: 'Артём С.', 
          lot: 'Картина "Лось"', 
          amount: '99000' 
        },
        { 
          name: 'Вольтер Ф.', 
          lot: 'Набор редких книг', 
          amount: '55555' 
        },
        { 
          name: 'Даймонд Д.', 
          lot: 'Микробы и сталь', 
          amount: '7777' 
        }
      ],
      // successStories: [
      //   'Благодаря средствам с предыдущих аукционов, в детском доме №5 обновили учебные материалы и оборудование для творческих занятий. Теперь дети могут развивать свои таланты в комфортных условиях.',
      //   'Поддержка участников аукциона помогла организовать бесплатные мастер-классы для детей с ограниченными возможностями здоровья, что значительно улучшило их социальную адаптацию.',
      //   'Собранные средства направлены на приобретение медикаментов и питание для больных детей в региональной детской больнице, что стало важной помощью в сложный период.',
      //   'Участники аукциона помогли реализовать проект по благоустройству детской площадки в приюте, где теперь дети могут безопасно играть и развиваться.'
      // ],
      auctions: [
        {
          title: 'Компьютерная мышь',
          image: '/src/assets/img/mouse.png',
          description: 'Уникальная компьютерная мышь, все средства пойдут на поддержку приюта для кошек.',
          currentBid: '1000',
          timeLeft: '2 дня'
        },
        {
          title: 'Картина "Лось"',
          image: '/src/assets/img/kartina.jpg',
          description: 'Уникальная работа, все средства пойдут на поддержку детского дома №5.',
          currentBid: '99000',
          timeLeft: '5 дней'
        },
        {
          title: '101 Чёрная роза',
          image: '/src/assets/img/roze.jpg',
          description: 'Эксклюзивный розы в количестве 101 штуки, все средства пойдут на поддержку онкологического центра.',
          currentBid: '1000000',
          timeLeft: '7 дня'
        }
      ]
    }
  },
  methods: {
    nextSlide() {
      this.currentSlide = (this.currentSlide + 1) % this.auctions.length;
    },
    prevSlide() {
      this.currentSlide = (this.currentSlide - 1 + this.auctions.length) % this.auctions.length;
    }
  }
}
</script>

<style scoped>
.home {
  background: linear-gradient(135deg, #EDE7F6 0%, #E3F2FD 100%);
}
.auctions-section {
  padding: 60px 0;
}

.section-grid {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 50px;
}

.section-title {
  font-size: 1.5rem;
  margin-bottom: 20px;
  color: var(--primary-color);
  font-weight: 600;
  display: flex;
  align-items: center;
}

.trophy-icon, .heart-icon {
  margin-right: 10px;
}

/* Winners Card */
.winners-card, .success-stories-card {
  background: white;
  border-radius: var(--border-radius);
  box-shadow: var(--box-shadow);
  padding: 20px;
  margin-bottom: 25px;
}

.winners-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.winner-item {
  display: flex;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}

.winner-item:last-child {
  border-bottom: none;
}

.winner-number {
  width: 30px;
  color: #999;
  font-weight: 600;
}

.winner-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  margin-right: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.winner-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.winner-info {
  flex: 1;
}

.winner-name {
  font-weight: 600;
  color: var(--text-color);
}

.winner-lot {
  font-size: 0.9rem;
  color: #777;
}

.winner-amount {
  font-weight: 600;
  color: var(--secondary-color);
}

/* Success Stories Card */
.success-stories-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.success-story-item {
  background-color: #f5f9ff;
  padding: 15px;
  border-radius: 8px;
  border-left: 4px solid var(--primary-color);
  color: #444;
  font-size: 0.95rem;
  line-height: 1.5;
}

/* Auctions Card */
.auctions-card {
  background: white;
  border-radius: var(--border-radius);
  box-shadow: var(--box-shadow);
  padding: 20px;
  height: 100%;
}

.auction-slider {
  position: relative;
}

.auction-image {
  position: relative;
  overflow: hidden;
  height: 220px;
  margin-bottom: 16px;
  border-radius: 8px;
  /* padding: 20px 15px; */
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #fafafa;
}

.auction-image img {
  width: 100%;
  height: 100%;
  /* object-fit: contain; */
  border-radius: 6px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
}

.auction-nav {
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  transform: translateY(-50%);
  display: flex;
  justify-content: space-between;
  padding: 0 10px;
}

.nav-button {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.8);
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 1.2rem;
  font-weight: bold;
}

.auction-category {
  color: var(--primary-color);
  font-size: 0.9rem;
  margin-bottom: 5px;
}

.auction-title {
  font-size: 1.3rem;
  margin-bottom: 10px;
  color: var(--text-color);
}

.auction-description {
  font-size: 0.95rem;
  color: black;
  margin-bottom: 20px;
}

.auction-details {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.current-bid {
  font-weight: 600;
}

.current-bid span {
  color: #777;
  font-weight: normal;
}

.auction-time {
  display: flex;
  align-items: center;
  gap: 5px;
}
.premium-button{
  background-color: var(--secondary-color);
  margin: 5px 0px;
}
.premium-promo-card{
  background-color: white;
  border-radius: 10px ;
  padding: 20px;
}
.make-bid-btn {
  width: 100%;
  margin-bottom: 20px;
}
.make-bid-btn:last-child {
  width: 100%;
}
/* .pagination-dots {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 20px;
} */

/* .dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background-color: #ddd;
  cursor: pointer;
} */

/* .dot.active {
  background-color: var(--primary-color);
} */

@media (max-width: 1200px) {
  .section-grid {
    gap: 40px;
  }
}

@media (max-width: 992px) {
  .section-grid {
    grid-template-columns: 1fr;
    gap: 30px;
  }
  
  .winners-card, .success-stories-card, .auctions-card {
    margin-bottom: 30px;
  }
}

@media (max-width: 768px) {
  .auctions-section {
    padding: 40px 0;
  }
  
  .section-grid {
    gap: 25px;
  }
  
  .winner-amount {
    font-size: 0.9rem;
  }
}

@media (max-width: 480px) {
  .section-title {
    font-size: 1.3rem;
  }
  
  .section-grid {
    gap: 20px;
  }
  
  .auction-details {
    flex-direction: column;
    gap: 10px;
  }
}
</style>