import os
import functions_framework
from core.orchestrator import run

@functions_framework.http
def main(request):
    # Step 2 重構階段：依然保持向後相容，預設只觸發 showtimes，不讀取 Payload
    force_notify = os.getenv("TEST_NOTIFICATION") == "1"
    run(chain="showtimes", force_notify=force_notify)
    return "OK"

if __name__ == "__main__":
    force_notify = os.getenv("TEST_NOTIFICATION") == "1"
    run(chain="showtimes", force_notify=force_notify)
