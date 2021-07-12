from flask_caching import Cache

config = {
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
}

cache = Cache()


def set_cache(app):
    app.config.update(config)
    cache.init_app(app)
