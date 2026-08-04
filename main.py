import os
import functions_framework
from core.orchestrator import run

@functions_framework.http
def main(request):
    request_json = request.get_json(silent=True)
    if request_json and 'chain' in request_json:
        chain = request_json['chain']
    else:
        chain = os.getenv("CHAIN", "showtimes")
        
    force_notify = os.getenv("TEST_NOTIFICATION") == "1"
    run(chain=chain, force_notify=force_notify)
    return "OK"

if __name__ == "__main__":
    chain = os.getenv("CHAIN", "showtimes")
    force_notify = os.getenv("TEST_NOTIFICATION") == "1"
    run(chain=chain, force_notify=force_notify)
