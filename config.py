import os
import time

from dotenv import load_dotenv

# Читаем файл .env (если он есть) ДО обращения к os.environ.
load_dotenv()

SQLITE_URL = "sqlite:///accessevent.db"


def _fix_driver(url):
    """postgres:// -> postgresql://; выбираем установленный драйвер."""
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    if url.startswith("postgresql://"):
        try:
            import psycopg2  # noqa: F401
        except ImportError:
            try:
                import psycopg  # noqa: F401
                url = url.replace("postgresql://", "postgresql+psycopg://", 1)
            except ImportError:
                pass
    return url


def _database_url():
    """PostgreSQL из .env; если не подключается - запасной SQLite.

    Так приложение запускается даже при неверном пароле или выключенной
    службе PostgreSQL, а причина выводится в терминал.
    """
    url = os.environ.get("DATABASE_URL", "").strip()
    if not url or os.environ.get("USE_SQLITE") == "1":
        return SQLITE_URL

    url = _fix_driver(url)
    if url.startswith("sqlite"):
        return url
    from sqlalchemy import create_engine

    retries = int(os.environ.get("DB_CONNECT_RETRIES", "1"))
    strict = os.environ.get("DB_STRICT") == "1"
    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            engine = create_engine(url, connect_args={"connect_timeout": 3})
            with engine.connect():
                pass
            engine.dispose()
            print("[config] Подключено к PostgreSQL")
            return url
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            if attempt < retries:
                print(f"[config] База не готова (попытка {attempt}/{retries}), "
                      "жду 2 сек...")
                time.sleep(2)

    if strict:
        # В Docker лучше упасть с понятной ошибкой, чем тихо взять SQLite
        raise RuntimeError("Не удалось подключиться к PostgreSQL: "
                           f"{type(last_exc).__name__}") from last_exc

    print("=" * 60)
    print("[config] НЕ УДАЛОСЬ подключиться к PostgreSQL.")
    print("[config] Проверьте пароль в .env, что служба PostgreSQL "
          "запущена и что база accessevent создана.")
    print("[config] Причина:", type(last_exc).__name__)
    print("[config] Запускаюсь на запасной базе SQLite (accessevent.db).")
    print("=" * 60)
    return SQLITE_URL


class Config:
    SECRET_KEY = os.environ.get(
        "SECRET_KEY", "dev-secret-key-for-accessevent-at-least-32-bytes"
    )
    SQLALCHEMY_DATABASE_URI = _database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_EXPIRATION_HOURS = 24
