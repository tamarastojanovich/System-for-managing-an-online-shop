import os
from datetime import timedelta


DATABASE_URL = "shop" if ( "PRODUCTION" in os.environ ) else "localhost:3308"

class Configuration:
    SQLALCHEMY_DATABASE_URI = f"mysql://root:root@{DATABASE_URL}/shopInfo"
    JWT_SECRET_KEY = "JWT_SECRET_DEV_KEY"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta( hours = 1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta ( days = 30)