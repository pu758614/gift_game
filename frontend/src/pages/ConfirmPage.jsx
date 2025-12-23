import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { giftAPI, getFullImageUrl } from '../api';

function ConfirmPage() {
  const { giftId } = useParams();
  const navigate = useNavigate();

  const [gift, setGift] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [regenerating, setRegenerating] = useState(false);
  const [generationStatus, setGenerationStatus] = useState(null);

  useEffect(() => {
    loadGift();
  }, [giftId]);

  // 輪詢查詢圖片生成狀態
  useEffect(() => {
    let pollInterval = null;

    if (regenerating) {
      pollInterval = setInterval(async () => {
        try {
          const response = await giftAPI.getGenerationStatus(giftId);
          const status = response.data;

          setGenerationStatus({
            status: status.status,
            retryCount: status.retry_count,
            error: status.error,
            queueInfo: status.queue_info
          });

          // 如果完成或失敗，停止輪詢並重新載入
          if (status.status === 'completed') {
            clearInterval(pollInterval);
            setRegenerating(false);
            await loadGift();
          } else if (status.status === 'failed') {
            clearInterval(pollInterval);
            setRegenerating(false);
            setError(`圖片生成失敗: ${status.error || '未知錯誤'}`);
            await loadGift();
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
  }, [regenerating, giftId]);

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

  const handleRegenerate = async () => {
    try {
      setError('');
      setRegenerating(true);
      setGenerationStatus({ status: 'processing', retryCount: 0 });
      await giftAPI.regenerateGift(giftId);
      // 輪詢機制會自動處理後續
    } catch (err) {
      setError('重新生成失敗，請稍後再試');
      setRegenerating(false);
    }
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

  // 動態顯示 loading 訊息
  const getRegeneratingMessage = () => {
    if (!generationStatus) return '重新生成中...';

    if (generationStatus.status === 'processing') {
      if (generationStatus.retryCount > 0) {
        return `重試中 (第 ${generationStatus.retryCount} 次)`;
      }
      const queueInfo = generationStatus.queueInfo;
      if (queueInfo && queueInfo.available_slots === 0) {
        return `等候中... (目前 ${queueInfo.active_count} 人在使用)`;
      }
      return '重新生成中...';
    }

    return '重新生成中...';
  };

  return (
    <>
      {/* Regenerating Loading 覇板 */}
      {regenerating && (
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
            {getRegeneratingMessage()}
          </h2>
          <div style={{
            color: 'white',
            fontSize: '20px',
            display: 'flex',
            gap: '8px',
            animation: 'pulse 1.5s ease-in-out infinite'
          }}>
            <span>✨</span>
            <span>🖄️</span>
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
            disabled={regenerating}
          >
            ✏️ 重新編輯
          </button>
          {gift.image_generation_status === 'failed' && (
            <button
              className="btn btn-warning"
              onClick={handleRegenerate}
              disabled={regenerating}
              style={{ backgroundColor: '#f39c12', borderColor: '#e67e22' }}
            >
              🔄 重新生成
            </button>
          )}
          <button
            className="btn btn-primary"
            onClick={handleConfirm}
            disabled={regenerating || gift.image_generation_status === 'failed'}
          >
            ✓ 確認並上傳
          </button>
        </div>
      </div>
    </div>
    </>
  );
}

export default ConfirmPage;
