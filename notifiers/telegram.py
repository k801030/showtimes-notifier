import requests
from .base import BaseNotifier
from core import config

class TelegramNotifier(BaseNotifier):
    def send(self, chain: str, theater_name: str, fri_str: str, thu_str: str, movie_count: int, target_url: str):
        if chain == "vieshow":
            channel_id = config.VIESHOW_TELEGRAM_CHANNEL_ID
        else:
            channel_id = config.TELEGRAM_CHANNEL_ID
            
        if not config.TELEGRAM_BOT_TOKEN or not channel_id:
            print("❌ 錯誤：未設定 Telegram Token 或 Channel ID。通知未發送。")
            return
            
        short_name = theater_name.replace("影城", "")
        f_date = fri_str[5:].replace("-", "/")
        t_date = thu_str[5:].replace("-", "/")
        
        print(f"\n[準備發送 Telegram 通知] {short_name} | {f_date}~{t_date} | {movie_count}部電影")
        
        url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": config.TELEGRAM_CHANNEL_ID,
            "text": f"**【{short_name}】場次開放 (週五至下週四)！**\n{f_date} ~ {t_date} (共 {movie_count} 部電影)",
            "parse_mode": "Markdown",
            "reply_markup": {
                "inline_keyboard": [
                    [{"text": "前往購票", "url": target_url}]
                ]
            }
        }
        r = requests.post(url, json=payload)
        if r.status_code == 200:
            print("✅ Telegram 通知發送成功！")
        else:
            print(f"❌ Telegram 通知發送失敗：{r.text}")
