import os


class Config:
    SECRET_KEY = os.urandom(24)  # Necessary for session handling
    SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
