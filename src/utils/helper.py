from datetime import datetime

from src.utils.types import IsoDateTimeString


def get_iso_date_time_now() -> IsoDateTimeString:
    """
    Returns the current date-time in ISO 8601 format
    """
    return IsoDateTimeString(datetime.now().isoformat())
