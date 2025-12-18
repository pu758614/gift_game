import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { giftAPI, getFullImageUrl } from '../api';

function ConfirmPage() {
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

  const handleEdit = () => {
    // 返回表單頁並帶入原本填寫的資料
    navigate('/', {
      state: {
        formData: {
          player_name: gift.player_name,
          gift_name: gift.gift_name,
          appearance: gift.appearance,
          who_likes: gift.who_likes,
          usage_time: gift.usage_time,
          happiness_reason: gift.happiness_reason,
        },
      },
    });
  };

  const handleConfirm = async () => {
    try {
      await giftAPI.confirmGift(giftId);
      // 確認成功後跳到上傳成功頁面
      navigate(`/success/${giftId}`);
    } catch (err) {
      setError('確認失敗，請稍後再試');
    }
  };

  if (loading) {
    return <div className="loading">載入中...</div>;
  }

  if (!gift) {
    return <div className="error">找不到禮物資訊</div>;
  }

  return (
    <div className="container">
      <h1>🎨 AI 生成的禮物</h1>

      <div className="card">
        <h2>AI 猜測你的禮物是：{gift.ai_guess}</h2>

        {error && <div className="error">{error}</div>}

        <div className="image-preview">
          <img src={getFullImageUrl(gift.image_url)} alt={gift.ai_guess} />
        </div>

        <div className="gift-info">
          <p><strong>{gift.player_name}的禮物</strong></p>
          <p><strong>外型或材質：</strong>{gift.appearance}</p>
          <p><strong>什麼人會喜歡：</strong>{gift.who_likes}</p>
          <p><strong>什麼時候使用：</strong>{gift.usage_time}</p>
          <p><strong>讚嘆：</strong>{gift.happiness_reason}</p>
        </div>

        <div className="button-group">
          <button
            className="btn btn-secondary"
            onClick={handleEdit}
          >
            ✏️ 重新編輯
          </button>
          <button
            className="btn btn-primary"
            onClick={handleConfirm}
          >
            ✓ 確認並上傳
          </button>
        </div>
      </div>
    </div>
  );
}

export default ConfirmPage;
