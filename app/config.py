import os

from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")

AUTH_SECRET = os.environ.get("AUTH_SECRET")
PASSWORD_RESET = os.environ.get("PASSWORD_RESET")

BOT_TOKEN = os.environ.get("BOT_TOKEN")