import os


class Settings:
    SECRET_KEY = os.getenv("SECRET_KEY", "development-only-change-me")
    DATABASE_PATH = os.getenv("DATABASE_PATH", "loja.db")
    DEBUG = os.getenv("FLASK_DEBUG", "0").lower() in {"1", "true", "yes"}
    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", "5000"))
