import apiClient from './axios';

export default {
  getAuctions() {
    return apiClient.get('/v1/auctions/');
  },

  getAuctionById(id) {
    return apiClient.get(`/v1/auctions/${id}/`);
  },

  getAuctionEvents(auctionId) {
    return apiClient.get(`/auction-events/?auction=${auctionId}`);
  },

  getCharities() {
    return apiClient.get('/charities/');
  },

  createAuction(auctionData) {
    const config = {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    };

    console.log('[API] Отправка запроса на создание аукциона:', {
      endpoint: '/v1/auctions/create/',
      headers: config.headers,
      isFormData: auctionData instanceof FormData
    });

    if (auctionData instanceof FormData) {
      for (let [key, value] of auctionData.entries()) {
        if (key === 'image') {
          console.log(`[API] FormData содержит ${key}: [Файл]`);
        } else {
          console.log(`[API] FormData содержит ${key}: ${value}`);
        }
      }
    }

    return apiClient.post('/v1/auctions/create/', auctionData, config);
  },

  updateAuction(id, auctionData) {
    const config = {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    };
    return apiClient.put(`/v1/auctions/${id}/update/`, auctionData, config);
  },

  deleteAuction(id) {
    return apiClient.delete(`/v1/auctions/${id}/delete/`);
  },

  purchaseTicket(auctionId) {
    return apiClient.post('/v1/auctions/tickets/purchase/', { auction: auctionId });
  },

  checkTicketAccess(auctionId) {
    return apiClient.get(`/v1/auctions/tickets/check-access/?auction_id=${auctionId}`);
  }
};