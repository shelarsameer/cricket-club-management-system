import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:root@localhost:5432/cricket_club'
    SQLALCHEMY_TRACK_MODIFICATIONS = False 