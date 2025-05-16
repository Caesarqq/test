<template>
  <div class="comment-card">
    <div class="comment-avatar">
      <span v-if="userAvatar" class="avatar-img"><img :src="userAvatar" :alt="username" /></span>
      <span v-else class="avatar-initials">{{ initials }}</span>
    </div>
    <div class="comment-content">
      <div class="comment-header">
        <span class="comment-username">{{ username }}</span>
        <span class="comment-date">{{ formattedDate }}</span>
      </div>
      <div class="comment-text">{{ comment.content }}</div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
const props = defineProps({
  comment: { type: Object, required: true }
});

const username = computed(() => props.comment.user_display_name || props.comment.user_username || 'Пользователь');
const userAvatar = computed(() => props.comment.user_avatar || null); // если есть поле user_avatar
const initials = computed(() => username.value.split(' ').map(n => n[0]).join('').toUpperCase().slice(0,2));
const formattedDate = computed(() => {
  const d = new Date(props.comment.created_at);
  return d.toLocaleString('ru-RU', { day: '2-digit', month: '2-digit', year: '2-digit', hour: '2-digit', minute: '2-digit' });
});
</script>

<style scoped>
.comment-card {
  display: flex;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid #eee;
  background: #f8f9fa;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
  margin-bottom: 10px;
}
.comment-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 18px;
  color: #555;
  overflow: hidden;
  margin-left: 10px;
}
.avatar-img img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
}
.avatar-initials {
  width: 100%;
  text-align: center;
}
.comment-content {
  flex: 1;
}
.comment-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 2px;
}
.comment-username {
  font-weight: 600;
  color: #222;
}
.comment-date {
  color: #888;
  font-size: 13px;
}
.comment-text {
  font-size: 15px;
  color: #333;
  white-space: pre-line;
}
</style> 