from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError

from models import db, Registration, Event
from utils.auth_helpers import token_required, role_required

registrations_bp = Blueprint("registrations", __name__)


@registrations_bp.route("/api/registrations", methods=["POST"])
@token_required
def register_to_event(user):
    data = request.get_json(silent=True) or {}
    try:
        event_id = int(data.get("event_id"))
    except (TypeError, ValueError):
        return jsonify({"message": "Укажите event_id"}), 400

    event = db.session.get(Event, event_id)
    if event is None:
        return jsonify({"message": "Мероприятие не найдено"}), 404

    # Повторная регистрация запрещена (UNIQUE-ограничение в БД)
    existing = Registration.query.filter_by(
        user_id=user.id, event_id=event_id).first()
    if existing:
        return jsonify({"message": "Вы уже зарегистрированы"}), 400

    reg = Registration(
        user_id=user.id,
        event_id=event_id,
        status="pending",
        accessibility_request=data.get("accessibility_request"),
    )
    db.session.add(reg)
    try:
        db.session.commit()
    except IntegrityError:
        # Два одновременных запроса: сработало ограничение UNIQUE в БД
        db.session.rollback()
        return jsonify({"message": "Вы уже зарегистрированы"}), 400
    return jsonify({"message": "Регистрация создана",
                    "id": reg.id, "status": reg.status}), 201


@registrations_bp.route("/api/registrations", methods=["GET"])
@token_required
def my_registrations(user):
    regs = Registration.query.filter_by(user_id=user.id).all()
    result = []
    for r in regs:
        result.append({
            "id": r.id,
            "event_id": r.event_id,
            "status": r.status,
            "accessibility_request": r.accessibility_request,
        })
    return jsonify(result), 200


@registrations_bp.route("/api/registrations/<int:reg_id>", methods=["PUT"])
@token_required
@role_required("organizer", "admin")
def change_status(user, reg_id):
    reg = db.get_or_404(Registration, reg_id)
    # Организатор меняет статусы только на своих мероприятиях; admin - везде
    if reg.event.organizer_id != user.id and user.role != "admin":
        return jsonify({"message": "Можно менять статусы только "
                        "на своих мероприятиях"}), 403
    data = request.get_json(silent=True) or {}
    status = data.get("status")
    if status not in ("pending", "confirmed", "cancelled"):
        return jsonify({"message": "Недопустимый статус"}), 400
    reg.status = status
    db.session.commit()
    return jsonify({"message": "Статус обновлён", "status": reg.status}), 200
