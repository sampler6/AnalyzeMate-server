import os

from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
SECRET = os.environ.get("SECRET")
TOKEN = os.environ.get("TOKEN")
STOCK_MARKET = os.environ.get("STOCK_MARKET")
REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD")

APP_HOST = os.environ.get("APP_HOST")
APP_PORT = os.environ.get("APP_PORT")

if not SECRET:
    raise Exception("SECRET is not defined")
