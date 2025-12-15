# 🎉 專案啟動成功！

## ✅ 當前狀態

所有服務已成功啟動並運行中：

- ✅ **資料庫 (PostgreSQL)**: 運行在 http://localhost:5432
- ✅ **後端 (Flask)**: 運行在 http://localhost:5000
- ✅ **前端 (React)**: 運行在 http://localhost:3000

## 🚀 立即使用

### 訪問應用程式

**前端介面**: http://localhost:3000

打開瀏覽器訪問上述網址即可開始使用！

### 後端 API

**API 端點**: http://localhost:5000

健康檢查: http://localhost:5000/api/health

## 📝 重要提示

### 1. Gemini API Key 設定

目前 AI 功能**需要 Gemini API Key**才能使用：

```powershell
# 編輯 .env 檔案
notepad .env

# 找到這一行並填入你的 API Key：
GEMINI_API_KEY=你的_API_Key_請填這裡
```

**取得 API Key**:
1. 前往: https://makersuite.google.com/app/apikey
2. 登入 Google 帳號
3. 點擊「Get API Key」
4. 複製 API Key
5. 貼到 `.env` 檔案中

### 2. 重新啟動服務（如果修改了 .env）

```powershell
# 停止服務
docker-compose down

# 重新啟動
docker-compose up -d
```

### 3. 圖片生成說明

目前使用**佔位圖服務**作為示範。如需使用真實的 AI 圖片生成：

- 選項 1: Google Imagen API
- 選項 2: OpenAI DALL-E
- 選項 3: Stable Diffusion

請參考 `backend/gemini_service.py` 中的 `generate_placeholder_image_url()` 函數進行整合。

## 🎮 使用流程

1. **新增禮物**
   - 訪問 http://localhost:3000
   - 填寫表單（6 個問題）
   - AI 會猜測並生成禮物圖片

2. **確認圖片**
   - 查看 AI 生成的結果
   - 可選擇重新生成或確認

3. **查看總覽**
   - 點擊「查看總覽」
   - 瀏覽所有玩家的禮物

4. **開始交換**
   - 點擊「開始交換禮物」
   - 選擇想要的禮物
   - 查看幸福理由
   - 確認交換

## 🛠️ 常用指令

### 查看日誌

```powershell
# 查看所有日誌
docker-compose logs

# 查看後端日誌
docker logs giftgame_backend

# 查看前端日誌
docker logs giftgame_frontend

# 查看資料庫日誌
docker logs giftgame_db

# 持續追蹤日誌
docker-compose logs -f
```

### 停止服務

```powershell
# 方式 1: 使用腳本
.\stop.ps1

# 方式 2: 手動停止（保留資料）
docker-compose down

# 方式 3: 停止並清除資料
docker-compose down -v
```

### 重新啟動

```powershell
# 重新啟動所有服務
docker-compose restart

# 重新啟動單一服務
docker-compose restart backend
docker-compose restart frontend
```

### 重新建置

```powershell
# 重新建置並啟動
docker-compose up -d --build
```

## 🧪 測試 API

執行測試腳本：

```powershell
.\test-api.ps1
```

這會自動測試所有 API 端點並顯示結果。

## 🐛 疑難排解

### 前端無法連接後端

1. 確認後端運行正常：
   ```powershell
   docker logs giftgame_backend
   ```

2. 檢查網路連接：
   ```powershell
   curl http://localhost:5000/api/health
   ```

### 資料庫連接失敗

1. 確認資料庫健康狀態：
   ```powershell
   docker ps
   ```
   查看 `giftgame_db` 的 STATUS 欄位應該顯示 "healthy"

2. 查看資料庫日誌：
   ```powershell
   docker logs giftgame_db
   ```

### Port 已被佔用

如果遇到 port 衝突：

```powershell
# 查看佔用 port 的程序
netstat -ano | findstr :5000
netstat -ano | findstr :3000

# 停止衝突的容器
docker ps -a
docker stop <container_id>
```

### 清除所有資料重新開始

```powershell
# 停止並刪除所有容器、網路、volumes
docker-compose down -v

# 刪除映像檔（可選）
docker rmi giift_game-backend giift_game-frontend

# 重新建置並啟動
docker-compose up -d --build
```

## 📂 專案檔案

重要檔案位置：

- 後端程式碼: `backend/app.py`
- 前端程式碼: `frontend/src/`
- 環境設定: `.env`
- Docker 設定: `docker-compose.yml`

## 📚 更多文件

- **QUICKSTART.md** - 快速啟動指南
- **README.md** - 專案概述
- **SETUP.md** - 詳細設定說明
- **USAGE.md** - 完整使用手冊
- **STRUCTURE.md** - 專案結構文件

## 💡 下一步

1. ✅ 服務已啟動
2. 📝 設定 Gemini API Key（選配）
3. 🌐 訪問 http://localhost:3000
4. 🎮 開始使用交換禮物遊戲！

---

**享受交換禮物的樂趣！🎁**
