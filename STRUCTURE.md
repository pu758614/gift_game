# 交換禮物遊戲 - 專案結構

```
giift_game/
│
├── backend/                          # Flask 後端
│   ├── app.py                        # 主應用程式，包含所有 API 路由
│   ├── models.py                     # SQLAlchemy 資料庫模型（Gift）
│   ├── config.py                     # 配置設定
│   ├── gemini_service.py             # Gemini AI 整合服務
│   ├── requirements.txt              # Python 依賴套件
│   ├── Dockerfile                    # 後端 Docker 配置
│   └── uploads/                      # 上傳檔案目錄（自動建立）
│
├── frontend/                         # React 前端
│   ├── src/
│   │   ├── pages/
│   │   │   ├── FormPage.jsx          # 表單填寫頁面
│   │   │   ├── ConfirmPage.jsx       # 圖片確認頁面
│   │   │   ├── GalleryPage.jsx       # 禮物總覽頁面
│   │   │   └── ExchangePage.jsx      # 交換禮物頁面
│   │   ├── App.jsx                   # 主應用程式組件
│   │   ├── main.jsx                  # 應用程式入口
│   │   ├── api.js                    # API 呼叫封裝
│   │   └── index.css                 # 全域樣式
│   ├── index.html                    # HTML 模板
│   ├── package.json                  # Node.js 依賴
│   ├── vite.config.js                # Vite 配置
│   └── Dockerfile                    # 前端 Docker 配置
│
├── docker-compose.yml                # Docker Compose 配置
├── .env.example                      # 環境變數範例
├── .gitignore                        # Git 忽略檔案
├── README.md                         # 專案說明
├── SETUP.md                          # 設定指南
├── USAGE.md                          # 使用說明
├── start.ps1                         # Windows 啟動腳本
├── stop.ps1                          # Windows 停止腳本
└── test-api.ps1                      # API 測試腳本

```

## 檔案說明

### 後端檔案

#### `app.py`
Flask 主應用程式，包含所有 API 路由：
- `/api/health` - 健康檢查
- `/api/submit-form` - 提交表單
- `/api/generate-gift/<id>` - 生成禮物
- `/api/regenerate/<id>` - 重新生成
- `/api/confirm/<id>` - 確認禮物
- `/api/gifts` - 取得所有禮物
- `/api/gift/<id>` - 取得單一禮物詳情
- `/api/exchange` - 交換禮物
- `/api/reset` - 重置遊戲

#### `models.py`
資料庫模型定義：
- `Gift` 模型包含所有禮物相關欄位
- 表單問答欄位
- AI 生成結果欄位
- 交換狀態欄位

#### `gemini_service.py`
Gemini AI 整合：
- `guess_gift()` - 根據描述猜測禮物
- `generate_gift_image_prompt()` - 生成圖片提示詞
- `generate_placeholder_image_url()` - 生成佔位圖（待替換為真實 AI 圖片生成）

#### `config.py`
應用程式配置：
- 資料庫連接設定
- Gemini API Key
- Flask 密鑰
- CORS 設定

### 前端檔案

#### `pages/FormPage.jsx`
表單填寫頁面：
- 6 個問題的表單
- 表單驗證
- 提交後自動生成並導航到確認頁

#### `pages/ConfirmPage.jsx`
圖片確認頁面：
- 顯示 AI 猜測的禮物
- 顯示生成的圖片
- 重新生成功能
- 確認並上傳

#### `pages/GalleryPage.jsx`
禮物總覽頁面：
- 顯示所有已確認的禮物
- 網格佈局展示
- 顯示禮物狀態（已交換/未交換）
- 新增禮物按鈕
- 開始交換按鈕

#### `pages/ExchangePage.jsx`
交換禮物頁面：
- 顯示可選擇的禮物
- 點擊顯示詳情 Modal
- 顯示幸福理由
- 輸入交換者名字
- 確認交換並顯示結果

