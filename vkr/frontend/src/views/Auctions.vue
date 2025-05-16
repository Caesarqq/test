<template>
  <div class="auctions-container">
    <div class="auctions-header">
      <h1>Аукционы</h1>
      
      <!-- Кнопка создания нового аукциона (только для благотворительных организаций) -->
      <button 
        v-if="authStore.isAuthenticated && authStore.user?.role === 'charity'" 
        @click="navigateToCreateAuction" 
        class="create-auction-btn"
      >
        Создать новый аукцион
      </button>
    </div>
    
    <!-- Индикатор загрузки -->
    <loading-spinner v-if="auctionsStore.loading" text="Загрузка аукционов..." />
    
    <!-- Сообщение об ошибке -->
    <div v-if="auctionsStore.error" class="error-message">
      {{ auctionsStore.error }}
    </div>
    
    <!-- Фильтры аукционов -->
    <div class="auction-filters">
      <div class="filter-group">
        <label for="status-filter">Статус:</label>
        <select id="status-filter" v-model="statusFilter">
          <option value="all">Все</option>
          <option value="active">Активные</option>
          <option value="upcoming">Предстоящие</option>
          <option value="ended">Завершенные</option>
        </select>
      </div>
      
      <div class="filter-group">
        <label for="search-filter">Поиск:</label>
        <input 
          type="text" 
          id="search-filter" 
          v-model="searchQuery" 
          placeholder="Название аукциона..."
        />
      </div>
    </div>
    
    <!-- Пустое состояние -->
    <div v-if="!auctionsStore.loading && filteredAuctions.length === 0" class="empty-state">
      <p>Аукционы не найдены</p>
      <button @click="auctionsStore.fetchAuctions" class="refresh-btn">
        Обновить
      </button>
    </div>
    
    <!-- Сетка аукционов -->
    <div v-if="!auctionsStore.loading && filteredAuctions.length > 0" class="auctions-grid">
      <auction-card 
        v-for="auction in filteredAuctions" 
        :key="auction.id" 
        :auction="auction"
      />
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuctionsStore } from '../store/auctionsStore';
import { useAuthStore } from '../store/auth';
import AuctionCard from '../components/AuctionCard.vue';
import LoadingSpinner from '../components/LoadingSpinner.vue';

export default {
  name: 'AuctionsView',
  
  components: {
    AuctionCard,
    LoadingSpinner
  },
  
  setup() {
    const router = useRouter();
    const auctionsStore = useAuctionsStore();
    const authStore = useAuthStore();
    const statusFilter = ref('all');
    const searchQuery = ref('');
    
    // Отфильтрованные аукционы
    const filteredAuctions = computed(() => {
      let filtered = auctionsStore.auctions;
      
      // Фильтрация по статусу
      if (statusFilter.value !== 'all') {
        const now = new Date();
        
        filtered = filtered.filter(auction => {
          const startDate = new Date(auction.start_time);
          const endDate = new Date(auction.end_time);
          
          switch (statusFilter.value) {
            case 'active':
              return now >= startDate && now <= endDate;
            case 'upcoming':
              return now < startDate;
            case 'ended':
              return now > endDate;
            default:
              return true;
          }
        });
      }
      
      // Фильтрация по поисковому запросу
      if (searchQuery.value.trim()) {
        const query = searchQuery.value.toLowerCase();
        filtered = filtered.filter(auction => 
          auction.name.toLowerCase().includes(query) || 
          (auction.description && auction.description.toLowerCase().includes(query))
        );
      }
      
      return filtered;
    });
    
    // Функция для перехода на страницу создания аукциона
    const navigateToCreateAuction = () => {
      router.push('/create-auction');
    };
    
    // Получение аукционов при монтировании компонента
    onMounted(async () => {
      await auctionsStore.fetchAuctions();
    });
    
    return {
      authStore,
      auctionsStore,
      statusFilter,
      searchQuery,
      filteredAuctions,
      navigateToCreateAuction
    };
  }
}
</script>

<style scoped>
.auctions-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

.auctions-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

h1 {
  margin: 0;
  color: #333;
}

.create-auction-btn {
  padding: 10px 16px;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 15px;
  font-weight: 500;
  transition: background-color 0.3s;
}

.create-auction-btn:hover {
  background-color: #218838;
}

.auction-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 24px;
  background-color: #f8f9fa;
  padding: 16px;
  border-radius: 8px;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-group label {
  font-weight: 500;
  color: #555;
}

.filter-group select,
.filter-group input {
  padding: 8px 12px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 14px;
  flex-grow: 1;
}

.auctions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
}

.empty-state {
  text-align: center;
  padding: 48px 0;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.empty-state p {
  color: #6c757d;
  margin-bottom: 16px;
  font-size: 16px;
}

.empty-state .refresh-btn {
  padding: 8px 16px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.error-message {
  background-color: #f8d7da;
  color: #721c24;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 24px;
  text-align: center;
}

@media (max-width: 768px) {
  .auctions-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }
  
  .auction-filters {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-group {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .filter-group select,
  .filter-group input {
    width: 100%;
  }
  
  .auctions-grid {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  }
}
</style>