from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_migrate import Migrate
from config import Config
from models import db, Gift, Vote
from gemini_service import gemini_service
import os

app = Flask(__name__)
app.config.from_object(Config)

# 初始化擴展
CORS(app, origins=Config.CORS_ORIGINS)
db.init_app(app)
migrate = Migrate(app, db)

# 創建資料表 (僅在沒有使用遷移時)
# with app.app_context():
#     db.create_all()


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
        required_fields = ['player_name', 'gift_name', 'appearance', 'who_likes',
                           'usage_time', 'happiness_reason']
        for field in required_fields:
            if not data.get(field):
                error_msg = f'缺少必填欄位: {field}'
                print(f"驗證失敗: {error_msg}")
                return jsonify({'error': error_msg}), 400

        # 創建新的禮物記錄
        gift = Gift(
            player_name=data['player_name'],
            gift_name=data['gift_name'],
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

        # 使用 AI 生成圖片並上傳到 MinIO
        image_url = gemini_service.generate_gift_image(image_prompt)
        if not image_url:
            raise Exception("圖片生成失敗")

        # 更新禮物記錄 (image_url 已是完整的 MinIO URL)
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
        image_url = gemini_service.generate_gift_image(image_prompt)
        if not image_url:
            raise Exception("圖片生成失敗")

        # 更新記錄 (image_url 已是完整的 MinIO URL)
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
        # 刪除所有禮物和投票
        Vote.query.delete()
        Gift.query.delete()
        db.session.commit()

        return jsonify({'message': '遊戲已重置'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/voting/submit', methods=['POST'])
def submit_vote():
    """提交投票"""
    try:
        data = request.get_json()
        gift_id = data.get('gift_id')
        award_type = data.get('award_type')  # 'creative' 或 'blessing'
        voter_fingerprint = data.get('voter_fingerprint')

        # 驗證參數
        if not all([gift_id, award_type, voter_fingerprint]):
            return jsonify({'error': '缺少必要參數'}), 400

        if award_type not in ['creative', 'blessing']:
            return jsonify({'error': '無效的獎項類型'}), 400

        # 檢查禮物是否存在
        gift = Gift.query.get(gift_id)
        if not gift:
            return jsonify({'error': '禮物不存在'}), 404

        # 檢查該投票者對此獎項已投了幾票
        votes_count = Vote.query.filter_by(
            voter_fingerprint=voter_fingerprint,
            award_type=award_type
        ).count()

        if votes_count >= 3:
            return jsonify({'error': f'您已用完此獎項的3票'}), 400

        # 檢查是否已對此禮物投過此獎項
        existing_vote = Vote.query.filter_by(
            voter_fingerprint=voter_fingerprint,
            gift_id=gift_id,
            award_type=award_type
        ).first()

        if existing_vote:
            return jsonify({'error': '您已對此禮物投過此獎項'}), 400

        # 創建投票記錄
        vote = Vote(
            gift_id=gift_id,
            award_type=award_type,
            voter_fingerprint=voter_fingerprint,
            voter_ip=request.remote_addr
        )

        db.session.add(vote)
        db.session.commit()

        # 返回當前投票狀態
        remaining_votes = 3 - (votes_count + 1)
        return jsonify({
            'message': '投票成功',
            'remaining_votes': remaining_votes
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/voting/status', methods=['POST'])
def get_voting_status():
    """獲取當前投票者的投票狀態"""
    try:
        data = request.get_json()
        voter_fingerprint = data.get('voter_fingerprint')

        if not voter_fingerprint:
            return jsonify({'error': '缺少投票者指紋'}), 400

        # 獲取該投票者的所有投票
        votes = Vote.query.filter_by(voter_fingerprint=voter_fingerprint).all()

        # 統計各獎項已投票數和已投票的禮物ID
        creative_votes = [
            v.gift_id for v in votes if v.award_type == 'creative']
        blessing_votes = [
            v.gift_id for v in votes if v.award_type == 'blessing']

        return jsonify({
            'creative': {
                'voted_gift_ids': creative_votes,
                'remaining_votes': 3 - len(creative_votes)
            },
            'blessing': {
                'voted_gift_ids': blessing_votes,
                'remaining_votes': 3 - len(blessing_votes)
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/voting/results', methods=['GET'])
def get_voting_results():
    """獲取投票結果"""
    try:
        # 獲取所有禮物及其票數
        gifts = Gift.query.filter_by(is_confirmed=True).all()

        results = []
        for gift in gifts:
            creative_count = Vote.query.filter_by(
                gift_id=gift.id,
                award_type='creative'
            ).count()

            blessing_count = Vote.query.filter_by(
                gift_id=gift.id,
                award_type='blessing'
            ).count()

            gift_data = gift.to_dict(include_happiness=False)
            gift_data['creative_votes'] = creative_count
            gift_data['blessing_votes'] = blessing_count
            results.append(gift_data)

        return jsonify({
            'gifts': results,
            'total': len(results)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
