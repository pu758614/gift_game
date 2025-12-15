# 🎁 交換禮物遊戲 - 快速啟動指南

## ✅ 已完成的內容

### 後端 (Flask + PostgreSQL)
- ✅ Flask API 伺服器
- ✅ PostgreSQL 資料庫模型
- ✅ Gemini AI 整合
- ✅ 所有 API 端點
- ✅ Docker 配置

### 前端 (React)
- ✅ 表單填寫頁面
- ✅ 圖片確認頁面
- ✅ 禮物總覽頁面
- ✅ 交換禮物頁面
- ✅ 完整樣式設計
- ✅ Docker 配置

### DevOps
- ✅ Docker Compose 設定
- ✅ 環境變數配置
- ✅ 啟動/停止腳本

## 🚀 立即開始

### 步驟 1: 設定環境變數

```powershell
# 複製環境變數範例檔案
Copy-Item .env.example .env
```

然後編輯 `.env` 檔案，填入你的 Gemini API Key：
```
GEMINI_API_KEY=你的_API_Key
```

> **如何取得 Gemini API Key？**
> 1. 前往：https://makersuite.google.com/app/apikey
> 2. 登入 Google 帳號
> 3. 點擊「Get API Key」
> 4. 複製並貼到 .env 檔案

### 步驟 2: 啟動服務

使用便捷腳本：
```powershell
.\start.ps1
```

或手動啟動：
```powershell
docker-compose up --build
```

### 步驟 3: 訪問應用程式

等待服務啟動完成（約 1-2 分鐘），然後訪問：

- 🌐 **前端介面**: http://localhost:3000
- 🔌 **後端 API**: http://localhost:5000
- 💾 **資料庫**: localhost:5432

## 🎮 遊戲流程

1. **填寫表單** (/)
   - 輸入名字和禮物相關問題
   - 提交後自動生成 AI 禮物

2. **確認圖片** (/confirm/:id)
   - 查看 AI 猜測的禮物
   - 可重新生成或確認

3. **查看總覽** (/gallery)
   - 瀏覽所有玩家的禮物
   - 點擊「開始交換」

4. **交換禮物** (/exchange)
   - 選擇想要的禮物
   - 查看幸福理由
   - 確認交換並顯示禮物主人

## 🧪 測試 API

執行測試腳本：
```powershell
.\test-api.ps1
```

這會自動測試所有 API 端點。

## 🛑 停止服務

使用便捷腳本：
```powershell
.\stop.ps1
```

或手動停止：
```powershell
# 僅停止服務（保留資料）
docker-compose down

# 停止並清除資料
docker-compose down -v
```

## 📁 專案結構

```
giift_game/
├── backend/              # Flask 後端
│   ├── app.py           # 主程式 + API 路由
│   ├── models.py        # 資料庫模型
│   ├── gemini_service.py # AI 整合
│   └── ...
├── frontend/            # React 前端
│   └── src/
│       ├── pages/       # 四個主要頁面
│       ├── api.js       # API 呼叫
│       └── ...
├── docker-compose.yml   # Docker 配置
├── .env.example         # 環境變數範例
└── start.ps1           # 啟動腳本
```

## 🔧 開發模式

### 本地開發後端
```powershell
cd backend
pip install -r requirements.txt
python app.py
```

### 本地開發前端
```powershell
cd frontend
npm install
npm run dev
```

## ⚠️ 注意事項

### 1. Gemini API Key
- **必須設定**才能使用 AI 猜測禮物功能
- 留空的話會顯示預設訊息

### 2. 圖片生成
- 目前使用**佔位圖服務**
- 如需真實 AI 圖片生成，請參考 `SETUP.md` 整合：
  - Google Imagen
  - OpenAI DALL-E
  - Stable Diffusion

### 3. 資料庫
- 資料儲存在 Docker Volume 中
- 重啟容器不會遺失資料
- 執行 `docker-compose down -v` 會清除所有資料

### 4. 生產環境
- 修改 `.env` 中的密碼和密鑰
- 使用 HTTPS
- 設定防火牆規則
- 參考 `SETUP.md` 的安全性建議

## 📚 更多文件

- **README.md** - 專案概述
- **SETUP.md** - 詳細設定指南
- **USAGE.md** - 詳細使用說明
- **STRUCTURE.md** - 專案結構說明

## 🐛 常見問題

### Q: 無法啟動 Docker？
```powershell
# 確認 Docker Desktop 是否運行
docker ps
```

### Q: 前端無法連接後端？
檢查 `vite.config.js` 的 proxy 設定和後端是否啟動成功。

### Q: 資料庫連接錯誤？
等待 30 秒讓資料庫完全啟動，或查看 `docker-compose logs db`。

### Q: Gemini API 錯誤？
確認 `.env` 中的 `GEMINI_API_KEY` 是否正確設定。

## 🎯 下一步

1. ✅ 啟動服務
2. ✅ 填寫表單測試
3. ✅ 體驗完整流程
4. 📝 設定你的 Gemini API Key
5. 🖼️ 整合真實圖片生成 API（選配）

## 💡 技術支援

遇到問題？檢查：
1. Docker 日誌：`docker-compose logs`
2. 後端日誌：`docker-compose logs backend`
3. 前端日誌：`docker-compose logs frontend`
4. 資料庫日誌：`docker-compose logs db`

---

**祝你使用愉快！🎉**
