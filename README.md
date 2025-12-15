# 交換禮物遊戲 (Gift Exchange Game)

一個基於 React + Flask + PostgreSQL + Docker 的交換禮物遊戲系統。

## 功能特色

- 玩家填寫禮物資訊表單
- 使用 Gemini AI 猜測禮物並生成圖片
- 查看所有玩家的禮物總覽
- 選擇想要的禮物進行交換
- 顯示禮物主人並完成配對

## 技術架構

- **前端**: React + Vite
- **後端**: Flask + SQLAlchemy
- **資料庫**: PostgreSQL
- **容器化**: Docker + Docker Compose
- **AI**: Google Gemini API

## 快速開始

### 前置需求

- Docker & Docker Compose
- Node.js 18+ (本地開發)
- Python 3.11+ (本地開發)

### 安裝步驟

1. 複製專案
```bash
git clone <your-repo-url>
cd giift_game
```

2. 設定環境變數
```bash
cp .env.example .env
# 編輯 .env 檔案，填入你的 GEMINI_API_KEY
```

3. 啟動服務
```bash
docker-compose up --build
```

4. 訪問應用
- 前端: http://localhost:3000
- 後端 API: http://localhost:5000

## 遊戲規則

1. **填寫表單**: 輸入姓名及禮物相關問題
2. **AI 生成**: 系統使用 AI 猜測禮物並生成圖片
3. **確認圖片**: 可以確認或重新生成圖片
4. **查看總覽**: 瀏覽所有已提交的禮物
5. **開始交換**: 選擇想要的禮物
6. **查看祝福**: 閱讀禮物的幸福理由
7. **完成配對**: 與禮物主人交換

## 開發指令

### 後端 (Flask)
```bash
cd backend
pip install -r requirements.txt
python app.py
```

### 前端 (React)
```bash
cd frontend
npm install
npm run dev
```

## 專案結構

```
giift_game/
├── backend/
│   ├── app.py
│   ├── models.py
│   ├── config.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## API 文檔

### POST /api/submit-form
提交禮物表單資料

### POST /api/generate-gift
呼叫 AI 生成禮物圖片

### POST /api/regenerate/{gift_id}
重新生成禮物圖片

### GET /api/gifts
取得所有禮物列表

### POST /api/exchange
執行禮物交換

## License

MIT
