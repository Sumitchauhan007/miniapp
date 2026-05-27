import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Secret key for Flask sessions/security
    SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key")

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///leaderboard.db"
    )

    # Disable unnecessary tracking (improves performance)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Allow frontend requests
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")