import requests
from .base import BaseNotifier
from core import config

class DiscordNotifier(BaseNotifier):
    def send(self, chain: str, theater_name: str, fri_str: str, thu_str: str, movie_count: int, target_url: str):
        if chain == "vieshow":
            webhook_url = config.VIESHOW_WEBHOOK_URL
        else:
            webhook_url = config.WEBHOOK_URL
            
        if not webhook_url:
            print("❌ 錯誤：未設定 WEBHOOK_URL。通知未發送。")
            return
            
        short_name = theater_name.replace("影城", "")
        f_date = fri_str[5:].replace("-", "/")
        t_date = thu_str[5:].replace("-", "/")
        
        print(f"\n[準備發送 Discord 通知] {short_name} | {f_date}~{t_date} | {movie_count}部電影")
        
        payload = {
            "embeds": [
                {
                    "title": f"【{short_name}】場次開放！",
                    "url": target_url,
                    "description": f"{f_date} ~ {t_date} (共 {movie_count} 部電影)",
                    "color": 15158332
                }
            ]
        }
        r = requests.post(webhook_url, json=payload)
        if r.status_code == 204:
            print("✅ Discord 通知發送成功！")
        else:
            print(f"❌ Discord 通知發送失敗：{r.text}")
