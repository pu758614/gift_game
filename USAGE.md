# 使用說明

## 啟動專案

### 方式一：使用 Docker Compose（推薦）

1. **設定環境變數**
```bash
cp .env.example .env
# 編輯 .env 檔案，填入你的 GEMINI_API_KEY
```

2. **啟動所有服務**
```bash
docker-compose up --build
```

3. **訪問應用程式**
- 前端介面：http://localhost:3000
- 後端 API：http://localhost:5000
- 資料庫：localhost:5432

### 方式二：本地開發

#### 後端設定

1. **安裝 Python 依賴**
```bash
cd backend
pip install -r requirements.txt
```

2. **設定環境變數**
```bash
# 在 backend 目錄下建立 .env 檔案
DATABASE_URL=postgresql://giftgame:giftgame123@localhost:5432/giftgame_db
GEMINI_API_KEY=your_api_key_here
FLASK_SECRET_KEY=dev_secret_key
```

3. **啟動後端**
```bash
python app.py
```

#### 前端設定

1. **安裝 Node.js 依賴**
```bash
cd frontend
npm install
```

2. **啟動前端**
```bash
npm run dev
```

#### 資料庫設定

1. **安裝 PostgreSQL**
2. **建立資料庫**
```bash
createdb giftgame_db
```

## 遊戲流程

### 1. 填寫禮物表單
- 訪問 http://localhost:3000
- 填寫你的名字和禮物相關問題
- 點擊「提交並生成禮物圖片」

### 2. 確認 AI 生成的禮物
- 系統會使用 AI 猜測你的禮物
- 顯示生成的禮物圖片
- 可以選擇「重新生成」或「確認並上傳」

### 3. 查看禮物總覽
- 點擊「禮物總覽」查看所有已提交的禮物
- 顯示每個禮物的圖片和主人名字

### 4. 開始交換禮物
- 點擊「開始交換禮物」
- 瀏覽所有可選擇的禮物
- 點擊想要的禮物查看詳情

### 5. 查看幸福理由
- 選擇禮物後會顯示「為什麼會感到幸福」的答案
- 閱讀禮物的詳細資訊

### 6. 確認交換
- 輸入你的名字
- 點擊「確認交換」
- 系統顯示禮物主人的名字
- 與該玩家完成實體禮物交換

## API 端點說明

### 健康檢查
```
GET /api/health
```

### 提交表單
```
POST /api/submit-form
Body: {
  "player_name": "玩家名字",
  "who_likes": "誰會喜歡",
  "usage_situation": "使用情況",
  "usage_time": "使用時機1",
  "usage_time_2": "使用時機2",
  "happiness_reason": "幸福理由"
}
```

### 生成禮物
```
POST /api/generate-gift/{gift_id}
```

### 重新生成
```
POST /api/regenerate/{gift_id}
```

### 確認禮物
```
POST /api/confirm/{gift_id}
```

### 取得所有禮物
```
GET /api/gifts
```

### 取得禮物詳情
```
GET /api/gift/{gift_id}
```

### 交換禮物
```
POST /api/exchange
Body: {
  "gift_id": 1,
  "exchanger_name": "交換者名字"
}
```

### 重置遊戲
```
POST /api/reset
```

## 常見問題

### Q: 無法連接到後端 API？
A: 確認後端服務是否正常運行在 port 5000，檢查 CORS 設定。

### Q: Gemini API 返回錯誤？
A: 檢查 `.env` 中的 `GEMINI_API_KEY` 是否正確設定。

### Q: 資料庫連接失敗？
A: 確認 PostgreSQL 服務正常運行，檢查 `DATABASE_URL` 設定。

### Q: 圖片顯示不出來？
A: 目前使用佔位圖服務，需要網路連線。如要使用真實 AI 圖片生成，請參考 SETUP.md。

### Q: 如何重置遊戲？
A: 發送 POST 請求到 `/api/reset` 端點，或重新啟動 Docker 容器。

## 停止服務

### Docker Compose
```bash
docker-compose down
```

### 本地開發
- 按 `Ctrl+C` 停止前端和後端服務

## 清除資料

### 清除 Docker 資料
```bash
docker-compose down -v  # 刪除 volumes，包含資料庫資料
```

### 清除資料庫
```sql
DROP DATABASE giftgame_db;
CREATE DATABASE giftgame_db;
```
