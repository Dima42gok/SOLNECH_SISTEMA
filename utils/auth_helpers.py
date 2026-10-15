import datetime
import functools

import jwt
from flask import current_app, jsonify, request
from werkzeug.security import generate_password_hash

from models import db, User


def hash_password(password):
    """Хеширование пароля (PBKDF2). Никогда не сохраняем сырой пароль."""
    return generate_password_hash(password)


def generate_token(user):
    """Создание JWT с id и ролью пользователя, срок - 24 часа."""
    payload = {
        "user_id": user.id,
        "role": user.role,
        "exp": datetime.datetime.now(datetime.timezone.utc)
               + datetime.timedelta(
                   hours=current_app.config["JWT_EXPIRATION_HOURS"]),
    }
    token = jwt.encode(payload, current_app.config["SECRET_KEY"],
                       algorithm="HS256")
    # В старых версиях PyJWT encode возвращает bytes
    return token.decode("utf-8") if isinstance(token, bytes) else token


def token_required(f):
    """Декоратор: маршрут доступен только с валидным JWT в заголовке."""
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"message": "Токен отсутствует"}), 401
        token = auth_header.split("Bearer ", 1)[1].strip()
        try:
            data = jwt.decode(token, current_app.config["SECRET_KEY"],
                              algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Срок действия токена истёк"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Неверный токен"}), 401
        user = db.session.get(User, data.get("user_id"))
        if user is None:
            return jsonify({"message": "Пользователь не найден"}), 401
        return f(*args, user=user, **kwargs)
    return wrapper


def role_required(*roles):
    """Декоратор поверх token_required: проверяет роль пользователя."""
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, user, **kwargs):
            if user.role not in roles:
                return jsonify({"message": "Недостаточно прав"}), 403
            return f(*args, user=user, **kwargs)
        return wrapper
    return decorator
