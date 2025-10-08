from fastapi import APIRouter
from datetime import datetime

router = APIRouter(prefix="/testapi", tags=["Test API"])

'''
This file corresponds to a test API, used to see if it's correcty configured.

The only endpoint (so far) is a GET request that returns the current local time
'''


def _time_of_day(hour: int) -> str:
    """Return a simple label for hour -> time of day."""
    if 5 <= hour < 12:
        return "morning"
    if 12 <= hour < 18:
        return "afternoon"
    if 18 <= hour < 22:
        return "evening"
    return "night"

@router.get("/time", summary="Get current local time and time-of-day")
def get_time():
    """
    Returns the current server local datetime (ISO) and a time-of-day label.
    This endpoint is intentionally simple for local development.
    """
    now = datetime.now().astimezone()   # timezone-aware local time
    hour = now.hour
    return {
        "now": now.isoformat(),
        "time_of_day": _time_of_day(hour),
        "hour": hour,
        "timezone": now.tzname() or str(now.utcoffset())
    }


