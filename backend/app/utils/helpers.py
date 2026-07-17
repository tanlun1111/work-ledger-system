from datetime import datetime


def format_datetime(value, fmt="%Y-%m-%d %H:%M"):
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return value.strftime(fmt)


def truncate_text(text, max_length=80):
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def parse_datetime(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d %H:%M")
    except ValueError:
        try:
            return datetime.strptime(value, "%Y-%m-%dT%H:%M")
        except ValueError:
            return None
