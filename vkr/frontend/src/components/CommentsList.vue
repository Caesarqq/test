<template>
  <div class="comments-list">
    <div v-if="loading && comments.length === 0" class="comments-loading">
      <loading-spinner text="Загрузка комментариев..." />
    </div>
    <div v-else>
      <div v-if="comments.length === 0" class="comments-empty">Комментариев пока нет</div>
      <div v-else>
        <CommentCard v-for="comment in comments" :key="comment.id" :comment="comment" />
        <div v-if="loading && comments.length > 0" class="comments-loading-more">
          <loading-spinner text="Загрузка..." />
        </div>
        <div ref="infiniteScrollTrigger"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, computed } from 'vue';
import { useCommentStore } from '../store/commentStore';
import CommentCard from './CommentCard.vue';
import LoadingSpinner from './LoadingSpinner.vue';

const props = defineProps({
  lotId: { type: [String, Number], required: true }
});

const commentStore = useCommentStore();
const { loading, hasMore, next, error } = commentStore;
const infiniteScrollTrigger = ref(null);

const comments = computed(() => commentStore.commentsByLot[props.lotId] || []);

const fetchInitial = () => {
  commentStore.clearComments(props.lotId);
  commentStore.fetchComments(props.lotId);
};

onMounted(() => {
  fetchInitial();
  // Бесконечный скролл
  const observer = new IntersectionObserver((entries) => {
    if (entries[0].isIntersecting && hasMore && !loading) {
      if (next) commentStore.fetchComments(props.lotId, next);
    }
  }, { threshold: 1 });
  if (infiniteScrollTrigger.value) {
    observer.observe(infiniteScrollTrigger.value);
  }
  // cleanup
  onUnmounted(() => {
    if (infiniteScrollTrigger.value) observer.disconnect();
  });
});

watch(() => props.lotId, fetchInitial);
</script>

<style scoped>
.comments-list {
  margin: 24px 0 0 0;
}
.comments-loading, .comments-loading-more {
  display: flex;
  justify-content: center;
  margin: 12px 0;
}
.comments-empty {
  color: #888;
  text-align: center;
  margin: 18px 0;
}
</style> 