from datetime import datetime, timezone

def get_date_from_str(date):
    for fmt in ('%Y-%m-%d', '%d %B %Y, %Z'):
        try:
            return datetime.strptime(date, fmt)
        except ValueError:
            pass

def dt_to_str(dt: datetime):
    return dt.strftime("%a, %d %b %Y %H:%M:%S GMT")

def dt_to_int(dt: datetime):
    utc_time: datetime = dt.replace(tzinfo=timezone.utc)
    return int(round(utc_time.timestamp())) * 1000

def make_res(dt):
    return {"unix": dt_to_int(dt), "utc": dt_to_str(dt)}
