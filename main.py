import os
import requests
from datetime import datetime, timedelta
import functions_framework
import config

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Origin": "https://www.showtimes.com.tw",
    "Referer": "https://www.showtimes.com.tw/",
    "Accept": "application/json, text/plain, */*",
}

STATE_FILE = "state.txt"

def get_upcoming_weekend():
    today = datetime.now()
    if today.weekday() > 4:
        next_fri = today + timedelta(days=(4 - today.weekday() + 7))
    else:
        next_fri = today + timedelta(days=(4 - today.weekday()))
    
    next_sat = next_fri + timedelta(days=1)
    next_sun = next_fri + timedelta(days=2)
    
    return next_fri.strftime("%Y-%m-%d"), next_sat.strftime("%Y-%m-%d"), next_sun.strftime("%Y-%m-%d")

def is_already_notified(date_str):
    if os.getenv("K_SERVICE"):
        from google.cloud import firestore
        db = firestore.Client()
        doc_ref = db.collection("state").document("notifier")
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict().get("last_notified") == date_str
        return False
    else:
        if not os.path.exists(STATE_FILE):
            return False
        with open(STATE_FILE, "r") as f:
            return f.read().strip() == date_str

def mark_as_notified(date_str):
    if os.getenv("K_SERVICE"):
        from google.cloud import firestore
        db = firestore.Client()
        doc_ref = db.collection("state").document("notifier")
        doc_ref.set({"last_notified": date_str})
    else:
        with open(STATE_FILE, "w") as f:
            f.write(date_str)

def send_notification(theater_name, fri_str, sun_str, movie_count):
    # 動態代入 THEATER_ID，確保未來換影城時連結依然 100% 正確
    target_url = f"https://www.showtimes.com.tw/ticketing/?cid={config.THEATER_ID}"
    short_name = theater_name.replace("影城", "")
    f_date = fri_str[5:].replace("-", "/")
    s_date = sun_str[5:].replace("-", "/")
    
    print(f"\n[準備發送通知] {short_name} | {f_date}~{s_date} | {movie_count}部電影")
    
    if config.NOTIFICATION_CHANNEL == "discord":
        if not config.WEBHOOK_URL:
            print("❌ 錯誤：未設定 WEBHOOK_URL。通知未發送。")
            return
        # 極簡化卡片訊息，無 Emoji，標題即連結
        payload = {
            "embeds": [
                {
                    "title": f"【{short_name}】本週末場次開放！",
                    "url": target_url,
                    "description": f"{f_date} ~ {s_date} (共 {movie_count} 部電影)",
                    "color": 15158332
                }
            ]
        }
        r = requests.post(config.WEBHOOK_URL, json=payload)
        if r.status_code == 204:
            print("✅ Discord 通知發送成功！")
        else:
            print(f"❌ Discord 通知發送失敗：{r.text}")
            
    elif config.NOTIFICATION_CHANNEL == "telegram":
        if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_CHANNEL_ID:
            print("❌ 錯誤：未設定 Telegram Token 或 Channel ID。通知未發送。")
            return
        url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
        # 極簡化 Telegram 訊息
        payload = {
            "chat_id": config.TELEGRAM_CHANNEL_ID,
            "text": f"**【{short_name}】本週末場次開放！**\n{f_date} ~ {s_date} (共 {movie_count} 部電影)",
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
    else:
        print(f"❌ 錯誤：未知的通知管道 {config.NOTIFICATION_CHANNEL}")

def run_check():
    print("=========================================")
    print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"目標影城 ID: {config.THEATER_ID}")
    print(f"通知管道: {config.NOTIFICATION_CHANNEL}")
    
    print("正在抓取秀泰影城 API...")
    try:
        r = requests.get("https://capi.showtimes.com.tw/4/app/bootstrap", headers=HEADERS)
        r.raise_for_status()
        data = r.json()['payload']
    except Exception as e:
        print(f"❌ API 請求失敗: {e}")
        return
        
    theaters = {str(c['id']): c['name'] for c in data.get('corporations', [])}
    theater_name = theaters.get(str(config.THEATER_ID), f"影城({config.THEATER_ID})")
    print(f"解析成功，影城名稱: {theater_name}")
    
    events_all = data.get('eventsForCorporations', {})
    events_theater = events_all.get(str(config.THEATER_ID), {}).get('events', [])
    
    if not events_theater:
        print(f"❌ 警告：沒找到該影城的場次資料。")
        return
        
    today_str = datetime.now().strftime("%Y-%m-%d")
    fri_str, sat_str, sun_str = get_upcoming_weekend()
    
    today_movies = set()
    fri_movies = set()
    sat_movies = set()
    sun_movies = set()
    
    for e in events_theater:
        d = e['startedAt'][:10]
        if d == today_str:
            today_movies.add(e['programId'])
        elif d == fri_str:
            fri_movies.add(e['programId'])
        elif d == sat_str:
            sat_movies.add(e['programId'])
        elif d == sun_str:
            sun_movies.add(e['programId'])
            
    n_today = len(today_movies)
    n_fri = len(fri_movies)
    n_sat = len(sat_movies)
    n_sun = len(sun_movies)
    
    # 寫 log (詳細印出各天數量，精準保留您修改後的無 emoji 清潔風格)
    print(f"[場次統計] 今天 ({today_str}): {n_today} 部")
    print(f"[場次統計] 週五 ({fri_str}): {n_fri} 部")
    print(f"[場次統計] 週六 ({sat_str}): {n_sat} 部")
    print(f"[場次統計] 週日 ({sun_str}): {n_sun} 部")
    
    # 取聯集，計算本週末共有幾部電影
    weekend_movies = fri_movies | sat_movies | sun_movies
    n_weekend = len(weekend_movies)
    print(f"本週末總計 (聯集): {n_weekend} 部電影")
    
    if n_today == 0:
        print("❌ 警告：今天居然沒有任何電影？無法計算比例。")
        return
        
    # 開放比例：只比較今天和週五 (精準避開六日早期預售票的比例稀釋)
    ratio = n_fri / n_today
    print(f"開放比例 (週五/今天): {ratio:.2f} (大於 0.50 即判定為全面開放)")
    
    force_notify = os.getenv("TEST_NOTIFICATION") == "1"
    if ratio > 0.50 or force_notify:
        if force_notify:
            print("⚠️ [測試模式] 強制發送通知！")
        print("🎉 偵測到全面開放！")
        if not force_notify and is_already_notified(fri_str):
            print("🤫 今天已經通知過了，不再重複轟炸。")
        else:
            send_notification(theater_name, fri_str, sun_str, n_weekend)
            if not force_notify:
                mark_as_notified(fri_str)
    else:
        print("⏳ 尚未全面開放，繼續等待...")
        
    print("=========================================")

@functions_framework.http
def main(request):
    run_check()
    return "OK"

if __name__ == "__main__":
    run_check()
