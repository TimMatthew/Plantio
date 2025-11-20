from datetime import UTC, datetime


def utcnow_tz():
    return datetime.now(UTC)
