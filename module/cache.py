from flask_caching import Cache

config = {
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_THRESHOLD": 30,  # cache存放items數量上限，超過依timeoute過期開始刪除
}

cache = Cache()


def set_cache(app):
    app.config.update(config)
    cache.init_app(app)
