from datetime import datetime, timezone, timedelta
from time import sleep


def get_expiry(expiryIn):
    now = datetime.now(timezone.utc)
    expiry = now + timedelta(minutes=expiryIn)
    return expiry


def check_expiry(expiryDateString):
    now = datetime.now(timezone.utc)
    expiryDateObject = datetime.fromisoformat(expiryDateString)
    if (now - expiryDateObject).days < 0:
        return False
    else:
        return True
