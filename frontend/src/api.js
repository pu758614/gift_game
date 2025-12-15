import axios from 'axios';

// 動態決定 API URL
// 總是使用當前訪問的主機名加上 5000 端口，這樣在手機和電腦上都能正常工作
const getApiUrl = () => {
  const hostname = window.location.hostname;
  return `http://${hostname}:5000`;
};

const API_URL = getApiUrl();

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 輔助函數：將相對路徑的圖片URL轉換為完整URL
export const getFullImageUrl = (imageUrl) => {
  if (!imageUrl) return null;
  if (imageUrl.startsWith('http')) return imageUrl;
  // 如果是相對路徑，添加API URL前綴
  return `${API_URL}${imageUrl}`;
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
};

export default api;
