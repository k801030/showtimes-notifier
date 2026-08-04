import requests
import datetime
from .base import BaseFetcher
from core import config

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Origin": "https://www.showtimes.com.tw",
    "Referer": "https://www.showtimes.com.tw/",
    "Accept": "application/json, text/plain, */*",
}

class ShowtimesFetcher(BaseFetcher):
    def fetch_and_check(self, fri_str: str, thu_str: str) -> dict:
        print("正在抓取秀泰影城 API...")
        try:
            r = requests.get("https://capi.showtimes.com.tw/4/app/bootstrap", headers=HEADERS)
            r.raise_for_status()
            data = r.json()['payload']
        except Exception as e:
            print(f"❌ API 請求失敗: {e}")
            return None
            
        theaters = {str(c['id']): c['name'] for c in data.get('corporations', [])}
        theater_name = theaters.get(str(config.THEATER_ID), f"影城({config.THEATER_ID})")
        print(f"解析成功，影城名稱: {theater_name}")
        
        events_all = data.get('eventsForCorporations', {})
        events_theater = events_all.get(str(config.THEATER_ID), {}).get('events', [])
        
        if not events_theater:
            print(f"❌ 警告：沒找到該影城的場次資料。")
            return None
            
        today_str = datetime.datetime.now().strftime("%Y-%m-%d")
        
        today_movies = set()
        fri_movies = set()
        week_movies = set()
        
        for e in events_theater:
            d = e['startedAt'][:10]
            if d == today_str:
                today_movies.add(e['programId'])
            if fri_str <= d <= thu_str:
                week_movies.add(e['programId'])
            if d == fri_str:
                fri_movies.add(e['programId'])
                
        n_today = len(today_movies)
        n_fri = len(fri_movies)
        n_week = len(week_movies)
        
        print(f"[場次統計] 今天 ({today_str}): {n_today} 部")
        print(f"[場次統計] 週五 ({fri_str}): {n_fri} 部")
        print(f"[場次統計] 全週總計 ({fri_str}~{thu_str}): {n_week} 部電影")
        
        if n_today == 0:
            print("❌ 警告：今天居然沒有任何電影？無法計算比例。")
            return None
            
        ratio = n_fri / n_today
        print(f"開放比例 (週五/今天): {ratio:.2f} (大於 0.50 即判定為全面開放)")
        
        is_opened = ratio > 0.50
        
        return {
            "is_opened": is_opened,
            "theater_name": theater_name,
            "movie_count": n_week,
            "target_url": f"https://www.showtimes.com.tw/ticketing/?cid={config.THEATER_ID}"
        }
