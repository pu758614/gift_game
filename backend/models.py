from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Gift(db.Model):
    """禮物資料模型"""
    __tablename__ = 'gifts'

    id = db.Column(db.Integer, primary_key=True)
    player_name = db.Column(db.String(100), nullable=False)

    # 表單問題答案
    gift_name = db.Column(db.String(200), nullable=False)  # 禮物名稱
    appearance = db.Column(db.Text, nullable=False)  # 外型或材質
    who_likes = db.Column(db.Text, nullable=False)  # 什麼人會喜歡
    usage_time = db.Column(db.Text, nullable=False)  # 什麼時候使用
    happiness_reason = db.Column(db.Text, nullable=False)  # 幸福感

    # AI 生成結果
    ai_guess = db.Column(db.String(200))  # AI 猜測的禮物
    image_url = db.Column(db.String(500))  # 生成的圖片 URL

    # 圖片生成狀態追蹤
    # pending/processing/completed/failed
    image_generation_status = db.Column(db.String(20), default='pending')
    image_generation_started_at = db.Column(db.DateTime)  # 開始生成時間
    image_generation_completed_at = db.Column(db.DateTime)  # 完成生成時間
    image_generation_error = db.Column(db.Text)  # 錯誤訊息
    image_generation_retry_count = db.Column(db.Integer, default=0)  # 重試次數

    # 狀態
    is_confirmed = db.Column(db.Boolean, default=False)  # 是否確認圖片
    is_exchanged = db.Column(db.Boolean, default=False)  # 是否已被交換
    exchanged_with = db.Column(db.String(100))  # 與誰交換

    # 時間戳記
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self, include_happiness=True):
        """轉換為字典格式"""
        data = {
            'id': self.id,
            'player_name': self.player_name,
            'gift_name': self.gift_name,
            'appearance': self.appearance,
            'who_likes': self.who_likes,
            'usage_time': self.usage_time,
            'ai_guess': self.ai_guess,
            'image_url': self.image_url,
            'is_confirmed': self.is_confirmed,
            'is_exchanged': self.is_exchanged,
            'exchanged_with': self.exchanged_with,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'image_generation_status': self.image_generation_status,
            'image_generation_started_at': self.image_generation_started_at.isoformat() if self.image_generation_started_at else None,
            'image_generation_completed_at': self.image_generation_completed_at.isoformat() if self.image_generation_completed_at else None,
            'image_generation_error': self.image_generation_error,
            'image_generation_retry_count': self.image_generation_retry_count,
        }

        # 預設包含幸福理由
        if include_happiness:
            data['happiness_reason'] = self.happiness_reason

        return data


class Vote(db.Model):
    """投票資料模型"""
    __tablename__ = 'votes'

    id = db.Column(db.Integer, primary_key=True)
    gift_id = db.Column(db.Integer, db.ForeignKey('gifts.id'), nullable=False)
    # 'creative' 或 'blessing'
    award_type = db.Column(db.String(50), nullable=False)
    voter_fingerprint = db.Column(db.String(255), nullable=False)  # 投票者指紋
    voter_ip = db.Column(db.String(50))  # IP 地址
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 建立索引以提高查詢效率
    __table_args__ = (
        db.Index('idx_voter_fingerprint', 'voter_fingerprint'),
        db.Index('idx_gift_award', 'gift_id', 'award_type'),
    )

    def to_dict(self):
        """轉換為字典格式"""
        return {
            'id': self.id,
            'gift_id': self.gift_id,
            'award_type': self.award_type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
