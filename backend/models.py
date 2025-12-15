from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Gift(db.Model):
    """禮物資料模型"""
    __tablename__ = 'gifts'

    id = db.Column(db.Integer, primary_key=True)
    player_name = db.Column(db.String(100), nullable=False)

    # 表單問題答案
    appearance = db.Column(db.Text, nullable=False)  # 外型或材質
    who_likes = db.Column(db.Text, nullable=False)  # 什麼人會喜歡
    usage_time = db.Column(db.Text, nullable=False)  # 什麼時候使用
    happiness_reason = db.Column(db.Text, nullable=False)  # 幸福感

    # AI 生成結果
    ai_guess = db.Column(db.String(200))  # AI 猜測的禮物
    image_url = db.Column(db.String(500))  # 生成的圖片 URL

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
            'appearance': self.appearance,
            'who_likes': self.who_likes,
            'usage_time': self.usage_time,
            'ai_guess': self.ai_guess,
            'image_url': self.image_url,
            'is_confirmed': self.is_confirmed,
            'is_exchanged': self.is_exchanged,
            'exchanged_with': self.exchanged_with,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

        # 預設包含幸福理由
        if include_happiness:
            data['happiness_reason'] = self.happiness_reason

        return data