#### `api.js`
API 呼叫封裝：
- 統一管理所有 API 請求
- 使用 axios 處理 HTTP 請求
- 配置 base URL

#### `index.css`
全域樣式：
- 漸層背景
- 卡片樣式
- 表單樣式
- 按鈕樣式
- 禮物網格佈局
- Modal 樣式
- 響應式設計

### Docker 配置

#### `docker-compose.yml`
定義三個服務：
1. **db** - PostgreSQL 資料庫
2. **backend** - Flask 後端
3. **frontend** - React 前端

#### `backend/Dockerfile`
- Python 3.11-slim 基礎映像
- 安裝系統依賴
- 安裝 Python 套件
- 複製應用程式碼

#### `frontend/Dockerfile`
- Node.js 18-alpine 基礎映像
- 安裝 npm 依賴
- 啟動 Vite 開發伺服器

### 配置檔案

#### `.env.example`
環境變數範本：
- 資料庫設定
- Flask 設定
- Gemini API Key
- 前端 API URL

#### `.gitignore`
Git 忽略規則：
- Python 快取檔案
- Node modules
- 環境變數檔案
- 建置輸出

### 輔助腳本

#### `start.ps1`
Windows 啟動腳本：
- 檢查 .env 檔案
- 檢查 Docker 服務
- 啟動 Docker Compose

#### `stop.ps1`
停止腳本：
- 停止服務
- 選擇是否清除資料

#### `test-api.ps1`
API 測試腳本：
- 測試所有 API 端點
- 模擬完整流程

## 資料流程

1. **表單提交流程**
   ```
   FormPage → POST /api/submit-form → 建立 Gift 記錄
   → POST /api/generate-gift → 呼叫 Gemini API
   → 返回 AI 猜測和圖片 → ConfirmPage
   ```

2. **確認流程**
   ```
   ConfirmPage → 顯示圖片 → 使用者確認
   → POST /api/confirm → 標記為已確認 → GalleryPage
   ```

3. **交換流程**
   ```
   GalleryPage → 點擊開始交換 → ExchangePage
   → 選擇禮物 → 顯示幸福理由 → 輸入名字
   → POST /api/exchange → 標記已交換 → 顯示結果
   ```

## 資料庫結構

### gifts 資料表
```sql
CREATE TABLE gifts (
    id SERIAL PRIMARY KEY,
    player_name VARCHAR(100) NOT NULL,
    who_likes TEXT NOT NULL,
    usage_situation TEXT NOT NULL,
    usage_time TEXT NOT NULL,
    usage_time_2 TEXT NOT NULL,
    happiness_reason TEXT NOT NULL,
    ai_guess VARCHAR(200),
    image_url VARCHAR(500),
    is_confirmed BOOLEAN DEFAULT FALSE,
    is_exchanged BOOLEAN DEFAULT FALSE,
    exchanged_with VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 技術特點

### 後端
- **Flask** - 輕量級 Web 框架
- **SQLAlchemy** - ORM，簡化資料庫操作
- **Flask-CORS** - 處理跨域請求
- **Google Generative AI** - Gemini API 整合
- **PostgreSQL** - 關聯式資料庫

### 前端
- **React 18** - 現代化 UI 框架
- **React Router** - 單頁應用路由
- **Axios** - HTTP 請求庫
- **Vite** - 快速開發建置工具
- **原生 CSS** - 響應式設計

### DevOps
- **Docker** - 容器化應用
- **Docker Compose** - 多容器編排
- **PostgreSQL** - 容器化資料庫

## 擴展建議

### 短期改進
1. 整合真實的圖片生成 API（Imagen、DALL-E、Stable Diffusion）
2. 新增使用者認證系統
3. 新增禮物編輯功能
4. 新增遊戲房間功能（多組玩家）

### 長期規劃
1. 新增行動版 App（React Native）
2. 新增即時通知（WebSocket）
3. 新增禮物評分功能
4. 新增遊戲歷史記錄
5. 新增社交分享功能
6. 多語言支援
7. 效能優化（Redis 快取）
