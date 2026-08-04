import os

# 載入 .env 檔案中的環境變數
# 注意：因為此檔案在 core/ 目錄下，故需要往上一層尋找 .env
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
if os.path.exists(env_path):
    with open(env_path, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                key, val = line.split("=", 1)
                os.environ[key.strip()] = val.strip()

# ==========================================
# 監控設定 (秀泰)
# ==========================================
THEATER_ID = os.getenv("THEATER_ID", "91")

# ==========================================
# 監控設定 (威秀)
# ==========================================
VIESHOW_CINEMA_CODE = os.getenv("VIESHOW_CINEMA_CODE", "BQ")

# ==========================================
# 通知管道設定
# ==========================================
NOTIFICATION_CHANNEL = os.getenv("NOTIFICATION_CHANNEL", "discord").lower()

# 秀泰通知
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "")

# 威秀通知 (Step 3 使用)
VIESHOW_WEBHOOK_URL = os.getenv("VIESHOW_WEBHOOK_URL", "")
VIESHOW_TELEGRAM_CHANNEL_ID = os.getenv("VIESHOW_TELEGRAM_CHANNEL_ID", "")
