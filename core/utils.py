from datetime import datetime, timedelta

def get_upcoming_week():
    today = datetime.now()
    if today.weekday() > 4:
        next_fri = today + timedelta(days=(4 - today.weekday() + 7))
    else:
        next_fri = today + timedelta(days=(4 - today.weekday()))
    
    next_thu = next_fri + timedelta(days=6)
    
    return next_fri.strftime("%Y-%m-%d"), next_thu.strftime("%Y-%m-%d")
