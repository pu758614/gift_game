"""更新資料庫中的圖片 URL,將完整 URL 轉換為相對路徑"""
from app import app
from models import db, Gift
import re


def update_image_urls():
    """將所有圖片 URL 轉換為相對路徑格式 (/gift-images/filename.png)"""
    with app.app_context():
        # 獲取所有有圖片的禮物
        gifts = Gift.query.filter(Gift.image_url.isnot(None)).all()

        updated_count = 0
        for gift in gifts:
            # 檢查是否是完整 URL (包含 http:// 或 https://)
            if gift.image_url.startswith('http://') or gift.image_url.startswith('https://'):
                # 使用正則表達式提取 /bucket/filename 部分
                # 例如: http://localhost:9000/gift-images/gift_image_123.png
                # 提取: /gift-images/gift_image_123.png
                match = re.search(r'/(gift-images/.+)$', gift.image_url)
                if match:
                    relative_path = '/' + match.group(1)

                    print(f"更新禮物 {gift.id}:")
                    print(f"  舊 URL: {gift.image_url}")
                    print(f"  新路徑: {relative_path}")

                    gift.image_url = relative_path
                    updated_count += 1
                else:
                    print(f"警告: 無法解析禮物 {gift.id} 的 URL: {gift.image_url}")

        # 提交變更
        if updated_count > 0:
            db.session.commit()
            print(f"\n✓ 成功更新 {updated_count} 個圖片 URL 為相對路徑")
        else:
            print("\n沒有需要更新的 URL")


if __name__ == '__main__':
    print("開始將圖片 URL 轉換為相對路徑格式...")
    update_image_urls()
