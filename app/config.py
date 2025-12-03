import os

POSTGRES_USER = os.getenv("POSTGRES_USER", "fastapi_app")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "secret")
POSTGRES_DB = os.getenv("POSTGRES_DB", "fastapi_app")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5431")

POSTGRES_DSN = (
    f"postgresql+asyncpg://"
    f"{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
    f"{POSTGRES_HOST}:{POSTGRES_PORT}/"
    f"{POSTGRES_DB}"
)

TOKEN_TTL_SEC = os.getenv("TOKEN_TTL", 172800)
