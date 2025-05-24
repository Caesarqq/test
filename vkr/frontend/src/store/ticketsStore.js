import { defineStore } from 'pinia';
import apiClient from '../api/axios';

export const useTicketsStore = defineStore('tickets', {
  state: () => ({
    tickets: [],
    loading: false,
    error: null
  }),
  
  getters: {
    hasTicketForAuction: (state) => (auctionId) => {
      return state.tickets.some(ticket => ticket.auction == auctionId);
    }
  },
  
  actions: {
    async fetchUserTickets() {
      this.loading = true;
      try {
        const response = await apiClient.get('/auctions/tickets/');
        this.tickets = response.data;
        // Сохраняем в localStorage
        localStorage.setItem('user_tickets', JSON.stringify(this.tickets));
        return this.tickets;
      } catch (error) {
        this.error = error.response?.data?.detail || 'Ошибка при загрузке билетов';
        console.error('Error fetching tickets:', error);
        return [];
      } finally {
        this.loading = false;
      }
    },
    
    loadTicketsFromStorage() {
      const storedTickets = localStorage.getItem('user_tickets');
      if (storedTickets) {
        try {
          this.tickets = JSON.parse(storedTickets);
        } catch (e) {
          console.error('Error parsing tickets from localStorage:', e);
        }
      }
    },
    
    addTicket(ticket) {
      this.tickets.push(ticket);
      localStorage.setItem('user_tickets', JSON.stringify(this.tickets));
    },
    
    clearTickets() {
      this.tickets = [];
      localStorage.removeItem('user_tickets');
    }
  }
});