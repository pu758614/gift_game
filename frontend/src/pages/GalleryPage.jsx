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
  const animationFrameRef = useRef(null);
  const ballsRef = useRef([]);

  useEffect(() => {
    loadGifts();

    // 每3秒檢查一次新禮物
    pollingIntervalRef.current = setInterval(() => {
      checkForNewGifts();
    }, 3000);

    // 啟動物理引擎
    const animate = () => {
      updateBallPositions();
      detectCollisions();
      animationFrameRef.current = requestAnimationFrame(animate);
    };
    animate();

    // 清理函數
    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, []);

  const loadGifts = async () => {
    try {
      const response = await giftAPI.getAllGifts();
      const minSpeed = 0.3;
      const maxSpeed = 0.8;

      // 為每個禮物創建物理泡泡
      const giftsWithPhysics = response.data.gifts.map((gift, index) => {
        const ballRadius = 80 + Math.random() * 40; // 泡泡半徑 80-120
        const minX = ballRadius;
        const maxX = window.innerWidth - ballRadius;
        const minY = ballRadius;
        const maxY = window.innerHeight - ballRadius;

        return {
          ...gift,
          x: Math.random() * (maxX - minX) + minX,
          y: Math.random() * (maxY - minY) + minY,
          speed: Math.random() * (maxSpeed - minSpeed) + minSpeed,
          angle: Math.random() * 360,
          acc: 0.005 * (Math.random() < 0.5 ? -1 : 1), // 加速度減小
          canCollide: false, // 初始不能碰撞,直到不與其他球重疊
          size: ballRadius * 2,
          isNew: false,
        };
      });

      setGifts(giftsWithPhysics);
      ballsRef.current = giftsWithPhysics;

      // 記錄初始載入的禮物 ID
      knownGiftIdsRef.current = new Set(giftsWithPhysics.map(g => g.id));
    } catch (err) {
      setError('載入失敗,請稍後再試');
    } finally {
      setLoading(false);
    }
  };

  const checkForNewGifts = async () => {
    try {
      const response = await giftAPI.getAllGifts();
      const newGifts = response.data.gifts.filter(gift => !knownGiftIdsRef.current.has(gift.id));

      if (newGifts.length > 0) {
        const minSpeed = 0.3;
        const maxSpeed = 0.8;

        const newGiftsWithPhysics = newGifts.map((gift) => {
          const ballRadius = 80 + Math.random() * 40; // 泡泡半徑 80-120
          const minX = ballRadius;
          const maxX = window.innerWidth - ballRadius;
          const minY = ballRadius;
          const maxY = window.innerHeight - ballRadius;

          return {
            ...gift,
            x: Math.random() * (maxX - minX) + minX,
            y: Math.random() * (maxY - minY) + minY,
            speed: Math.random() * (maxSpeed - minSpeed) + minSpeed,
            angle: Math.random() * 360,
            acc: 0.005 * (Math.random() < 0.5 ? -1 : 1),
            canCollide: false,
            size: ballRadius * 2,
            isNew: true,
          };
        });

        const updatedGifts = [...ballsRef.current, ...newGiftsWithPhysics];
        setGifts(updatedGifts);
        ballsRef.current = updatedGifts;

        newGifts.forEach(gift => {
          knownGiftIdsRef.current.add(gift.id);
        });

        const newIds = new Set(newGifts.map(g => g.id));
        setNewGiftIds(newIds);

        setTimeout(() => {
          setNewGiftIds(new Set());
          const updated = ballsRef.current.map(g => ({ ...g, isNew: false }));
          setGifts(updated);
          ballsRef.current = updated;
        }, 3000);
      }
    } catch (err) {
      console.error('檢查新禮物失敗:', err);
    }
  };

  const updateBallPositions = () => {
    const minSpeed = 0.3;
    const maxSpeed = 0.8;

    const newBalls = ballsRef.current.map(ball => {
      const updatedBall = { ...ball };
      const ballRadius = updatedBall.size / 2; // 使用球的實際半徑

      // 處理加速度和速度變化
      if (updatedBall.acc) {
        if (updatedBall.acc > 0 && updatedBall.speed >= maxSpeed) {
          updatedBall.acc = updatedBall.acc * -1;
        } else if (updatedBall.acc < 0 && updatedBall.speed <= 0.1) {
          updatedBall.angle = Math.random() * 360;
          updatedBall.acc = updatedBall.acc * -1;
        }
        updatedBall.speed = updatedBall.speed + updatedBall.acc;
      }

      // 檢查牆壁碰撞
      if (
        updatedBall.x - ballRadius - updatedBall.speed < 0 ||
        updatedBall.x + ballRadius + updatedBall.speed > window.innerWidth
      ) {
        updatedBall.angle = 180 - updatedBall.angle;
      }
      if (
        updatedBall.y - ballRadius - updatedBall.speed < 0 ||
        updatedBall.y + ballRadius + updatedBall.speed > window.innerHeight
      ) {
        updatedBall.angle = 360 - updatedBall.angle;
      }

      // 修正角度範圍
      updatedBall.angle = ((updatedBall.angle % 360) + 360) % 360;

      // 更新位置
      updatedBall.x = updatedBall.x + updatedBall.speed * Math.cos((updatedBall.angle * Math.PI) / 180);
      updatedBall.y = updatedBall.y + updatedBall.speed * Math.sin((updatedBall.angle * Math.PI) / 180);

      // 檢查是否可以開始碰撞
      if (!updatedBall.canCollide) {
        updatedBall.canCollide = enableCollision(updatedBall, ballsRef.current);
      }

      return updatedBall;
    });

    ballsRef.current = newBalls;
    setGifts(newBalls);
  };

  const enableCollision = (ball, allBalls) => {
    return !allBalls.find((otherBall) => {
      if (ball.id === otherBall.id) return false;

      const ballDist = Math.sqrt(
        Math.pow(ball.x - otherBall.x, 2) + Math.pow(ball.y - otherBall.y, 2)
      );

      const ballRadius = ball.size / 2;
      const otherBallRadius = otherBall.size / 2;

      return ballDist <= ballRadius + otherBallRadius;
    });
  };

  const detectCollisions = () => {
    const newBalls = [...ballsRef.current];

    for (let i = 0; i < newBalls.length; i++) {
      const ball = newBalls[i];
      if (!ball.canCollide) continue;
      const ballRadius = ball.size / 2;

      for (let j = i + 1; j < newBalls.length; j++) {
        const otherBall = newBalls[j];
        if (!otherBall.canCollide) continue;
        const otherBallRadius = otherBall.size / 2;

        const ballDist = Math.sqrt(
          Math.pow(ball.x - otherBall.x, 2) + Math.pow(ball.y - otherBall.y, 2)
        );

        if (ballDist <= ballRadius + otherBallRadius) {
          // 碰撞!計算新的速度和角度
          const ballAngleRad = (ball.angle * Math.PI) / 180;
          const otherBallAngleRad = (otherBall.angle * Math.PI) / 180;
          const hitAngle = Math.atan2(ball.y - otherBall.y, ball.x - otherBall.x);

          const ballXspeed =
            otherBall.speed * Math.cos(otherBallAngleRad - hitAngle) * Math.cos(hitAngle) +
            ball.speed * Math.sin(ballAngleRad - hitAngle) * Math.sin(hitAngle);
          const ballYspeed =
            otherBall.speed * Math.cos(otherBallAngleRad - hitAngle) * Math.sin(hitAngle) +
            ball.speed * Math.sin(ballAngleRad - hitAngle) * Math.cos(hitAngle);

          const otherBallXspeed =
            ball.speed * Math.cos(ballAngleRad - hitAngle) * Math.cos(hitAngle) +
            otherBall.speed * Math.sin(otherBallAngleRad - hitAngle) * Math.sin(hitAngle);
          const otherBallYspeed =
            ball.speed * Math.cos(ballAngleRad - hitAngle) * Math.sin(hitAngle) +
            otherBall.speed * Math.sin(otherBallAngleRad - hitAngle) * Math.cos(hitAngle);

          const ballAngle = (Math.atan2(ballYspeed, ballXspeed) * 180) / Math.PI;
          const otherBallAngle = (Math.atan2(otherBallYspeed, otherBallXspeed) * 180) / Math.PI;

          const ballSpeed = Math.sqrt(Math.pow(ballXspeed, 2) + Math.pow(ballYspeed, 2));
          const otherBallSpeed = Math.sqrt(Math.pow(otherBallXspeed, 2) + Math.pow(otherBallYspeed, 2));

          newBalls[i] = { ...ball, angle: ballAngle, speed: ballSpeed, canCollide: false };
          newBalls[j] = { ...otherBall, angle: otherBallAngle, speed: otherBallSpeed, canCollide: false };
        }
      }
    }

    ballsRef.current = newBalls;
    setGifts(newBalls);
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

      {/* 填寫禮物表單 QR Code */}
      <div style={{
        position: 'fixed',
        top: '20px',
        left: '20px',
        background: 'rgba(255, 255, 255, 0.95)',
        padding: '13px',
        borderRadius: '10px',
        boxShadow: '0 4px 15px rgba(0, 0, 0, 0.2)',
        zIndex: 100,
        textAlign: 'center'
      }}>
        <div style={{
          fontSize: '12px',
          fontWeight: 'bold',
          color: '#667eea',
          marginTop: '7px'
        }}>
          📝 填寫禮物表單
        </div>
        <br />
        <img
          src="/form_qr.png"
          alt="填寫禮物表單 QR Code"
          style={{
            width: '133px',
            height: '133px',
            display: 'block',
            marginBottom: '7px',
            borderRadius: '5px'
          }}
        />

      </div>

      {/* WiFi 資訊 */}
      <div style={{
        position: 'fixed',
        top: '20px',
        right: '20px',
        background: 'rgba(255, 255, 255, 0.95)',
        padding: '13px',
        borderRadius: '10px',
        boxShadow: '0 4px 15px rgba(0, 0, 0, 0.2)',
        zIndex: 100,
        textAlign: 'center'
      }}>
        <div style={{ fontWeight: 'bold', marginBottom: '10px', color: '#667eea', fontSize: '15px' }}>
          📶 WiFi
        </div>
        <img
          src="/wifi.jpg"
          alt="WiFi QR Code"
          style={{
            width: '133px',
            height: '133px',
            display: 'block',
            margin: '0 auto 10px',
            borderRadius: '5px'
          }}
        />
        <div style={{ fontSize: '12px', fontFamily: 'monospace', lineHeight: '1.6', color: '#333' }}>
          <div style={{ fontSize: '12px' }}><strong>名稱:</strong> DoDo</div>
          <div style={{ fontSize: '12px' }}><strong>密碼:</strong> 073419215</div>
        </div>
      </div>

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
            return (
              <div
                key={gift.id}
                className={`bubble-ball ${gift.isNew ? 'new-gift' : ''}`}
                style={{
                  position: 'absolute',
                  left: `${gift.x - gift.size / 2}px`,
                  top: `${gift.y - gift.size / 2}px`,
                  width: `${gift.size}px`,
                  height: `${gift.size}px`,
                  cursor: 'pointer',
                  transition: 'filter 0.3s ease',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  pointerEvents: 'none',
                }}
              >
                <div
                  style={{
                    position: 'relative',
                    width: '100%',
                    height: '100%',
                    borderRadius: '50%',
                    background: `url(${getFullImageUrl(gift.image_url)}) no-repeat center center`,
                    backgroundSize: 'cover',
                    boxShadow: gift.isNew
                      ? '0 0 40px rgba(255, 215, 0, 1), 0 0 60px rgba(255, 255, 255, 0.8), inset 0 0 60px rgba(255, 255, 255, 0.3)'
                      : '0 8px 30px rgba(0, 0, 0, 0.3), inset 0 0 40px rgba(255, 255, 255, 0.2)',
                    border: gift.is_exchanged ? '4px solid #FFD700' : '4px solid rgba(255, 255, 255, 0.5)',
                    animation: gift.isNew ? 'popIn 0.5s ease-out' : 'none',
                  }}
                >
                  {/* 泡泡光澤效果 */}
                  <div style={{
                    position: 'absolute',
                    top: '15%',
                    left: '20%',
                    width: '40%',
                    height: '40%',
                    background: 'radial-gradient(circle at 30% 30%, rgba(255, 255, 255, 0.8), transparent 50%)',
                    borderRadius: '50%',
                    pointerEvents: 'none',
                  }} />


                </div>
              </div>
            );
          })}
        </div>
      )}

      <style>{`
        @keyframes popIn {
          0% {
            transform: scale(0);
            opacity: 0;
          }
          50% {
            transform: scale(1.2);
          }
          100% {
            transform: scale(1);
            opacity: 1;
          }
        }

        .bubble-ball:hover {
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
