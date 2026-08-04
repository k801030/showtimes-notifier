import os
import json

STATE_FILE = "state.txt"

def is_already_notified(chain: str, date_str: str) -> bool:
    if os.getenv("K_SERVICE"):
        from google.cloud import firestore
        db = firestore.Client()
        # 為保持向後相容，showtimes 依然使用舊的 document ID "notifier"
        doc_id = "notifier" if chain == "showtimes" else chain
        doc_ref = db.collection("state").document(doc_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict().get("last_notified") == date_str
        return False
    else:
        if not os.path.exists(STATE_FILE):
            return False
        
        # 本地檔案支援 JSON 格式以區分不同影城。若讀取失敗（舊格式），則視為 showtimes 的狀態
        try:
            with open(STATE_FILE, "r") as f:
                content = f.read().strip()
                if not content:
                    return False
                data = json.loads(content)
                return data.get(chain) == date_str
        except (json.JSONDecodeError, AttributeError):
            if chain == "showtimes":
                with open(STATE_FILE, "r") as f:
                    return f.read().strip() == date_str
            return False

def mark_as_notified(chain: str, date_str: str):
    if os.getenv("K_SERVICE"):
        from google.cloud import firestore
        db = firestore.Client()
        doc_id = "notifier" if chain == "showtimes" else chain
        doc_ref = db.collection("state").document(doc_id)
        doc_ref.set({"last_notified": date_str})
    else:
        data = {}
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, "r") as f:
                    content = f.read().strip()
                    if content:
                        data = json.loads(content)
            except json.JSONDecodeError:
                pass
        
        data[chain] = date_str
        with open(STATE_FILE, "w") as f:
            json.dump(data, f)
