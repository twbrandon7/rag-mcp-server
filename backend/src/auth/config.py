
from pydantic import BaseModel

from src.config import settings


class JWTSettings(BaseModel):
    secret_key: str = settings.SECRET_KEY
    algorithm: str = "HS256"
    access_token_expire_minutes: int = settings.ACCESS_TOKEN_EXPIRE_MINUTES


jwt_settings = JWTSettings()
