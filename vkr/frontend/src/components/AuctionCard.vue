<template>
  <div class="auction-card-wrapper">
    <div class="auction-card" @click="navigateToAuction">
      <div class="auction-image">
        <img v-if="auction.image_url" :src="auction.image_url" :alt="auction.name" />
        <div v-else class="no-image">Нет изображения</div>
      </div>
      <div class="auction-content">
        <h3 class="auction-title">{{ auction.name }}</h3>
        <div class="auction-category" v-if="auction.category">
          {{ auction.category }}
        </div>
        <div class="auction-dates">
          <div class="date-item">
            <span class="date-label">Начало:</span>
            <span class="date-value">{{ formatDate(auction.start_time) }}</span>
          </div>
          <div class="date-item">
            <span class="date-label">Окончание:</span>
            <span class="date-value">{{ formatDate(auction.end_time) }}</span>
          </div>
        </div>
        <div class="auction-status" :class="getStatusClass">
          {{ getStatusText }}
        </div>
        <div v-if="showOwnerControls" class="auction-owner-controls">
          <button @click.stop="editAuction" class="btn-edit">Редактировать</button>
          <button @click.stop="showCustomConfirm = true" class="btn-delete">Удалить</button>
        </div>
      </div>
    </div>
    <teleport to="body">
      <div v-if="showCustomConfirm" class="global-confirm-overlay" @click.self="showCustomConfirm = false">
        <div class="global-confirm-modal">
          <span>Удалить аукцион <b>{{ auction.name }}</b>?</span>
          <button @click="confirmDelete" class="btn-delete">Удалить</button>
          <button @click="showCustomConfirm = false" class="btn-cancel">Отмена</button>
        </div>
      </div>
    </teleport>
  </div>
</template>

<script>
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../store/auth';
import { useAuctionsStore } from '../store/auctionsStore';

export default {
  name: 'AuctionCard',
  
  props: {
    auction: {
      type: Object,
      required: true
    }
  },
  
  setup(props) {
    const router = useRouter();
    const authStore = useAuthStore();
    const auctionsStore = useAuctionsStore();
    const showCustomConfirm = ref(false);

    const showOwnerControls = computed(() => {
      if (!authStore.isAuthenticated || authStore.user?.role !== 'charity') return false;
      if (!authStore.user.charity || !props.auction.charity) return false;
      const userCharityId = typeof authStore.user.charity === 'object' ? authStore.user.charity.id : authStore.user.charity;
      const auctionCharityId = typeof props.auction.charity === 'object' ? props.auction.charity.id : props.auction.charity;
      return userCharityId === auctionCharityId;
    });

    const formatDate = (dateString) => {
      if (!dateString) return 'Не указано';
      
      const date = new Date(dateString);
      return new Intl.DateTimeFormat('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
      }).format(date);
    };

    const getStatusClass = computed(() => {
      const now = new Date();
      const startDate = new Date(props.auction.start_time);
      const endDate = new Date(props.auction.end_time);
      
      if (now < startDate) return 'upcoming';
      if (now > endDate) return 'ended';
      return 'active';
    });

    const getStatusText = computed(() => {
      switch (getStatusClass.value) {
        case 'upcoming': return 'Ожидается';
        case 'active': return 'Активен';
        case 'ended': return 'Завершен';
        default: return 'Неизвестно';
      }
    });

    const navigateToAuction = () => {
      router.push({ name: 'auction-detail', params: { id: props.auction.id } });
    };

    const editAuction = () => {
      router.push({ name: 'create-auction', query: { edit: props.auction.id } });
    };
    
    const confirmDelete = async () => {
      try {
        await auctionsStore.deleteAuction(props.auction.id);
        showCustomConfirm.value = false;
      } catch (e) {
        alert('Ошибка при удалении аукциона');
      }
    };
    
    return {
      formatDate,
      getStatusClass,
      getStatusText,
      navigateToAuction,
      showOwnerControls,
      editAuction,
      showCustomConfirm,
      confirmDelete
    };
  }
}
</script>

<style scoped>
.auction-card-wrapper {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  position: relative;
}

.auction-card {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: transform 0.3s, box-shadow 0.3s;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.auction-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.auction-image {
  height: 200px;
  overflow: hidden;
  position: relative;
  padding: 20px 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #fafafa;
}

.auction-image img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: #fff;
  border-radius: 6px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
}

.no-image {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  background-color: #f8f9fa;
  color: #6c757d;
  font-size: 14px;
}

.auction-content {
  padding: 16px;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.auction-title {
  margin: 0 0 8px;
  font-size: 18px;
  color: #333;
  line-height: 1.3;
}

.auction-category {
  font-size: 14px;
  color: #6c757d;
  margin-bottom: 12px;
}

.auction-dates {
  margin-top: auto;
  font-size: 14px;
}

.date-item {
  margin-bottom: 6px;
}

.date-label {
  color: #6c757d;
  margin-right: 6px;
}

.date-value {
  color: #333;
  font-weight: 500;
}

.auction-status {
  margin-top: 12px;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 14px;
  font-weight: bold;
  text-align: center;
}

.auction-status.upcoming {
  background-color: #e2f0fd;
  color: #0d6efd;
}

.auction-status.active {
  background-color: #d4edda;
  color: #198754;
}

.auction-status.ended {
  background-color: #f8d7da;
  color: #dc3545;
}

.auction-owner-controls {
  margin-top: 16px;
  display: flex;
  gap: 10px;
}

.btn-edit {
  background: #0d6efd;
  color: #fff;
  border: none;
  padding: 6px 14px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.2s;
}

.btn-edit:hover {
  background: #0b5ed7;
}

.btn-delete {
  background: #dc3545;
  color: #fff;
  border: none;
  padding: 6px 14px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.2s;
}

.btn-delete:hover {
  background: #b02a37;
}

.global-confirm-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0,0,0,0.25);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.global-confirm-modal {
  background: #fff;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 2px 16px rgba(0,0,0,0.22);
  padding: 22px 28px;
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 220px;
  max-width: 90vw;
  box-sizing: border-box;
}

.btn-cancel {
  background: #6c757d;
  color: #fff;
  border: none;
  padding: 6px 14px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.2s;
}
.btn-cancel:hover {
  background: #495057;
}
</style> 