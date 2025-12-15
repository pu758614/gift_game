# 環境變數配置說明

## 必要配置

### 1. 複製環境變數檔案
```bash
cp .env.example .env
```

### 2. 編輯 .env 檔案

#### 資料庫設定
```
POSTGRES_USER=giftgame
POSTGRES_PASSWORD=your_secure_password_here  # 請修改為安全的密碼
POSTGRES_DB=giftgame_db
DATABASE_URL=postgresql://giftgame:your_secure_password_here@db:5432/giftgame_db
```

#### Flask 設定
```
FLASK_SECRET_KEY=your_secret_key_here_change_in_production  # 請修改為隨機字串
```

#### Google Gemini API
```
GEMINI_API_KEY=your_gemini_api_key_here  # 請填入你的 Gemini API Key
```

## 取得 Gemini API Key

1. 前往 [Google AI Studio](https://makersuite.google.com/app/apikey)
2. 登入你的 Google 帳號
3. 點擊「Get API Key」
4. 複製生成的 API Key
5. 貼到 `.env` 檔案的 `GEMINI_API_KEY` 欄位

## 圖片生成說明

目前系統使用佔位圖服務作為示範。如需使用真實的 AI 圖片生成功能，可以整合以下服務：

### 選項 1: Google Imagen (推薦)
- 使用 Google Cloud Vertex AI 的 Imagen API
- 與 Gemini API 同屬 Google Cloud 平台

### 選項 2: OpenAI DALL-E
- 需要 OpenAI API Key
- 在 `gemini_service.py` 中新增 DALL-E 呼叫邏輯

### 選項 3: Stable Diffusion
- 可使用 Stability AI API 或自架服務
- 在 `gemini_service.py` 中新增 Stable Diffusion 呼叫邏輯

## 安全性建議

### 生產環境部署前：

1. **更改所有預設密碼**
   - 資料庫密碼
   - Flask Secret Key

2. **設定防火牆規則**
   - 限制資料庫端口 (5432) 只能從內部網路存取

3. **使用 HTTPS**
   - 設定 SSL 憑證
   - 使用 Nginx 或 Traefik 作為反向代理

4. **環境變數保護**
   - 不要將 `.env` 檔案提交到版本控制
   - 使用 Docker secrets 或 Kubernetes secrets 管理敏感資訊

5. **API 速率限制**
   - 實作 API rate limiting
   - 防止 DDoS 攻擊

## 開發與生產環境

### 開發環境
```
FLASK_ENV=development
```

### 生產環境
```
FLASK_ENV=production
```

記得在生產環境關閉 Flask 的 debug 模式！
