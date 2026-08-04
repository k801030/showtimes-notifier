from abc import ABC, abstractmethod

class BaseFetcher(ABC):
    @abstractmethod
    def fetch_and_check(self, fri_str: str, thu_str: str) -> dict:
        """
        抓取資料並判斷是否全面開放。
        傳回值格式:
        {
            "is_opened": bool,
            "theater_name": str,
            "movie_count": int,
            "target_url": str
        }
        若抓取失敗則傳回 None。
        """
        pass
