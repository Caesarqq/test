<template>
  <div class="comment-form">
    <div v-if="!isAuthenticated" class="comment-form-auth">
      <router-link to="/login">Войдите, чтобы оставить комментарий</router-link>
    </div>
    <form v-else @submit.prevent="handleSubmit">
      <textarea
        v-model="text"
        :maxlength="maxLength"
        :disabled="loading"
        placeholder="Ваш комментарий..."
        rows="3"
        class="comment-textarea"
      ></textarea>
      <div class="comment-form-actions">
        <span class="comment-form-error" v-if="error">{{ error }}</span>
        <span class="comment-form-success" v-if="success">Комментарий добавлен!</span>
        <button type="submit" :disabled="!valid || loading" class="btn-submit">
          <loading-spinner v-if="loading" size="18" />
          <span v-else>Отправить</span>
        </button>
        <span class="comment-form-length">{{ text.length }}/{{ maxLength }}</span>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { useCommentStore } from '../store/commentStore';
import { useAuthStore } from '../store/auth';
import LoadingSpinner from './LoadingSpinner.vue';

const props = defineProps({
  lotId: { type: [String, Number], required: true }
});

const commentStore = useCommentStore();
const authStore = useAuthStore();
const isAuthenticated = computed(() => authStore.isAuthenticated);

const text = ref('');
const maxLength = 500;
const loading = ref(false);
const error = ref('');
const success = ref(false);

const valid = computed(() => {
  return text.value.trim().length > 0 && text.value.length <= maxLength;
});

const handleSubmit = async () => {
  if (!valid.value) return;
  loading.value = true;
  error.value = '';
  success.value = false;
  try {
    await commentStore.addComment(props.lotId, text.value);
    text.value = '';
    success.value = true;
    setTimeout(() => success.value = false, 1500);
    // Прокрутка к новому комментарию (опционально)
    setTimeout(() => {
      const list = document.querySelector('.comments-list');
      if (list) list.scrollTop = 0;
    }, 100);
  } catch (e) {
    if (e.response?.status === 401) {
      error.value = 'Требуется авторизация';
    } else if (e.response?.status === 400) {
      error.value = 'Ошибка валидации';
    } else {
      error.value = 'Ошибка отправки комментария';
    }
  } finally {
    loading.value = false;
  }
};

watch(text, () => {
  error.value = '';
  success.value = false;
});
</script>

<style scoped>
.comment-form {
  margin: 18px 0 0 0;
  padding: 0;
}
.comment-form-auth {
  color: #888;
  margin-bottom: 10px;
}
.comment-textarea {
  width: 100%;
  min-height: 60px;
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 8px 10px;
  font-size: 15px;
  resize: vertical;
  margin-bottom: 6px;
}
.comment-form-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}
.btn-submit {
  background: #0d6efd;
  color: #fff;
  border: none;
  padding: 6px 18px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 15px;
  transition: background 0.2s;
  display: flex;
  align-items: center;
  gap: 6px;
}
.btn-submit:disabled {
  background: #b3d1fa;
  cursor: not-allowed;
}
.comment-form-error {
  color: #dc3545;
  font-size: 14px;
}
.comment-form-success {
  color: #198754;
  font-size: 14px;
}
.comment-form-length {
  color: #888;
  font-size: 13px;
  margin-left: auto;
}
</style> 