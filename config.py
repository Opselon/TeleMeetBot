import os

class Config:
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///telemeet.db')
    TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
