from abc import ABC, abstractmethod

class BaseNotifier(ABC):
    @abstractmethod
    def send(self, chain: str, theater_name: str, fri_str: str, thu_str: str, movie_count: int, target_url: str):
        pass
