import os

# 純 Python 載入 .env 檔案，避免依賴外部套件，讓本地執行極致單純
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    with open(env_path, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                key, val = line.split("=", 1)
                os.environ[key.strip()] = val.strip()

# ==========================================
# 監控設定
# ==========================================
THEATER_ID = os.getenv("THEATER_ID", "91")

# ==========================================
# 通知管道設定
# ==========================================
NOTIFICATION_CHANNEL = os.getenv("NOTIFICATION_CHANNEL", "discord").lower()
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "")
