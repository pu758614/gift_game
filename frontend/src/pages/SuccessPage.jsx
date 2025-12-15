import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { giftAPI, getFullImageUrl } from '../api';

function SuccessPage() {
  const { giftId } = useParams();
  const navigate = useNavigate();
  const [gift, setGift] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadGift();
  }, [giftId]);

  const loadGift = async () => {
    try {
      const response = await giftAPI.getGiftDetail(giftId);
      setGift(response.data.gift);
    } catch (err) {
      setError('載入失敗，請稍後再試');
    } finally {
      setLoading(false);
    }
  };

  const handleAddAnother = () => {
    navigate('/');
  };

  const handleViewGallery = () => {
    navigate('/gallery');
  };

  if (loading) {
    return <div className="loading">載入中...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  if (!gift) {
    return <div className="error">找不到禮物資訊</div>;
  }

  return (
    <div className="container">
      <div className="success-banner">
        <h1>🎉 禮物已成功上傳！</h1>
        <p>你的禮物已經加入交換池中</p>
      </div>

      <div className="card">
        <h2>你上傳的禮物資訊</h2>

        <div className="gift-preview">
          <div className="gift-image-container">
            <img
              src={getFullImageUrl(gift.image_url)}
              alt="禮物圖片"
              style={{
                width: '100%',
                maxWidth: '400px',
                height: 'auto',
                borderRadius: '12px',
                boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
                margin: '0 auto',
                display: 'block'
              }}
            />
          </div>

          <div className="gift-details">
            <div className="detail-item">
              <label>🎭 你的名字：</label>
              <p>{gift.player_name}</p>
            </div>

            <div className="detail-item">
              <label>📦 外型或材質：</label>
              <p>{gift.appearance}</p>
            </div>

            <div className="detail-item">
              <label>👥 適合的人：</label>
              <p>{gift.who_likes}</p>
            </div>

            <div className="detail-item">
              <label>⏰ 使用時機：</label>
              <p>{gift.usage_time}</p>
            </div>

            <div className="detail-item">
              <label>💝 帶來的幸福感：</label>
              <p>{gift.happiness_reason}</p>
            </div>
          </div>
        </div>
      </div>

      <style>{`
        .success-banner {
          text-align: center;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          padding: 30px;
          border-radius: 12px;
          margin-bottom: 30px;
          box-shadow: 0 8px 30px rgba(102, 126, 234, 0.3);
        }

        .success-banner h1 {
          margin: 0 0 10px 0;
          font-size: 32px;
        }

        .success-banner p {
          margin: 0;
          font-size: 18px;
          opacity: 0.9;
        }

        .gift-preview {
          margin: 20px 0;
        }

        .gift-image-container {
          margin-bottom: 30px;
          padding: 20px;
          background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
          border-radius: 12px;
        }

        .gift-details {
          display: flex;
          flex-direction: column;
          gap: 20px;
        }

        .detail-item {
          background: #f8f9fa;
          padding: 15px;
          border-radius: 8px;
          border-left: 4px solid #667eea;
        }

        .detail-item label {
          display: block;
          font-weight: bold;
          color: #667eea;
          margin-bottom: 8px;
          font-size: 16px;
        }

        .detail-item p {
          margin: 0;
          color: #333;
          font-size: 15px;
          line-height: 1.6;
        }
      `}</style>
    </div>
  );
}

export default SuccessPage;
