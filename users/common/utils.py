import datetime
import logging
import random
import string
from typing import Optional

logger = logging.getLogger(__name__)


def generate_random_string_from_letters_and_digits(length):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_random_phone_number(length):
    return "".join(random.choices(string.digits, k=length))


def count_workdays(start_date: datetime.date, days_number: int) -> Optional[int]:
    return sum(
        [
            True
            for days_delta in range(1, days_number)
            if (start_date + datetime.timedelta(days=days_delta)).isoweekday() < 6
        ]
    )
