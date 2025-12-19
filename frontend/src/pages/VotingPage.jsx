import React, { useState, useEffect } from 'react';
import { getFingerprint } from '../utils/fingerprint';
import { giftAPI, getFullImageUrl } from '../api';
import './VotingPage.css';

const VotingPage = () => {
  const [gifts, setGifts] = useState([]);
  const [votingStatus, setVotingStatus] = useState({
    creative: { voted_gift_ids: [], remaining_votes: 3 },
    blessing: { voted_gift_ids: [], remaining_votes: 3 }
  });
  const [fingerprint, setFingerprint] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // 當前選擇的投票
  const [selectedCreative, setSelectedCreative] = useState([]);
  const [selectedBlessing, setSelectedBlessing] = useState([]);
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);

  useEffect(() => {
    initializePage();
  }, []);

  const initializePage = async () => {
    console.log('=== Initializing Voting Page ===');
    try {
      setLoading(true);
      setError('');

      // 生成指紋
      console.log('Generating fingerprint...');
      const fp = await getFingerprint();
      console.log('Fingerprint:', fp);
      setFingerprint(fp);

      // 獲取投票結果（所有禮物）
      console.log('Fetching voting results...');
      const giftsResponse = await giftAPI.getVotingResults();
      console.log('Gifts response:', giftsResponse);
      console.log('Gifts response data:', giftsResponse.data);

      const giftsData = giftsResponse.data?.gifts || [];
      console.log('Extracted gifts data:', giftsData, 'Length:', giftsData.length);
      setGifts(giftsData);

      // 獲取當前用戶的投票狀態
      console.log('Fetching voting status...');
      const statusResponse = await giftAPI.getVotingStatus(fp);
      console.log('Status response:', statusResponse);
      const status = statusResponse.data;
      console.log('Voting status:', status);

      // 確保狀態結構正確
      if (status && status.creative && status.blessing) {
        setVotingStatus(status);
      } else {
        console.warn('Invalid voting status structure:', status);
        // 使用默認值
        setVotingStatus({
          creative: { voted_gift_ids: [], remaining_votes: 3 },
          blessing: { voted_gift_ids: [], remaining_votes: 3 }
        });
      }

      console.log('=== Initialization Complete ===');
      setLoading(false);
    } catch (err) {
      console.error('Failed to initialize voting page:', err);
      console.error('Error details:', err.message, err.response);
      setError(`載入投票頁面失敗: ${err.message}`);
      setLoading(false);
    }
  };

  // 切換選擇禮物
  const toggleSelection = (giftId, awardType) => {
    if (awardType === 'creative') {
      if (selectedCreative.includes(giftId)) {
        setSelectedCreative(selectedCreative.filter(id => id !== giftId));
      } else {
        if (selectedCreative.length >= 3) {
          alert('最多只能選擇 3 個禮物');
          return;
        }
        setSelectedCreative([...selectedCreative, giftId]);
      }
    } else {
      if (selectedBlessing.includes(giftId)) {
        setSelectedBlessing(selectedBlessing.filter(id => id !== giftId));
      } else {
        if (selectedBlessing.length >= 3) {
          alert('最多只能選擇 3 個禮物');
          return;
        }
        setSelectedBlessing([...selectedBlessing, giftId]);
      }
    }
  };

  // 顯示確認對話框
  const handleSubmitClick = () => {
    if (selectedCreative.length === 0 && selectedBlessing.length === 0) {
      alert('請至少選擇一個禮物進行投票');
      return;
    }
    setShowConfirmDialog(true);
  };

  // 確認送出投票
  const confirmSubmitVotes = async () => {
    try {
      setShowConfirmDialog(false);
      setLoading(true);

      // 提交所有選擇的投票
      for (const giftId of selectedCreative) {
        await giftAPI.submitVote(giftId, 'creative', fingerprint);
      }
      for (const giftId of selectedBlessing) {
        await giftAPI.submitVote(giftId, 'blessing', fingerprint);
      }

      // 清空選擇
      setSelectedCreative([]);
      setSelectedBlessing([]);

      // 重新載入頁面資料
      await initializePage();

      alert('投票成功！');
    } catch (err) {
      console.error('Vote failed:', err);
      alert(err.response?.data?.error || '投票失敗');
      setLoading(false);
    }
  };

  // 取消確認
  const cancelSubmit = () => {
    setShowConfirmDialog(false);
  };

  if (loading) {
    return <div className="voting-page"><div className="loading">載入中...</div></div>;
  }

  if (error) {
    return <div className="voting-page"><div className="error">{error}</div></div>;
  }

  // 渲染禮物卡片
  const renderGiftCard = (gift, awardType) => {
    const isSelected = awardType === 'creative'
      ? selectedCreative.includes(gift.id)
      : selectedBlessing.includes(gift.id);

    const isAlreadyVoted = votingStatus[awardType].voted_gift_ids.includes(gift.id);

    return (
      <div
        key={gift.id}
        className={`gift-card ${isSelected ? 'selected' : ''} ${isAlreadyVoted ? 'already-voted' : ''}`}
        onClick={() => !isAlreadyVoted && toggleSelection(gift.id, awardType)}
      >
        <div className="gift-image-container">
          <img
            src={getFullImageUrl(gift.image_url)}
            alt={gift.gift_name || '禮物'}
            className="gift-image"
          />
          {isAlreadyVoted && (
            <div className="already-voted-badge">✓ 已投過</div>
          )}
          {isSelected && !isAlreadyVoted && (
            <div className="selected-badge">✓ 已選擇</div>
          )}
        </div>

        <div className="gift-info">
          <h3 className="gift-name">{gift.gift_name || '神秘禮物'}</h3>
          <p className="gift-player">{gift.player_name} 的禮物</p>
        </div>
      </div>
    );
  };

  return (
    <div className="voting-page">
      <header className="voting-header">
        <h1>🎁 禮物投票</h1>
        <p className="instruction">請選擇您喜歡的禮物，最後按「送出投票」確認</p>
      </header>

      {/* 最佳創意獎區域 */}
      <section className="voting-section creative-section">
        <div className="section-header">
          <h2>🎨 最佳創意獎</h2>
          <div className="selection-status">
            已選擇: {selectedCreative.length}/3
            {votingStatus.creative.remaining_votes < 3 && (
              <span className="voted-info"> (已投過 {3 - votingStatus.creative.remaining_votes} 票)</span>
            )}
          </div>
        </div>
        <div className="gifts-grid">
          {gifts.map(gift => renderGiftCard(gift, 'creative'))}
        </div>
      </section>

      {/* 最佳祝福獎區域 */}
      <section className="voting-section blessing-section">
        <div className="section-header">
          <h2>💝 最佳祝福獎</h2>
          <div className="selection-status">
            已選擇: {selectedBlessing.length}/3
            {votingStatus.blessing.remaining_votes < 3 && (
              <span className="voted-info"> (已投過 {3 - votingStatus.blessing.remaining_votes} 票)</span>
            )}
          </div>
        </div>
        <div className="gifts-grid">
          {gifts.map(gift => renderGiftCard(gift, 'blessing'))}
        </div>
      </section>

      {/* 送出按鈕 */}
      {(selectedCreative.length > 0 || selectedBlessing.length > 0) && (
        <div className="submit-container">
          <button className="submit-btn" onClick={handleSubmitClick}>
            送出投票
          </button>
        </div>
      )}

      {/* 確認對話框 */}
      {showConfirmDialog && (
        <div className="confirm-dialog-overlay" onClick={cancelSubmit}>
          <div className="confirm-dialog" onClick={(e) => e.stopPropagation()}>
            <h3>確認投票</h3>

            {selectedCreative.length > 0 && (
              <div className="confirm-section">
                <h4>🎨 最佳創意獎 ({selectedCreative.length} 票)</h4>
                <ul>
                  {selectedCreative.map(giftId => {
                    const gift = gifts.find(g => g.id === giftId);
                    return <li key={giftId}>{gift?.gift_name || '神秘禮物'} - {gift?.player_name}</li>;
                  })}
                </ul>
              </div>
            )}

            {selectedBlessing.length > 0 && (
              <div className="confirm-section">
                <h4>💝 最佳祝福獎 ({selectedBlessing.length} 票)</h4>
                <ul>
                  {selectedBlessing.map(giftId => {
                    const gift = gifts.find(g => g.id === giftId);
                    return <li key={giftId}>{gift?.gift_name || '神秘禮物'} - {gift?.player_name}</li>;
                  })}
                </ul>
              </div>
            )}

            <div className="confirm-buttons">
              <button className="cancel-btn" onClick={cancelSubmit}>取消</button>
              <button className="confirm-btn" onClick={confirmSubmitVotes}>確認投票</button>
            </div>
          </div>
        </div>
      )}

      {gifts.length === 0 && !loading && (
        <div className="no-gifts">
          <p>目前沒有可投票的禮物</p>
        </div>
      )}
    </div>
  );
};

export default VotingPage;
