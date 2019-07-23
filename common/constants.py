import re

CORRECT_DATE_FORMAT = "YYYY-MM-DD"

DOMAIN_REGEX = re.compile(
    r"(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}|[A-Z0-9-]{2,})$|localhost"  # domain
    # literal form, ipv4 address (SMTP 4.1.3)
    r"|^\[(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}\]$",
    re.IGNORECASE,
)
