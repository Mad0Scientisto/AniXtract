import time
from datetime import time
from urllib.parse import urlparse


def convert_millisec_to_timeobj(millisec: int) -> time:
    seconds_tot = millisec // 1000
    # hours = total_time_video // 3600
    minutes = (seconds_tot // 60) % 60
    seconds = seconds_tot % 60
    return time(minute=minutes, second=seconds)


def convert_timeobj_to_milliseconds(timeobj: time) -> int:
    hours, minutes, seconds = timeobj.hour, timeobj.minute, timeobj.second
    totSec = hours * 3600 + minutes * 60 + seconds
    return totSec * 1000


def check_valid_youtube_url(url_youtube: str) -> bool:
    result = urlparse(url_youtube)
    return True if result.scheme in ['http', 'https'] and\
                   'youtube.com' in result.netloc and\
                   '/watch' in result.path and\
                   'v=' in result.query else False
