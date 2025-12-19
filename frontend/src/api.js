import axios from 'axios';

// 使用相對路徑，利用 Vite 的 proxy 配置
// 這樣在開發環境會通過 proxy 轉發到後端
const api = axios.create({
  baseURL: '',
  headers: {
    'Content-Type': 'application/json',
  },
});

// 輔助函數：將相對路徑的圖片URL轉換為完整URL
export const getFullImageUrl = (imageUrl) => {
  if (!imageUrl) return null;
  if (imageUrl.startsWith('http')) return imageUrl;
  // 如果是相對路徑 (例如 /gift-images/xxx.png)，使用當前主機名加上 MinIO 端口
  const hostname = window.location.hostname;
  return `http://${hostname}:9000${imageUrl}`;
};

export const giftAPI = {
  // 提交表單
  submitForm: (formData) => api.post('/api/submit-form', formData),

  // 生成禮物圖片
  generateGift: (giftId) => api.post(`/api/generate-gift/${giftId}`),

  // 重新生成
  regenerateGift: (giftId) => api.post(`/api/regenerate/${giftId}`),

  // 確認禮物
  confirmGift: (giftId) => api.post(`/api/confirm/${giftId}`),

  // 取得所有禮物
  getAllGifts: () => api.get('/api/gifts'),

  // 取得單一禮物詳情
  getGiftDetail: (giftId) => api.get(`/api/gift/${giftId}`),

  // 交換禮物
  exchangeGift: (giftId, exchangerName) =>
    api.post('/api/exchange', { gift_id: giftId, exchanger_name: exchangerName }),

  // 重置遊戲
  resetGame: () => api.post('/api/reset'),

  // 投票相關
  submitVote: (giftId, awardType, voterFingerprint) =>
    api.post('/api/voting/submit', {
      gift_id: giftId,
      award_type: awardType,
      voter_fingerprint: voterFingerprint,
    }),

  getVotingStatus: (voterFingerprint) =>
    api.post('/api/voting/status', { voter_fingerprint: voterFingerprint }),

  getVotingResults: () => api.get('/api/voting/results'),
};

export default api;
