class Config(object):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:hdrn59!@localhost/login"
    SECRET_KEY = 'gfgsdjfghjkfgksdgfksgdkjgdskjfgsdkjgdkjgjd'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

# class ProductionConfig(Config):
#     DATABASE_URI = 'mysql://user@localhost/foo'

# class DevelopmentConfig(Config):
#     DEBUG = True

# class TestingConfig(Config):
#     TESTING = True