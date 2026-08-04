import requests
from .base import BaseNotifier
from core import config

class TelegramNotifier(BaseNotifier):
    def send(self, chain: str, theater_name: str, fri_str: str, thu_str: str, movie_count: int, target_url: str):
        if chain == "vieshow":
            channel_id = config.VIESHOW_TELEGRAM_CHANNEL_ID
            var_name = "VIESHOW_TELEGRAM_CHANNEL_ID"
        else:
            channel_id = config.TELEGRAM_CHANNEL_ID
            var_name = "TELEGRAM_CHANNEL_ID"
            
        if not config.TELEGRAM_BOT_TOKEN:
            print("❌ 錯誤：未設定 TELEGRAM_BOT_TOKEN。通知未發送。")
            return
        if not channel_id:
            print(f"❌ 錯誤：未設定 {var_name}。通知未發送。")
            return
            
        short_name = theater_name.replace("影城", "")
        f_date = fri_str[5:].replace("-", "/")
        t_date = thu_str[5:].replace("-", "/")
        unit = "個場次" if chain == "vieshow" else "部電影"
        
        print(f"\n[準備發送 Telegram 通知] {short_name} | {f_date}~{t_date} | {movie_count}{unit}")
        
        url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": channel_id,
            "text": f"**【{short_name}】場次開放 (週五至下週四)！**\n{f_date} ~ {t_date} (共 {movie_count} {unit})",
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
