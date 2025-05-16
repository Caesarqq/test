<template>
  <div class="spinner-container" :class="{ overlay: isOverlay, inline: !isOverlay }">
    <div class="spinner"></div>
    <p v-if="text" class="spinner-text">{{ text }}</p>
  </div>
</template>

<script>
export default {
  name: 'LoadingSpinner',
  props: {
    text: {
      type: String,
      default: 'Загрузка...'
    },
    isOverlay: {
      type: Boolean,
      default: false
    }
  }
}
</script>

<style scoped>
.spinner-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.8);
  z-index: 9999;
}

.inline {
  padding: 20px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(0, 123, 255, 0.2);
  border-top-color: #007bff;
  border-radius: 50%;
  animation: spin 1s ease-in-out infinite;
}

.spinner-text {
  margin-top: 16px;
  font-size: 16px;
  color: #6c757d;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style> 