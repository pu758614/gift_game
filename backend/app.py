from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from config import Config
from models import db, Gift
from gemini_service import gemini_service
import os

app = Flask(__name__)
app.config.from_object(Config)

# 初始化擴展
CORS(app, origins=Config.CORS_ORIGINS)
db.init_app(app)

# 確保上傳目錄存在
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

# 創建資料表
with app.app_context():
    db.create_all()


@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    """提供上傳的圖片檔案"""
    return send_from_directory(Config.UPLOAD_FOLDER, filename)


@app.route('/api/health', methods=['GET'])
def health_check():
    """健康檢查端點"""
    return jsonify({'status': 'healthy', 'message': 'Gift Exchange API is running'}), 200


@app.route('/api/submit-form', methods=['POST'])
def submit_form():
    """接收並儲存表單資料"""
    try:
        print(f"收到提交請求，Headers: {dict(request.headers)}")
        data = request.get_json()
        print(f"接收到的數據: {data}")

        # 驗證必填欄位
        required_fields = ['player_name', 'appearance', 'who_likes',
                           'usage_time', 'happiness_reason']
        for field in required_fields:
            if not data.get(field):
                error_msg = f'缺少必填欄位: {field}'
                print(f"驗證失敗: {error_msg}")
                return jsonify({'error': error_msg}), 400

        # 創建新的禮物記錄
        gift = Gift(
            player_name=data['player_name'],
            appearance=data['appearance'],
            who_likes=data['who_likes'],
            usage_time=data['usage_time'],
            happiness_reason=data['happiness_reason']
        )

        db.session.add(gift)
        db.session.commit()

        print(f"禮物創建成功，ID: {gift.id}")

        return jsonify({
            'message': '表單提交成功',
            'gift_id': gift.id
        }), 201

    except Exception as e:
        db.session.rollback()
        error_msg = str(e)
        print(f"提交表單錯誤: {error_msg}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': error_msg}), 500


@app.route('/api/generate-gift/<int:gift_id>', methods=['POST'])
def generate_gift(gift_id):
    """使用 AI 猜測禮物並生成圖片"""

    try:
        gift = Gift.query.get_or_404(gift_id)

        # 使用 Gemini 猜測禮物
        ai_guess = gemini_service.guess_gift(
            gift.appearance,
            gift.who_likes,
            gift.usage_time
        )

        # 生成圖片提示詞
        image_prompt = gemini_service.generate_gift_image_prompt(
            ai_guess,
            gift.appearance,
            gift.who_likes
        )

        # 使用 Gemini Imagen API 生成圖片
        image_filename = gemini_service.generate_gift_image(image_prompt)
        if not image_filename:
            raise Exception("圖片生成失敗")
        # 使用相對路徑，讓前端可以根據當前host訪問
        image_url = f"/uploads/{image_filename}" if image_filename else None

        # 更新禮物記錄
        gift.ai_guess = ai_guess
        gift.image_url = image_url
        db.session.commit()

        return jsonify({
            'message': 'AI 生成成功',
            'gift': gift.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/regenerate/<int:gift_id>', methods=['POST'])
def regenerate_gift(gift_id):
    """重新生成禮物圖片"""
    try:
        gift = Gift.query.get_or_404(gift_id)

        # 重新猜測禮物
        ai_guess = gemini_service.guess_gift(
            gift.appearance,
            gift.who_likes,
            gift.usage_time
        )

        # 重新生成圖片
        image_prompt = gemini_service.generate_gift_image_prompt(
            ai_guess,
            gift.appearance,
            gift.who_likes
        )
        image_filename = gemini_service.generate_gift_image(image_prompt)
        # 使用相對路徑，讓前端可以根據當前host訪問
        image_url = f"/uploads/{image_filename}" if image_filename else None

        # 更新記錄
        gift.ai_guess = ai_guess
        gift.image_url = image_url
        db.session.commit()

        return jsonify({
            'message': '重新生成成功',
            'gift': gift.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/confirm/<int:gift_id>', methods=['POST'])
def confirm_gift(gift_id):
    """確認禮物圖片"""
    try:
        gift = Gift.query.get_or_404(gift_id)
        gift.is_confirmed = True
        db.session.commit()

        return jsonify({
            'message': '禮物確認成功',
            'gift': gift.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/gifts', methods=['GET'])
def get_gifts():
    """取得所有已確認的禮物"""
    try:
        # 只返回已確認的禮物
        gifts = Gift.query.filter_by(is_confirmed=True).all()

        return jsonify({
            'gifts': [gift.to_dict() for gift in gifts],
            'total': len(gifts)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/gift/<int:gift_id>', methods=['GET'])
def get_gift_detail(gift_id):
    """取得單一禮物詳情（包含幸福理由）"""
    try:
        gift = Gift.query.get_or_404(gift_id)

        # 包含幸福理由
        return jsonify({
            'gift': gift.to_dict(include_happiness=True)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/exchange', methods=['POST'])
def exchange_gift():
    """執行禮物交換"""
    try:
        data = request.get_json()
        gift_id = data.get('gift_id')
        exchanger_name = data.get('exchanger_name')

        if not gift_id or not exchanger_name:
            return jsonify({'error': '缺少必要參數'}), 400

        gift = Gift.query.get_or_404(gift_id)

        # 檢查禮物是否已被交換
        if gift.is_exchanged:
            return jsonify({'error': '此禮物已被交換'}), 400

        # 標記為已交換
        gift.is_exchanged = True
        gift.exchanged_with = exchanger_name
        db.session.commit()

        return jsonify({
            'message': f'交換成功！請與 {gift.player_name} 交換禮物',
            'gift_owner': gift.player_name,
            'gift': gift.to_dict(include_happiness=True)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/reset', methods=['POST'])
def reset_game():
    """重置遊戲（開發用）"""
    try:
        # 刪除所有禮物
        Gift.query.delete()
        db.session.commit()

        return jsonify({'message': '遊戲已重置'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
