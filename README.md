# 電影院售票開放通知系統 (秀泰 & 威秀)

這個系統會定時監控**秀泰影城**與**威秀影城**是否開放了本週末的場次，並透過 Discord 或 Telegram 發送通知。

系統採用模組化設計與 Scheme A (Payload 分發) 架構，支援平行監控多個影城體系。

## 系統架構 (Scheme A)

我們使用 Google Cloud Functions 作為核心，並透過 Cloud Scheduler 傳入 JSON Payload 來觸發不同影城的檢查，實作平行處理與高擴充性。

```mermaid
graph TD
    subgraph Cloud Scheduler
        S_Showtimes["Job: 秀泰 (週三)"]
        S_Vieshow["Job: 威秀 (週三)"]
    end

    S_Showtimes -- Payload: {"chain":"showtimes"} --> GC["Cloud Function (main.py)"]
    S_Vieshow -- Payload: {"chain":"vieshow"} --> GC

    GC --> DP["Orchestrator (調度器)"]

    subgraph Fetchers (抓取策略)
        DP --> F_Showtimes["ShowtimesFetcher"]
        DP --> F_Vieshow["VieshowFetcher (板橋)"]
    end

    subgraph Notifiers (通知管道)
        DP --> N_Discord["DiscordNotifier"]
        DP --> N_Telegram["TelegramNotifier"]
    end
```

## 監控目標與簡化策略
為了簡化架構，系統採用「指標性分店監控」策略。根據影城慣例，全台分店通常會同步開放場次，因此我們只需要監控一個代表性分店即可：
- **秀泰影城**：預設監控 **大巨蛋秀泰影城** (ID: 91)。
- **威秀影城**：預設監控 **板橋大遠百威秀影城**。

*(秀泰的完整影城 ID 清單請參考本文末附錄)*

## 本地測試與執行 (使用 Makefile)

我們準備了快捷指令，讓您可以分開測試不同的影城：

1. **安裝套件**：
   ```bash
   make install
   ```
2. **設定通知**：
   打開 `.env` 檔案，填入對應的 Webhook URL 或 Telegram Channel ID：
   - 秀泰通知：`WEBHOOK_URL` 或 `TELEGRAM_CHANNEL_ID`
   - 威秀通知：`VIESHOW_WEBHOOK_URL` 或 `VIESHOW_TELEGRAM_CHANNEL_ID`

3. **個別影城檢查與測試**：
   - 檢查秀泰：`make run-showtimes`
   - 檢查威秀：`make run-vieshow`
   - 強制測試秀泰通知：`make test-showtimes`
   - 強制測試威秀通知：`make test-vieshow`

4. **清除本地快取與狀態**：
   ```bash
   make clean
   ```

## 雲端部署 (GCP)

### 1. 首次初始化 (僅需執行一次)
```bash
make setup
```

### 2. 快速部署 (更新程式碼、排程或通知管道時執行)
```bash
make deploy
```
系統會自動更新 Cloud Functions，並在 Cloud Scheduler 建立兩個獨立的 Job：
- `showtimes-notifier-trigger` (傳送 payload `{"chain": "showtimes"}`)
- `vieshow-notifier-trigger` (傳送 payload `{"chain": "vieshow"}`)

---

## 附錄：秀泰影城 ID 清單
如果想變更秀泰的監控影城，可以在 Payload 或環境變數中修改 `THEATER_ID`：

### 台北/新北
- **91** - 大巨蛋秀泰影城 (預設)
- **2** - 台北欣欣秀泰影城
- **55** - 土城秀泰影城
- **54** - 樹林秀泰影城

### 台中
- **53** - 台中站前秀泰影城
- **56** - 台中文心秀泰影城
- **59** - 台中麗寶秀泰影城

### 南部/東部/其他
- **9** - 嘉義秀泰影城
- **5** - 基隆秀泰影城
- **3** - 花蓮秀泰影城
- **7** - 台東秀泰影城
- **58** - 北港秀泰影城
- **60** - 台南仁德秀泰影城
- **84** - 高雄岡山秀泰影城
- **87** - 高雄夢時代秀泰影城
