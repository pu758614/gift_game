# Gemini API 測試腳本使用說明

## 測試腳本說明

我已經為您建立了兩個測試腳本來驗證 Gemini API 的功能：

### 1. PowerShell 測試腳本 (`test-gemini.ps1`)

**功能**：
- 透過 REST API 測試完整的禮物生成流程
- 測試 3 個不同的禮物案例（咖啡杯、藍牙耳機、香氛蠟燭）
- 測試 AI 猜測和重新生成功能
- 計算 API 回應時間
- 提供詳細的測試報告

**使用方法**：
```powershell
# 在專案根目錄執行
.\test-gemini.ps1
```

**測試流程**：
1. 檢查 Gemini API Key 是否設定
2. 為每個測試案例提交表單
3. 呼叫 Gemini API 猜測禮物
4. 測試重新生成功能
5. 顯示測試結果統計

### 2. Python 直接測試腳本 (`backend/test_gemini_direct.py`)

**功能**：
- 直接測試 Gemini API 連接
- 驗證套件安裝和配置
- 列出可用的 Gemini 模型
- 測試禮物猜測功能（3 個案例）
- 測試圖片提示詞生成
- 計算平均回應時間

**使用方法**：

方式 1 - 在 Docker 容器內執行：
```powershell
# 進入後端容器
docker exec -it giftgame_backend bash

# 執行測試腳本
python test_gemini_direct.py
```

方式 2 - 從外部執行：
```powershell
# 直接執行容器內的腳本
docker exec giftgame_backend python test_gemini_direct.py
```

**測試項目**：
1. ✓ Import Test - 檢查 google.generativeai 套件
2. ✓ API Key Test - 驗證 API Key 是否設定
3. ✓ Configuration Test - 測試 API 配置
4. ✓ List Models Test - 列出可用模型
5. ✓ Gift Guessing Test - 測試禮物猜測（3 個案例）
6. ✓ Image Prompt Test - 測試圖片提示詞生成

## 設定 Gemini API Key

### 步驟 1: 取得 API Key

1. 前往：https://makersuite.google.com/app/apikey
2. 使用 Google 帳號登入
3. 點擊「Get API Key」或「Create API Key」
4. 複製生成的 API Key

### 步驟 2: 設定環境變數

編輯 `.env` 檔案：
```powershell
notepad .env
```

找到這一行：
```
GEMINI_API_KEY=your_gemini_api_key_here
```

替換為您的實際 API Key：
```
GEMINI_API_KEY=AIzaSyC...您的實際Key
```

### 步驟 3: 重新啟動後端服務

```powershell
# 重啟後端容器以載入新的環境變數
docker-compose restart backend

# 等待幾秒鐘
Start-Sleep -Seconds 5

# 確認 API Key 已載入
docker exec giftgame_backend printenv GEMINI_API_KEY
```

## 測試結果解讀

### 成功的測試輸出

PowerShell 腳本：
```
✓ Coffee Mug
  AI Guess: 咖啡杯
  Regenerate: 保溫杯
  Duration: 2.34s
  Gift ID: 1
```

Python 腳本：
```
✓ All tests passed! Gemini API is working correctly.
```

### 常見問題

#### 1. API Key 未設定
**錯誤**：
```
WARNING: Gemini API Key is not set!
```

**解決方法**：
- 檢查 `.env` 檔案中的 `GEMINI_API_KEY`
- 確保沒有多餘的空格或引號
- 重啟後端服務

#### 2. AI 猜測結果都是「神秘禮物」
**原因**：
- API Key 無效或未正確載入
- API 配額已用完
- 網路連接問題

**解決方法**：
```powershell
# 1. 檢查 API Key
docker exec giftgame_backend printenv GEMINI_API_KEY

# 2. 查看後端日誌
docker logs giftgame_backend --tail 50

# 3. 執行 Python 直接測試
docker exec giftgame_backend python test_gemini_direct.py
```

#### 3. 導入錯誤
**錯誤**：
```
✗ Failed to import: No module named 'google.generativeai'
```

**解決方法**：
```powershell
# 重新建置後端容器
docker-compose build backend
docker-compose up -d backend
```

#### 4. API 配額超限
**錯誤**：
```
Resource has been exhausted (e.g. check quota)
```

**解決方法**：
- 檢查 Google Cloud Console 的配額
- 等待配額重置（通常每日重置）
- 考慮升級到付費方案

## 測試腳本對比

| 特性 | PowerShell 腳本 | Python 腳本 |
|------|----------------|-------------|
| 測試方式 | REST API | 直接呼叫 |
| 測試範圍 | 完整流程 | API 功能 |
| 執行位置 | 本機 | 容器內 |
| 診斷能力 | 基本 | 詳細 |
| 適用場景 | 端對端測試 | API 除錯 |

## 建議的測試順序

1. **首次測試**：
   ```powershell
   # 先執行 Python 腳本確認 API 功能
   docker exec giftgame_backend python test_gemini_direct.py
   ```

2. **功能測試**：
   ```powershell
   # 再執行 PowerShell 腳本測試完整流程
   .\test-gemini.ps1
   ```

3. **前端測試**：
   - 訪問 http://localhost:3000
   - 手動填寫表單測試

## 效能參考

正常情況下的回應時間：
- 禮物猜測：1-3 秒
- 圖片提示詞生成：1-2 秒
- 重新生成：1-3 秒

如果回應時間超過 10 秒，可能是：
- 網路問題
- API 服務繁忙
- 提示詞過於複雜

## 進階除錯

### 查看完整的 API 回應

修改 `backend/gemini_service.py` 增加除錯輸出：

```python
try:
    response = self.model.generate_content(prompt)
    guess = response.text.strip()
    print(f"DEBUG - Prompt: {prompt}")
    print(f"DEBUG - Response: {guess}")
    return guess
except Exception as e:
    print(f"DEBUG - Error: {str(e)}")
    return "神秘禮物"
```

### 測試不同的 Gemini 模型

在 Python 測試腳本中修改：

```python
# 嘗試不同的模型
model = genai.GenerativeModel('gemini-1.5-pro')  # 或 'gemini-pro'
```

## 相關文件

- **QUICKSTART.md** - 快速啟動指南
- **SETUP.md** - 詳細設定說明
- **USAGE.md** - 使用手冊

## 支援

如果測試仍有問題，請：

1. 收集日誌：
```powershell
docker logs giftgame_backend > backend.log
docker logs giftgame_db > db.log
```

2. 檢查系統狀態：
```powershell
.\system-test.ps1
```

3. 查看 Gemini API 文件：
   https://ai.google.dev/docs
