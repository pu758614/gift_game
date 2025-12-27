import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { getFullImageUrl } from '../api';
import './VoteCompletePage.css';

const VoteCompletePage = () => {
  const location = useLocation();
  const { votedGifts } = location.state || { votedGifts: { creative: [], blessing: [] } };


  return (
    <div className="vote-complete-page">
      <div className="complete-container">
        <div className="success-icon">✅</div>
        <h1>投票完畢！</h1>
        <p className="thank-you-text">感謝您的參與</p>

        {/* 最佳創意獎投票結果 */}
        {votedGifts.creative && votedGifts.creative.length > 0 && (
          <section className="voted-section">
            <h2>🎨 最佳創意獎</h2>
            <div className="voted-gifts-list">
              {votedGifts.creative.map((gift, index) => (
                <div key={gift.id} className="voted-gift-card">
                  <img
                    src={getFullImageUrl(gift.image_url)}
                    alt={gift.gift_name || '禮物'}
                    className="voted-gift-image"
                  />
                  <div className="voted-gift-info">
                    <h3>{gift.gift_name || '神秘禮物'}</h3>
                    <p>{gift.player_name} 的禮物</p>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* 最佳祝福獎投票結果 */}
        {votedGifts.blessing && votedGifts.blessing.length > 0 && (
          <section className="voted-section">
            <h2>💝 最佳祝福獎</h2>
            <div className="voted-gifts-list">
              {votedGifts.blessing.map((gift, index) => (
                <div key={gift.id} className="voted-gift-card">
                  <img
                    src={getFullImageUrl(gift.image_url)}
                    alt={gift.gift_name || '禮物'}
                    className="voted-gift-image"
                  />
                  <div className="voted-gift-info">
                    <h3>{gift.gift_name || '神秘禮物'}</h3>
                    <p>{gift.player_name} 的禮物</p>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}
      </div>
    </div>
  );
};

export default VoteCompletePage;
