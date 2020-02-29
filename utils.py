from datetime import datetime

import pytz
from pytz import timezone


def get_time_in_iran_timezone() -> datetime:
    return datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(timezone('Iran'))


def make_aware(db_date: datetime) -> datetime:
    tz = timezone('Iran')
    return tz.localize(db_date)
