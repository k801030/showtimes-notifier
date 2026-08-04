from datetime import datetime
from core import config, state, utils
from fetchers.showtimes import ShowtimesFetcher
from notifiers.discord import DiscordNotifier
from notifiers.telegram import TelegramNotifier

def run(chain: str, force_notify: bool):
    print("=========================================")
    print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"執行影城體系: {chain}")
    print(f"通知管道: {config.NOTIFICATION_CHANNEL}")
    
    # 1. 取得對應的 Fetcher
    if chain == "showtimes":
        fetcher = ShowtimesFetcher()
    elif chain == "vieshow":
        from fetchers.vieshow import VieshowFetcher
        fetcher = VieshowFetcher()
    else:
        print(f"❌ 未知的影城體系: {chain}")
        return
        
    fri_str, thu_str = utils.get_upcoming_week()
    
    # 2. 檢查狀態是否已經通知過
    if not force_notify and state.is_already_notified(chain, fri_str):
        print("🤫 今天已經通知過了，不再重複轟炸。")
        return
        
    # 3. 執行抓取與開放判斷
    result = fetcher.fetch_and_check(fri_str, thu_str)
    if not result:
        return
        
    # 4. 根據判斷結果發送通知
    is_opened = result["is_opened"]
    if is_opened or force_notify:
        if force_notify:
            print("⚠️ [測試模式] 強制發送通知！")
        print("🎉 偵測到全面開放！")
        
        if config.NOTIFICATION_CHANNEL == "discord":
            notifier = DiscordNotifier()
            notifier.send(chain, result["theater_name"], fri_str, thu_str, result["movie_count"], result["target_url"])
        elif config.NOTIFICATION_CHANNEL == "telegram":
            notifier = TelegramNotifier()
            notifier.send(chain, result["theater_name"], fri_str, thu_str, result["movie_count"], result["target_url"])
        else:
            print(f"❌ 錯誤：未知的通知管道 {config.NOTIFICATION_CHANNEL}")
            
        if not force_notify:
            state.mark_as_notified(chain, fri_str)
    else:
        print("⏳ 尚未全面開放，繼續等待...")
        
    print("=========================================")
