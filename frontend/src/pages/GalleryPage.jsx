import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { giftAPI, getFullImageUrl } from '../api';

function GalleryPage() {
  const navigate = useNavigate();
  const [gifts, setGifts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [newGiftIds, setNewGiftIds] = useState(new Set());
  const pollingIntervalRef = useRef(null);
  const knownGiftIdsRef = useRef(new Set());

  useEffect(() => {
    loadGifts();

    // 每3秒檢查一次新禮物
    pollingIntervalRef.current = setInterval(() => {
      checkForNewGifts();
    }, 3000);

    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
    };
  }, []);

  const loadGifts = async () => {
    try {
      const response = await giftAPI.getAllGifts();
      // 為每個禮物添加隨機位置和動畫參數
      const giftsWithAnimation = response.data.gifts.map((gift, index) => ({
        ...gift,
        x: Math.random() * 80 + 10, // 10-90% 避免邊緣
        y: Math.random() * 80 + 10,
        size: Math.random() * 80 + 130, // 130-210px (增大)
        duration: Math.random() * 8 + 6, // 6-14秒
        delay: index * 0.3, // 錯開動畫
        // 為每個泡泡生成隨機移動路徑
        path: Array.from({length: 5}, () => ({
          x: (Math.random() - 0.5) * 200,
          y: (Math.random() - 0.5) * 200,
          rotate: (Math.random() - 0.5) * 20
        })),
        isNew: false,
      }));
      setGifts(giftsWithAnimation);

      // 記錄初始載入的禮物 ID
      knownGiftIdsRef.current = new Set(giftsWithAnimation.map(g => g.id));
    } catch (err) {
      setError('載入失敗，請稍後再試');
    } finally {
      setLoading(false);
    }
  };

  const checkForNewGifts = async () => {
    try {
      const response = await giftAPI.getAllGifts();
      // 使用 ref 中記錄的已知禮物 ID
      const newGifts = response.data.gifts.filter(gift => !knownGiftIdsRef.current.has(gift.id));

      if (newGifts.length > 0) {
        const newGiftsWithAnimation = newGifts.map((gift, index) => ({
          ...gift,
          x: Math.random() * 80 + 10,
          y: Math.random() * 80 + 10,
          size: Math.random() * 80 + 130,
          duration: Math.random() * 8 + 6,
          delay: 0,
          path: Array.from({length: 5}, () => ({
            x: (Math.random() - 0.5) * 200,
            y: (Math.random() - 0.5) * 200,
            rotate: (Math.random() - 0.5) * 20
          })),
          isNew: true,
        }));

        setGifts(prev => [...prev, ...newGiftsWithAnimation]);

        // 更新已知禮物 ID 集合
        newGifts.forEach(gift => {
          knownGiftIdsRef.current.add(gift.id);
        });

        // 標記新禮物ID
        const newIds = new Set(newGifts.map(g => g.id));
        setNewGiftIds(newIds);

        // 3秒後移除新禮物標記
        setTimeout(() => {
          setNewGiftIds(new Set());
          setGifts(prev => prev.map(g => ({ ...g, isNew: false })));
        }, 3000);
      }
    } catch (err) {
      console.error('檢查新禮物失敗:', err);
    }
  };

  const handleStartExchange = () => {
    navigate('/exchange');
  };

  const handleAddNewGift = () => {
    navigate('/');
  };

  if (loading) {
    return <div className="loading">載入中...</div>;
  }

  return (
    <div style={{
      position: 'relative',
      width: '100vw',
      height: '100vh',
      overflow: 'hidden',
      backgroundImage: 'url(/background.png)',
      backgroundSize: 'cover',
      backgroundPosition: 'center',
      backgroundRepeat: 'no-repeat'
    }}>
      {/* 半透明白色遮罩讓背景顏色淡化 */}
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'rgba(255, 255, 255, 0.4)',
        pointerEvents: 'none'
      }} />

      {error && (
        <div className="error" style={{ position: 'fixed', top: '100px', left: '50%', transform: 'translateX(-50%)', zIndex: 100 }}>
          {error}
        </div>
      )}

      {loading ? (
        <div className="loading" style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)' }}>
          載入中...
        </div>
      ) : gifts.length === 0 ? (
        <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', textAlign: 'center', color: 'white', fontSize: '20px' }}>
          還沒有任何禮物，快去新增一個吧！
        </div>
      ) : (
        <div style={{ position: 'relative', width: '100%', height: '100%' }}>
          {gifts.map((gift) => {
            const animationName = `float-${gift.id}`;
            return (
              <div
                key={gift.id}
                className={`floating-bubble ${gift.isNew ? 'new-gift' : ''}`}
                style={{
                  position: 'absolute',
                  left: `${gift.x}%`,
                  top: `${gift.y}%`,
                  animation: gift.isNew
                    ? `popIn 0.5s ease-out, ${animationName} ${gift.duration}s ease-in-out infinite 0.5s`
                    : `${animationName} ${gift.duration}s ease-in-out infinite`,
                  animationDelay: gift.isNew ? '0s' : `${gift.delay}s`,
                  cursor: 'pointer',
                  transition: 'transform 0.3s ease',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  gap: '10px',
                }}
                onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.1)'}
                onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
              >
                <img
                  src={getFullImageUrl(gift.image_url)}
                  alt="禮物"
                  style={{
                    width: `${gift.size}px`,
                    height: `${gift.size}px`,
                    objectFit: 'cover',
                    borderRadius: '50%',
                    boxShadow: gift.isNew
                      ? '0 0 40px rgba(255, 215, 0, 1), 0 0 60px rgba(255, 255, 255, 0.8)'
                      : '0 8px 30px rgba(255, 215, 0, 0.4), 0 0 20px rgba(255, 255, 255, 0.3)',
                    border: gift.is_exchanged ? '5px solid #FFD700' : '5px solid rgba(255, 255, 255, 0.9)',
                  }}
                />
                <div style={{
                  maxWidth: `${gift.size}px`,
                  padding: '8px 12px',
                  background: 'rgba(255, 255, 255, 0.95)',
                  borderRadius: '12px',
                  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
                  fontSize: '14px',
                  color: '#333',
                  textAlign: 'center',
                  lineHeight: '1.4',
                  fontWeight: '500',
                }}>
                  {gift.happiness_reason}
                </div>
              </div>
            );
          })}
        </div>
      )}

      <style>{`
        ${gifts.map(gift => `
          @keyframes float-${gift.id} {
            0%, 100% {
              transform: translate(0, 0) rotate(0deg);
            }
            20% {
              transform: translate(${gift.path[0].x}px, ${gift.path[0].y}px) rotate(${gift.path[0].rotate}deg);
            }
            40% {
              transform: translate(${gift.path[1].x}px, ${gift.path[1].y}px) rotate(${gift.path[1].rotate}deg);
            }
            60% {
              transform: translate(${gift.path[2].x}px, ${gift.path[2].y}px) rotate(${gift.path[2].rotate}deg);
            }
            80% {
              transform: translate(${gift.path[3].x}px, ${gift.path[3].y}px) rotate(${gift.path[3].rotate}deg);
            }
          }
        `).join('')}

        @keyframes popIn {
          0% {
            transform: scale(0) rotate(0deg);
            opacity: 0;
          }
          50% {
            transform: scale(1.3) rotate(180deg);
          }
          100% {
            transform: scale(1) rotate(360deg);
            opacity: 1;
          }
        }

        .floating-bubble:hover {
          z-index: 10;
          filter: brightness(1.2) drop-shadow(0 0 20px rgba(255, 215, 0, 0.8));
        }

        .new-gift {
          z-index: 20;
        }
      `}</style>
    </div>
  );
}

export default GalleryPage;
