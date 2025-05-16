<template>
  <transition name="fade">
    <div class="alert" :class="alertClasses" v-if="visible">
      <div class="alert-content">
        <div class="alert-icon" v-if="showIcon">
          <span v-if="type === 'success'">✓</span>
          <span v-else-if="type === 'error'">✕</span>
          <span v-else-if="type === 'warning'">!</span>
          <span v-else-if="type === 'info'">i</span>
        </div>
        <span class="alert-message">{{ message }}</span>
        <button class="close-btn" @click="closeAlert">&times;</button>
      </div>
    </div>
  </transition>
</template>

<script>
export default {
  name: 'AlertMessage',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    message: {
      type: String,
      default: ''
    },
    type: {
      type: String,
      default: 'success',
      validator: value => ['success', 'error', 'warning', 'info'].includes(value)
    },
    autoHide: {
      type: Boolean,
      default: false
    },
    duration: {
      type: Number,
      default: 3000
    },
    showIcon: {
      type: Boolean,
      default: true
    }
  },
  
  data() {
    return {
      visible: this.show,
      timer: null
    };
  },
  
  computed: {
    alertClasses() {
      return {
        'alert-success': this.type === 'success',
        'alert-error': this.type === 'error',
        'alert-warning': this.type === 'warning',
        'alert-info': this.type === 'info'
      };
    }
  },
  
  watch: {
    show(newVal) {
      this.visible = newVal;
      this.handleAutoHide();
    }
  },
  
  mounted() {
    this.handleAutoHide();
  },
  
  beforeUnmount() {
    this.clearTimer();
  },
  
  methods: {
    closeAlert() {
      this.visible = false;
      this.clearTimer();
      this.$emit('close');
    },
    
    handleAutoHide() {
      this.clearTimer();
      
      if (this.visible && this.autoHide) {
        this.timer = setTimeout(() => {
          this.closeAlert();
        }, this.duration);
      }
    },
    
    clearTimer() {
      if (this.timer) {
        clearTimeout(this.timer);
        this.timer = null;
      }
    }
  }
}
</script>

<style scoped>
.alert {
  padding: 14px 16px;
  margin-bottom: 16px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  position: relative;
  overflow: hidden;
}

.alert::before {
  content: "";
  position: absolute;
  bottom: 0;
  left: 0;
  height: 3px;
  background-color: currentColor;
  opacity: 0.3;
  width: 100%;
}

.alert-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.alert-icon {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background-color: currentColor;
  color: white;
  font-weight: bold;
  font-size: 14px;
}

.alert-message {
  flex-grow: 1;
}

.alert-success {
  background-color: #d4edda;
  color: #155724;
  border-left: 4px solid #28a745;
}

.alert-error {
  background-color: #f8d7da;
  color: #721c24;
  border-left: 4px solid #dc3545;
}

.alert-warning {
  background-color: #fff3cd;
  color: #856404;
  border-left: 4px solid #ffc107;
}

.alert-info {
  background-color: #d1ecf1;
  color: #0c5460;
  border-left: 4px solid #17a2b8;
}

.close-btn {
  background: none;
  border: none;
  color: inherit;
  font-size: 20px;
  cursor: pointer;
  padding: 0;
  opacity: 0.7;
  transition: opacity 0.2s;
}

.close-btn:hover {
  opacity: 1;
}

/* Анимации появления и исчезновения */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s, transform 0.3s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style> 