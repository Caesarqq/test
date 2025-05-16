<template>
  <div class="bid-card" :class="{ 'bid-card--winner': bid.is_winner || isWinner, 'bid-card--active': bid.is_active, 'bid-card--outbid': !bid.is_winner && !bid.is_active && !isWinner }">
    <div class="bid-card__header">
      <div class="bid-card__title-wrapper">
        <span class="bid-card__title">{{ getUserName(bid) }}</span>
        <span v-if="!isHighest && !isWinner" class="bid-card__badge badge-outbid" style="color:#dc3545; background:transparent; border:none; font-weight:600;">Перебита</span>
        <span v-if="isWinner" class="bid-card__badge badge-winner" style="color:#28a745; background:transparent; border:none; font-weight:600;">Победитель</span>
      </div>
      <span class="bid-card__amount">{{ formatPrice(bid.amount) }}</span>
    </div>
    
    <div class="bid-card__content">
      <div class="bid-card__detail">
        <span class="bid-card__label">Дата ставки:</span>
        <span class="bid-card__value">{{ formatDate(bid.created_at) }}</span>
      </div>
      
      <div v-if="bid.auction_end_time" class="bid-card__detail">
        <span class="bid-card__label">Завершение аукциона:</span>
        <span class="bid-card__value">{{ formatDate(bid.auction_end_time) }}</span>
      </div>
    </div>
    
    <div class="bid-card__footer">
      <button v-if="bid.is_active" @click="$emit('place-bid', bid.lot)" class="btn-make-bid">
        Сделать новую ставку
      </button>
      <!-- <button v-if="bid.is_winner || isWinner" class="btn-view-lot">
        <router-link :to="{ name: 'lot', params: { id: bid.lot } }" class="link-no-style">
          Посмотреть лот
        </router-link>
      </button> -->
    </div>
  </div>
</template>

<script>
export default {
  name: 'BidCard',
  props: {
    bid: {
      type: Object,
      required: true
    },
    formatPrice: {
      type: Function,
      required: true
    },
    formatDate: {
      type: Function,
      required: true
    },
    highestAmount: {
      type: Number,
      required: false
    },
    isWinner: {
      type: Boolean,
      default: false
    }
  },
  emits: ['place-bid'],
  methods: {
    getUserName(bid) {
      if (bid.user_first_name && bid.user_last_name) {
        return `${bid.user_first_name} ${bid.user_last_name}`;
      }
      
      if (bid.user_first_name) return bid.user_first_name;
      if (bid.user_last_name) return bid.user_last_name;
      
      if (bid.user_username) return bid.user_username;
      
      return bid.user_email || 'Пользователь';
    }
  },
  computed: {
    isHighest() {
      return this.highestAmount !== undefined && Number(this.bid.amount) === Number(this.highestAmount);
    }
  }
}
</script>

<style scoped>
.bid-card {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 16px;
  margin-bottom: 16px;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  background-color: #fff;
  border-left: 4px solid #e9ecef;
}

.bid-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.bid-card--winner {
  border-left-color: #28a745;
}

.bid-card--active {
  border-left-color: #007bff;
}

.bid-card--outbid {
  border-left-color: #6c757d;
}

.bid-card__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.bid-card__title-wrapper {
  display: flex;
  flex-direction: column;
}

.bid-card__title {
  font-weight: 600;
  font-size: 1.1rem;
  color: #2c3e50;
  text-decoration: none;
  margin-bottom: 6px;
}

.bid-card__title:hover {
  color: #007bff;
  text-decoration: underline;
}

.bid-card__badge {
  font-size: 0.75rem;
  padding: 2px 8px;
  border-radius: 12px;
  display: inline-block;
  align-self: flex-start;
}

.badge-winner {
  background-color: #d4edda;
  color: #155724;
  font-weight: bold;
}

.badge-active {
  background-color: #cce5ff;
  color: #004085;
}

.badge-outbid {
  background-color: #f8f9fa;
  color: #6c757d;
}

.bid-card__amount {
  font-weight: 700;
  font-size: 1.2rem;
  color: #28a745;
}

.bid-card__content {
  margin-bottom: 16px;
}

.bid-card__detail {
  display: flex;
  margin-bottom: 6px;
}

.bid-card__label {
  font-weight: 500;
  color: #6c757d;
  min-width: 140px;
  margin-right: 12px;
}

.bid-card__value {
  color: #212529;
}

.bid-card__footer {
  display: flex;
  justify-content: flex-end;
}

.btn-make-bid, .btn-view-lot {
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  text-align: center;
  border: none;
  transition: background-color 0.2s ease;
}

.btn-make-bid {
  background-color: #007bff;
  color: white;
}

.btn-make-bid:hover {
  background-color: #0069d9;
}

.btn-view-lot {
  background-color: #6c757d;
  color: white;
}

.btn-view-lot:hover {
  background-color: #5a6268;
}

.link-no-style {
  color: inherit;
  text-decoration: none;
}

@media (max-width: 576px) {
  .bid-card__header {
    flex-direction: column;
  }
  
  .bid-card__amount {
    margin-top: 8px;
  }
  
  .bid-card__detail {
    flex-direction: column;
  }
  
  .bid-card__label {
    margin-bottom: 4px;
  }
}
</style> 