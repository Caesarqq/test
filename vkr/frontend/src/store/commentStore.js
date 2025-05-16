import { defineStore } from 'pinia';
import apiClient from '../api/axios';

export const useCommentStore = defineStore('comment', {
  state: () => ({
    commentsByLot: {}, // { [lotId]: [comments] }
    loading: false,
    error: null,
    hasMore: true,
    next: null,
  }),
  actions: {
    async fetchComments(lotId, url = null) {
      this.loading = true;
      this.error = null;
      try {
        const endpoint = url || `/comments/?lot=${lotId}`;
        const response = await apiClient.get(endpoint);
        if (!this.commentsByLot[lotId] || !url) {
          this.commentsByLot[lotId] = response.data.results || response.data;
        } else if (url) {
          this.commentsByLot[lotId].push(...response.data.results);
        }
        this.next = response.data.next;
        this.hasMore = !!response.data.next;
      } catch (e) {
        this.error = 'Ошибка загрузки комментариев';
      } finally {
        this.loading = false;
      }
    },
    async addComment(lotId, content) {
      this.error = null;
      try {
        const response = await apiClient.post('/comments/', { lot: lotId, content });
        if (!this.commentsByLot[lotId]) {
          this.commentsByLot[lotId] = [];
        }
        this.commentsByLot[lotId].unshift(response.data);
        return response.data;
      } catch (e) {
        this.error = e.response?.data?.detail || 'Ошибка добавления комментария';
        throw e;
      }
    },
    clearComments(lotId) {
      if (lotId) {
        this.commentsByLot[lotId] = [];
      } else {
        this.commentsByLot = {};
      }
      this.hasMore = true;
      this.next = null;
    }
  }
});
