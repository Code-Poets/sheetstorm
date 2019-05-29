from datetime import timedelta


def timedelta_to_string(data: timedelta) -> str:
    days = data.days
    hours = data.seconds // 3600
    minutes = (data.seconds % 3600) // 60
    return "{:02d}:{:02d}".format((hours + (days * 24)) if days > 0 else hours, minutes)
