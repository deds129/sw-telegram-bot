from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    BOT_TOKEN: str
    DATABASE_URL: str
    WEBHOOK_ENABLED: bool = False
    WEBHOOK_URL: str | None = None
    WEBHOOK_PATH: str | None = None
    WEBAPP_HOST: str = "0.0.0.0"
    WEBAPP_PORT: int = 8000
    MAX_HABITS_PER_USER: int = 3

settings = Settings()