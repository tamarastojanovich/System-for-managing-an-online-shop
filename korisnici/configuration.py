import os
from datetime import timedelta


DATABASE_URL = "authentication" if ( "PRODUCTION" in os.environ ) else "localhost:3307"

class Configuration:
    SQLALCHEMY_DATABASE_URI = f"mysql://root:root@{DATABASE_URL}/userInfo"
    JWT_SECRET_KEY = "JWT_SECRET_DEV_KEY"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta( hours = 1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta ( days = 30)