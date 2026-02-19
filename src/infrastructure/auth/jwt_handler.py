from datetime import datetime, timedelta, timezone

import jwt

from src.config import settings


def create_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
