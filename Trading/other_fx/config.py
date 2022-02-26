import os

class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://postgres:admin@localhost:5432/postgres')
    W_UPDATE = os.environ.get('W_UPDATE', 'True')
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379')
    CACHE_DEFAULT_TIMEOU = 60 * 60 * 2

Config = DevelopmentConfig
