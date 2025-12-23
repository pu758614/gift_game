import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { giftAPI } from '../api';

function FormPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [generationStatus, setGenerationStatus] = useState(null);

  const [formData, setFormData] = useState({
    player_name: '',
    gift_name: '',
    appearance: '',
    who_likes: '',
    usage_time: '',
    happiness_reason: '',
  });

  // 如果有傳入的資料，則預填表單
  useEffect(() => {
    if (location.state?.formData) {
      setFormData(location.state.formData);
    }
  }, [location.state]);

  // 輪詢查詢圖片生成狀態
  useEffect(() => {
    let pollInterval = null;

    if (loading && generationStatus?.giftId) {
      pollInterval = setInterval(async () => {
        try {
          const response = await giftAPI.getGenerationStatus(generationStatus.giftId);
          const status = response.data;

          setGenerationStatus({
            ...generationStatus,
            status: status.status,
            retryCount: status.retry_count,
            error: status.error,
            queueInfo: status.queue_info
          });

          // 如果完成或失敗，停止輪詢並導航
          if (status.status === 'completed') {
            clearInterval(pollInterval);
            setLoading(false);
            navigate(`/confirm/${generationStatus.giftId}`);
          } else if (status.status === 'failed') {
            clearInterval(pollInterval);
            setLoading(false);
            setError(`圖片生成失敗: ${status.error || '未知錯誤'}`);
          }
        } catch (err) {
          console.error('輪詢狀態錯誤:', err);
        }
      }, 2000); // 每2秒查詢一次
    }

    return () => {
      if (pollInterval) {
        clearInterval(pollInterval);
      }
    };
  }, [loading, generationStatus, navigate]);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // 提交表單
      const submitResponse = await giftAPI.submitForm(formData);
      const giftId = submitResponse.data.gift_id;

      // 開始生成禮物圖片（非同步）
      setGenerationStatus({ giftId, status: 'processing', retryCount: 0 });
      await giftAPI.generateGift(giftId);

      // 輪詢機制會自動處理後續導航
    } catch (err) {
      console.error('提交錯誤:', err);
      console.error('錯誤詳情:', err.response);
      const errorMsg = err.response?.data?.error || err.message || '提交失敗，請稍後再試';
      setError(`錯誤: ${errorMsg}`);
      setLoading(false);
    }
  };

  // 動態顯示 loading 訊息
  const getLoadingMessage = () => {
    if (!generationStatus) return 'AI 正在努力畫畫中';

    if (generationStatus.status === 'processing') {
      if (generationStatus.retryCount > 0) {
        return `重試中 (第 ${generationStatus.retryCount} 次)`;
      }
      const queueInfo = generationStatus.queueInfo;
      if (queueInfo && queueInfo.available_slots === 0) {
        return `等候中... (目前 ${queueInfo.active_count} 人在使用)`;
      }
      return 'AI 正在努力畫畫中';
    }

    return 'AI 正在努力畫畫中';
  };

  return (
    <>
      {/* Loading 蓋板 */}
      {loading && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(102, 126, 234, 0.95)',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 9999,
          animation: 'fadeIn 0.3s ease-in'
        }}>
          <div style={{
            fontSize: '80px',
            marginBottom: '20px',
            animation: 'bounce 1s ease-in-out infinite'
          }}>
            🎨
          </div>
          <h2 style={{
            color: 'white',
            fontSize: '28px',
            marginBottom: '10px',
            textAlign: 'center'
          }}>
            {getLoadingMessage()}
          </h2>
          <div style={{
            color: 'white',
            fontSize: '20px',
            display: 'flex',
            gap: '8px',
            animation: 'pulse 1.5s ease-in-out infinite'
          }}>
            <span>✨</span>
            <span>🖌️</span>
            <span>💝</span>
            <span>🎁</span>
            <span>✨</span>
          </div>
          <p style={{
            color: 'rgba(255, 255, 255, 0.9)',
            fontSize: '16px',
            marginTop: '20px'
          }}>
            請稍候片刻，馬上就好囉 (｡♥‿♥｡)
          </p>

          <style>{`
            @keyframes fadeIn {
              from { opacity: 0; }
              to { opacity: 1; }
            }

            @keyframes bounce {
              0%, 100% { transform: translateY(0); }
              50% { transform: translateY(-20px); }
            }

            @keyframes pulse {
              0%, 100% { opacity: 1; transform: scale(1); }
              50% { opacity: 0.7; transform: scale(1.1); }
            }
          `}</style>
        </div>
      )}

      <div className="container">
        <h1>🎁 交換禮物遊戲</h1>

        <div className="card">
          <h2>請填寫你的禮物資訊</h2>

          {error && <div className="error">{error}</div>}

          <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="player_name">1. 你的名字 *</label>
            <input
              type="text"
              id="player_name"
              name="player_name"
              value={formData.player_name}
              onChange={handleChange}
              required
              placeholder="請輸入你的名字"
            />
          </div>

          <div className="form-group">
            <label htmlFor="gift_name">2. 這個禮物是什麼？*</label>
            <input
              type="text"
              id="gift_name"
              name="gift_name"
              value={formData.gift_name}
              onChange={handleChange}
              required
              placeholder="例如：保溫杯、藍牙耳機、香氛蠟燭..."
            />
          </div>
          <div className="form-group">
            <label htmlFor="happiness_reason">3. 收到的人會因為這禮物而發出什麼讚嘆？*</label>
            <textarea
              id="happiness_reason"
              name="happiness_reason"
              value={formData.happiness_reason}
              onChange={handleChange}
              required
              placeholder="例如：哇！好實用！、太貼心了！、這正是我需要的！..."
            />
          </div>
          <div className="form-group">
            <label htmlFor="appearance">4. 你這個禮物的外型或材質是什麼？*</label>
            <textarea
              id="appearance"
              name="appearance"
              value={formData.appearance}
              onChange={handleChange}
              required
              placeholder="例如：長方形的金屬盒、圓形的陶瓷杯、柔軟的棉質物品..."
            />
          </div>

          <div className="form-group">
            <label htmlFor="who_likes">5. 你這個禮物通常是什麼人會喜歡的？*</label>
            <textarea
              id="who_likes"
              name="who_likes"
              value={formData.who_likes}
              onChange={handleChange}
              required
              placeholder="例如：喜歡閱讀的人、愛運動的人、咖啡愛好者..."
            />
          </div>

          <div className="form-group">
            <label htmlFor="usage_time">6. 你這個禮物通常是在什麼時候使用？*</label>
            <textarea
              id="usage_time"
              name="usage_time"
              value={formData.usage_time}
              onChange={handleChange}
              required
              placeholder="例如：早上起床時、下班放鬆時、運動後、睡前放鬆時..."
            />
          </div>



          <div className="button-group">
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? '處理中...' : '提交並生成禮物圖片'}
            </button>
          </div>
        </form>
      </div>
    </div>
    </>
  );
}

export default FormPage;
