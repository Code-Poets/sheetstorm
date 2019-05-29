from datetime import timedelta


def timedelta_to_string(data: timedelta) -> str:
    return "{:02d}:{:02d}".format((data.seconds // 3600), (data.seconds % 3600) // 60)
