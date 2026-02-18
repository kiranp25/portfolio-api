from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    APP_NAME: str = 'portfolio_api'
    APP_ENV: str = 'development'
    APP_PORT: int = 8000
    PUBLIC_BASE_URL: str


    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379/0"

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    REFREH_TOKEN_EXPIRE_DAYS: int = 7
    PUBLIC_PROFILE_CACHE_TTL_SECONDS: int = 300
    RATE_LIMIT_LOGIN_REQUESTS: int = 10
    RATE_LIMIT_LOGIN_WINDOW_SECONDS: int = 60
    RATE_LIMIT_PUBLIC_REQUESTS: int = 60
    RATE_LIMIT_PUBLIC_WINDOW_SECONDS: int = 60

    model_config = {
        "env_file":".env",
        "extra":"ignore",
    } 


settings = Settings()
