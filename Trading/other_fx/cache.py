import os
from flask_caching import Cache

# Cacheインスタンスの作成
cache = Cache(config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': os.environ.get('REDIS_URL', 'redis://localhost:6379'),
    'CACHE_DEFAULT_TIMEOUT': 60 * 60 * 2,
})

# Database Connection
def init_cache(app):
    cache.init_app(app)
