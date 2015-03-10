import os
CSRF_ENABLE = True
basedir = os.path.abspath(os.path.dirname(__file__))
MONKEYS_PAGE = 2


class Config(object):
    DEBUG = False
    SECRET_KEY = 'Thisismysecretkey'
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'postgresql+psycopg2://localhost/app')
    print SQLALCHEMY_DATABASE_URI


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'postgresql+psycopg2://localhost/testapp')
    print SQLALCHEMY_DATABASE_URI


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


class HerokuConfig(ProductionConfig):
    def init_app(cls, app):
        ProductionConfig.init_app(app)
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.WARNING)
        app.logger.addHandler(file_handler)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'heroku': HerokuConfig,
    'default': DevelopmentConfig
}
