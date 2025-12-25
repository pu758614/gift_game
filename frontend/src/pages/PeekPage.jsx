import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { giftAPI, getFullImageUrl } from '../api';

function PeekPage() {
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

  const handleConfirmPeek = () => {
    setShowConfirmModal(false);
    setShowResultModal(true);
  };

  const handleCloseConfirm = () => {
    setShowConfirmModal(false);
    setSelectedGift(null);
  };

  const handleCloseResult = () => {
    setShowResultModal(false);
    setSelectedGift(null);
  };

  if (loading) {
    return <div className="loading">載入中...</div>;
  }

  const availableGifts = gifts.filter(g => !g.is_exchanged);

  return (
    <div className="container">
      <h1>👀 偷看禮物</h1>

      <div className="card">
        <h2 style={{ marginBottom: '24px' }}>選擇你想偷看的禮物</h2>

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

      {/* 確認要偷看 Modal */}
      {showConfirmModal && selectedGift && (
        <div className="modal-overlay" onClick={handleCloseConfirm}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>👀 確認要偷看這份禮物嗎？</h3>
            <p style={{ color: '#666', marginTop: '16px' }}>
              偷看後會看到禮物的名稱喔！
            </p>

            <div className="button-group" style={{ marginTop: '24px' }}>
              <button className="btn btn-secondary" onClick={handleCloseConfirm}>
                取消
              </button>
              <button className="btn btn-primary" onClick={handleConfirmPeek}>
                確認偷看
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 偷看結果 Modal */}
      {showResultModal && selectedGift && (
        <div className="modal-overlay" onClick={handleCloseResult}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3 style={{ color: '#667eea' }}>👀 你偷看到了...</h3>

            <div className="image-preview" style={{ margin: '24px 0' }}>
              <img
                src={getFullImageUrl(selectedGift.image_url)}
                alt="禮物"
                style={{ maxHeight: '300px', width: '100%', objectFit: 'contain' }}
              />
            </div>

            <div style={{
              marginBottom: '16px',
              textAlign: 'center',
              background: '#f8f9fa',
              padding: '24px',
              borderRadius: '8px',
              border: '2px solid #667eea'
            }}>
              <p style={{
                fontSize: '1.5rem',
                fontWeight: 'bold',
                color: '#667eea',
                margin: 0
              }}>
                🎁 {selectedGift.gift_name}
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

export default PeekPage;
