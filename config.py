import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "tajne-haslo"
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "app.db?check_same_thread=False")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    LANGUAGES = ["pl", "en"]

    ELEMENTS_PER_PAGE = 10

    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = int(os.environ.get("MAIL_PORT") or 25)
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS") is not None
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    ADMINS = ["mail@example.com"]

    ELASTICSEARCH_URL = os.environ.get("ELASTICSEARCH_URL")

    UPLOAD_FOLDER = os.path.join(basedir, "app", "static", "uploads")
    REPORTS_FOLDER = os.path.join(basedir, "app", "static", "reports")
    ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg", "gif", "csv"}
    MAX_FILE_FILESIZE = 5 * 1024 * 1024

    REDIS_URL = os.environ.get("REDIS_URL") or "redis://localhost:6379"


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URL") or "sqlite://"
    WTF_CSRF_ENABLED = False
