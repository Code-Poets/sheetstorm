import logging
import random
import string

logger = logging.getLogger(__name__)


def generate_random_string_from_letters_and_digits(length):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_random_phone_number(length):
    return "".join(random.choices(string.digits, k=length))
