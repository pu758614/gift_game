import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { giftAPI, getFullImageUrl } from '../api';

function ExchangePage() {
  const navigate = useNavigate();
  const [gifts, setGifts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedGift, setSelectedGift] = useState(null);
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [showResultModal, setShowResultModal] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadGifts();
  }, []);

  const loadGifts = async () => {
    try {
      const response = await giftAPI.getAllGifts();
      setGifts(response.data.gifts);
    } catch (err) {
      setError('載入失敗，請稍後再試');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectGift = async (gift) => {
    if (gift.is_exchanged) {
      return; // 已交換的禮物不能選擇
    }

    try {
      // 獲取禮物詳情
      const response = await giftAPI.getGiftDetail(gift.id);
      setSelectedGift(response.data.gift);
      setShowConfirmModal(true);
    } catch (err) {
      setError('獲取禮物詳情失敗');
    }
  };

  const handleConfirmExchange = async () => {
    setShowConfirmModal(false);

    try {
      // 直接執行交換（使用匿名交換者）
      await giftAPI.exchangeGift(selectedGift.id, '匿名');

      // 顯示結果視窗
      setShowResultModal(true);
    } catch (err) {
      setError(err.response?.data?.error || '交換失敗');
      setSelectedGift(null);
    }
  };

  const handleCloseConfirm = () => {
    setShowConfirmModal(false);
    setSelectedGift(null);
  };

  const handleCloseResult = () => {
    // 從列表中移除這個禮物
    setGifts(prevGifts => prevGifts.filter(g => g.id !== selectedGift.id));

    // 關閉彈窗並重置
    setShowResultModal(false);
    setSelectedGift(null);
  };

  if (loading) {
    return <div className="loading">載入中...</div>;
  }

  const availableGifts = gifts.filter(g => !g.is_exchanged);

  return (
    <div className="container">
      <h1>🎲 開始交換禮物</h1>

      <div className="card">
        <h2 style={{ marginBottom: '24px' }}>選擇你想要的禮物</h2>

        {error && <div className="error">{error}</div>}

        {availableGifts.length === 0 ? (
          <p style={{ textAlign: 'center', padding: '48px', color: '#666' }}>
            所有禮物都已被交換完畢！
          </p>
        ) : (
          <div className="gifts-grid">
            {availableGifts.map((gift) => (
              <div key={gift.id} className="gift-item">
                <div
                  className="gift-card"
                  onClick={() => handleSelectGift(gift)}
                  style={{
                    cursor: 'pointer',
                    border: '1px solid #e0e0e0',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                  }}
                >
                  <img
                    src={getFullImageUrl(gift.image_url)}
                    alt="禮物"
                    className="gift-image"
                  />
                </div>
                <div className="gift-description">
                  <div className="gift-description-icon">💬</div>
                  <p className="gift-description-text">
                    {gift.happiness_reason}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 確認要這份禮物 Modal */}
      {showConfirmModal && selectedGift && (
        <div className="modal-overlay" onClick={handleCloseConfirm}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>確認要這份禮物嗎？</h3>

            <div className="button-group" style={{ marginTop: '24px' }}>
              <button className="btn btn-secondary" onClick={handleCloseConfirm}>
                取消
              </button>
              <button className="btn btn-primary" onClick={handleConfirmExchange}>
                確認
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 交換成功詳情 Modal */}
      {showResultModal && selectedGift && (
        <div className="modal-overlay" onClick={handleCloseResult}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3 style={{ color: '#28a745' }}>🎉 交換成功！你獲得的禮物</h3>

            <div className="image-preview" style={{ margin: '24px 0' }}>
              <img
                src={getFullImageUrl(selectedGift.image_url)}
                alt="禮物"
                style={{ maxHeight: '300px', width: '100%', objectFit: 'contain' }}
              />
            </div>

            <div style={{ marginBottom: '16px', textAlign: 'left', background: '#f8f9fa', padding: '16px', borderRadius: '8px', color: '#333' }}>
              <p style={{ marginBottom: '12px', color: '#333' }}>
                <strong style={{ color: '#667eea' }}>你的名字？</strong><br />
                {selectedGift.player_name}
              </p>
              <p style={{ marginBottom: '12px', color: '#333' }}>
                <strong style={{ color: '#667eea' }}>你這個禮物的外型或材質是什麼？</strong><br />
                {selectedGift.appearance}
              </p>
              <p style={{ marginBottom: '12px', color: '#333' }}>
                <strong style={{ color: '#667eea' }}>你這個禮物通常是什麼人會喜歡的？</strong><br />
                {selectedGift.who_likes}
              </p>
              <p style={{ marginBottom: '12px', color: '#333' }}>
                <strong style={{ color: '#667eea' }}>你這個禮物通常是在什麼時候使用？</strong><br />
                {selectedGift.usage_time}
              </p>
              <p style={{ marginBottom: '0', color: '#333' }}>
                <strong style={{ color: '#667eea' }}>收到的人會因為這禮物而發出什麼讚嘆？</strong><br />
                {selectedGift.happiness_reason}
              </p>
            </div>

            <div style={{ marginTop: '24px', textAlign: 'center' }}>
              <button className="btn btn-primary" onClick={handleCloseResult}>
                關閉
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ExchangePage;
