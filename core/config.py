from pydantic import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str = "CHANGE_ME_TO_A_SECURE_RANDOM"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    DATABASE_URL: str = "sqlite:///./test.db"
    DEBUG: bool = True

    class Config:
        env_file = ".env"

settings = Settings()