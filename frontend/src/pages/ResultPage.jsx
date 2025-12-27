import React, { useState, useEffect } from 'react';
import { giftAPI, getFullImageUrl } from '../api';
import './ResultPage.css';

const ResultPage = () => {
  const [results, setResults] = useState([]);
  const [stage, setStage] = useState('ready'); // ready, creative-show, creative-countdown, creative-ranking, blessing-show, blessing-countdown, blessing-ranking
  const [creativeTop3, setCreativeTop3] = useState([]);
  const [blessingTop3, setBlessingTop3] = useState([]);
  const [countingIndex, setCountingIndex] = useState(-1);
  const [animatedVotes, setAnimatedVotes] = useState({});
  const [showRanking, setShowRanking] = useState(false);

  useEffect(() => {
    loadResults();
  }, []);

  const loadResults = async () => {
    try {
      const response = await giftAPI.getVotingResults();
      const gifts = response.data.gifts || [];
      setResults(gifts);

      // 計算最佳創意獎前三名
      const creativeRanking = [...gifts]
        .sort((a, b) => b.creative_votes - a.creative_votes)
        .slice(0, 3);
      setCreativeTop3(creativeRanking);

      // 計算最佳祝福獎前三名
      const blessingRanking = [...gifts]
        .sort((a, b) => b.blessing_votes - a.blessing_votes)
        .slice(0, 3);
      setBlessingTop3(blessingRanking);
    } catch (err) {
      console.error('Failed to load results:', err);
    }
  };

  const startCreativeReveal = () => {
    setStage('creative-show');
    setShowRanking(false);
    setAnimatedVotes({});
    // 2秒後開始計票
    setTimeout(() => {
      setStage('creative-countdown');
      setCountingIndex(0);
    }, 2000);
  };

  const startBlessingReveal = () => {
    setStage('blessing-show');
    setShowRanking(false);
    setAnimatedVotes({});
    // 2秒後開始計票
    setTimeout(() => {
      setStage('blessing-countdown');
      setCountingIndex(0);
    }, 2000);
  };

  // 數字滾動動畫
  useEffect(() => {
    if (stage === 'creative-countdown' && countingIndex >= 0 && countingIndex < creativeTop3.length) {
      const gift = creativeTop3[countingIndex];
      const targetVotes = gift.creative_votes;

      let currentVotes = 0;
      const duration = 1000; // 1秒
      const steps = 50;
      const increment = targetVotes / steps;
      const stepDuration = duration / steps;

      const interval = setInterval(() => {
        currentVotes += increment;
        if (currentVotes >= targetVotes) {
          currentVotes = targetVotes;
          clearInterval(interval);

          // 延遲後顯示下一個，或顯示排名
          setTimeout(() => {
            if (countingIndex < creativeTop3.length - 1) {
              setCountingIndex(countingIndex + 1);
            } else {
              // 所有票數都顯示完畢，開始顯示排名
              setStage('creative-ranking');
              setTimeout(() => {
                setShowRanking(true);
              }, 500);
            }
          }, 800);
        }

        setAnimatedVotes(prev => ({
          ...prev,
          [`creative-${gift.id}`]: Math.floor(currentVotes)
        }));
      }, stepDuration);

      return () => clearInterval(interval);
    }
  }, [stage, countingIndex, creativeTop3]);

  // 祝福獎數字滾動
  useEffect(() => {
    if (stage === 'blessing-countdown' && countingIndex >= 0 && countingIndex < blessingTop3.length) {
      const gift = blessingTop3[countingIndex];
      const targetVotes = gift.blessing_votes;

      let currentVotes = 0;
      const duration = 1000;
      const steps = 50;
      const increment = targetVotes / steps;
      const stepDuration = duration / steps;

      const interval = setInterval(() => {
        currentVotes += increment;
        if (currentVotes >= targetVotes) {
          currentVotes = targetVotes;
          clearInterval(interval);

          setTimeout(() => {
            if (countingIndex < blessingTop3.length - 1) {
              setCountingIndex(countingIndex + 1);
            } else {
              // 所有票數都顯示完畢，開始顯示排名
              setStage('blessing-ranking');
              setTimeout(() => {
                setShowRanking(true);
              }, 500);
            }
          }, 800);
        }

        setAnimatedVotes(prev => ({
          ...prev,
          [`blessing-${gift.id}`]: Math.floor(currentVotes)
        }));
      }, stepDuration);

      return () => clearInterval(interval);
    }
  }, [stage, countingIndex, blessingTop3]);

  const renderRankBadge = (rank) => {
    const badges = ['🥇', '🥈', '🥉'];
    const colors = ['#FFD700', '#C0C0C0', '#CD7F32'];
    return (
      <div className="rank-badge" style={{ backgroundColor: colors[rank] }}>
        {badges[rank]}
      </div>
    );
  };

  const renderCreativeResults = () => {
    const isShowStage = stage === 'creative-show';
    const isCountingStage = stage === 'creative-countdown';
    const isRankingStage = stage === 'creative-ranking';

    return (
      <div className="results-container creative-results">
        <h2 className="award-title creative-title">
          🎨 最佳創意獎
        </h2>

        <div className="podium">
          {creativeTop3.map((gift, index) => {
            const votes = animatedVotes[`creative-${gift.id}`] || 0;
            const showVotes = (isCountingStage && countingIndex >= index) || isRankingStage;
            const showRank = isRankingStage && showRanking;

            return (
              <div
                key={gift.id}
                className={`podium-item ${showRank ? `rank-${index + 1}` : 'no-rank'} reveal`}
                style={{ animationDelay: `${index * 0.3}s` }}
              >
                {showRank && renderRankBadge(index)}

                <div className="gift-image-wrapper">
                  <img
                    src={getFullImageUrl(gift.image_url)}
                    alt={gift.gift_name}
                    className="result-gift-image"
                  />
                </div>

                <h3 className="gift-name">{gift.gift_name || '神秘禮物'}</h3>
                <p className="gift-player">{gift.player_name}</p>

                {showVotes && (
                  <div className="vote-display">
                    <span className="vote-number">{votes}</span>
                    <span className="vote-label">票</span>
                  </div>
                )}

                {isShowStage && (
                  <div className="vote-placeholder">
                    <span className="question-mark">?</span>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {isRankingStage && showRanking && (
          <button className="continue-btn" onClick={startBlessingReveal}>
            繼續 → 最佳祝福獎
          </button>
        )}
      </div>
    );
  };

  const renderBlessingResults = () => {
    const isShowStage = stage === 'blessing-show';
    const isCountingStage = stage === 'blessing-countdown';
    const isRankingStage = stage === 'blessing-ranking';

    return (
      <div className="results-container blessing-results">
        <h2 className="award-title blessing-title">
          💝 最佳祝福獎
        </h2>

        <div className="podium">
          {blessingTop3.map((gift, index) => {
            const votes = animatedVotes[`blessing-${gift.id}`] || 0;
            const showVotes = (isCountingStage && countingIndex >= index) || isRankingStage;
            const showRank = isRankingStage && showRanking;

            return (
              <div
                key={gift.id}
                className={`podium-item ${showRank ? `rank-${index + 1}` : 'no-rank'} reveal`}
                style={{ animationDelay: `${index * 0.3}s` }}
              >
                {showRank && renderRankBadge(index)}

                <div className="gift-image-wrapper">
                  <img
                    src={getFullImageUrl(gift.image_url)}
                    alt={gift.gift_name}
                    className="result-gift-image"
                  />
                </div>

                <h3 className="gift-name">{gift.gift_name || '神秘禮物'}</h3>
                <p className="gift-player">{gift.player_name}</p>

                {showVotes && (
                  <div className="vote-display">
                    <span className="vote-number">{votes}</span>
                    <span className="vote-label">票</span>
                  </div>
                )}

                {isShowStage && (
                  <div className="vote-placeholder">
                    <span className="question-mark">?</span>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {isRankingStage && showRanking && (
          <div className="final-message">
            <h2>🎉 恭喜所有得獎者！🎉</h2>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="result-page">
      {stage === 'ready' && (
        <div className="start-screen">
          <h1 className="main-title">🎁 開獎時刻 🎁</h1>
          <p className="subtitle">準備揭曉投票結果</p>
          <button className="start-btn" onClick={startCreativeReveal}>
            🎊 開始開獎 🎊
          </button>
        </div>
      )}

      {(stage === 'creative-show' || stage === 'creative-countdown' || stage === 'creative-ranking') && renderCreativeResults()}

      {(stage === 'blessing-show' || stage === 'blessing-countdown' || stage === 'blessing-ranking') && renderBlessingResults()}
    </div>
  );
};

export default ResultPage;
