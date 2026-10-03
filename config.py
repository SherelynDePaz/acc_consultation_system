import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "acc-consultation-dev-secret-change-me")
    DATABASE = os.path.join(BASE_DIR, "database", "acc_consultation.db")
    SCHEMA_PATH = os.path.join(BASE_DIR, "database", "schema.sql")
