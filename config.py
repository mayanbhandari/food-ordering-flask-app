import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()


class Config:
    # Secret key for sessions & CSRF
    SECRET_KEY = os.environ.get(
        "SECRET_KEY", "dev-secret-key-change-in-production")

    # Use DATABASE_URL from .env, fallback to MySQL fooddelivery
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "mysql+pymysql://root@localhost/fooddelivery"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    TESTING = False


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
