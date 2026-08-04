import requests
import datetime
from bs4 import BeautifulSoup
from .base import BaseFetcher
from core import config

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Mobile Safari/537.36",
    "Origin": "https://www.vscinemas.com.tw",
    "Referer": "https://www.vscinemas.com.tw/ShowTimes/",
    "X-Requested-With": "XMLHttpRequest",
    "Content-Type": "application/x-www-form-urlencoded",
}

class VieshowFetcher(BaseFetcher):
    def fetch_and_check(self, fri_str: str, thu_str: str) -> dict:
        print("正在抓取威秀影城官方 API (通過 Session & Queue-It 驗證)...")
        
        try:
            fri_date = datetime.datetime.strptime(fri_str, "%Y-%m-%d")
            today = datetime.datetime.now()
            
            fri_str_tw = fri_date.strftime("%m月%d日")
            today_str_tw = today.strftime("%m月%d日")
        except Exception as e:
            print(f"❌ 日期格式轉換失敗: {e}")
            return None
            
        s = requests.Session()
        
        # 1. 抓取首頁以獲取 ASP.NET SessionId 與 Queue-It Cookie
        try:
            s.get("https://www.vscinemas.com.tw/ShowTimes/", headers=HEADERS, timeout=10)
        except Exception as e:
            print(f"❌ 抓取威秀首頁獲取 Cookie 失敗: {e}")
            return None
            
        # 2. 發送 POST 請求獲取場次 HTML
        cinema_code = config.VIESHOW_CINEMA_CODE
        print(f"目標影城代碼: {cinema_code}")
        
        try:
            r = s.post(
                "https://www.vscinemas.com.tw/ShowTimes/ShowTimes/GetShowTimes",
                headers=HEADERS,
                data={"CinemaCode": cinema_code},
                timeout=10
            )
            r.raise_for_status()
        except Exception as e:
            print(f"❌ 抓取威秀官方 API 失敗: {e}")
            return None
            
        soup = BeautifulSoup(r.text, "html.parser")
        
        today_movies = set()
        fri_movies = set()
        
        for movie_tag in soup.find_all("strong", class_="MovieName"):
            movie_name = movie_tag.text.strip()
            parent_div = movie_tag.parent
            if not parent_div:
                continue
                
            dates = [d.text.strip() for d in parent_div.find_all("strong", class_="RealShowDate")]
            
            if any(today_str_tw in d for d in dates):
                today_movies.add(movie_name)
            if any(fri_str_tw in d for d in dates):
                fri_movies.add(movie_name)
                
        n_today = len(today_movies)
        n_fri = len(fri_movies)
        
        print(f"[場次統計] 今天 ({today_str_tw}): {n_today} 部")
        print(f"[場次統計] 週五 ({fri_str_tw}): {n_fri} 部 (包含預售/應援場)")
        print(f"週五上映清單: {fri_movies}")
        
        if n_today == 0:
            print("❌ 警告：今天居然沒有任何電影？無法計算比例。")
            return None
            
        ratio = n_fri / n_today
        print(f"開放比例 (週五/今天): {ratio:.2f} (大於 0.50 即判定為全面開放)")
        
        is_opened = ratio > 0.50
        
        return {
            "is_opened": is_opened,
            "theater_name": "威秀影城",
            "movie_count": n_fri,
            "target_url": "https://www.vscinemas.com.tw/vsTicketing/ticketing/ticket.aspx"
        }
