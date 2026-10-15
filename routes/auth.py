from flask import Blueprint, jsonify, request

from models import db, User
from utils.auth_helpers import generate_token

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    username = str(data.get("username") or "").strip()
    email = str(data.get("email") or "").strip().lower()
    password = str(data.get("password") or "")
    role = data.get("role", "user")
    is_deaf = bool(data.get("is_deaf", False))

    # Валидация: пустые поля, формат email, длина пароля, роли
    if not username or len(username) > 50:
        return jsonify({"message": "Некорректное имя пользователя"}), 400
    if ("@" not in email or len(email) > 120
            or "." not in email.split("@")[-1]):
        return jsonify({"message": "Некорректный email"}), 400
    if len(password) < 8:
        return jsonify(
            {"message": "Пароль должен быть не короче 8 символов"}), 400
    if role not in ("user", "organizer", "admin"):
        return jsonify({"message": "Недопустимая роль"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email уже занят"}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Имя пользователя уже занято"}), 400

    user = User(username=username, email=email, role=role, is_deaf=is_deaf)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "Пользователь создан",
                    "user_id": user.id}), 201


@auth_bp.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = str(data.get("email") or "").strip().lower()
    password = str(data.get("password") or "")

    user = User.query.filter_by(email=email).first()
    if user is None or not user.check_password(password):
        return jsonify({"message": "Неверный email или пароль"}), 401

    return jsonify({
        "message": "Вход выполнен",
        "token": generate_token(user),
        "role": user.role,
        "user_id": user.id,
    }), 200
