import datetime

from flask import Blueprint, jsonify, request

from models import db, Event
from utils.auth_helpers import token_required, role_required
from utils.accessibility import format_event_response

events_bp = Blueprint("events", __name__)


def parse_event_date(value):
    """Строка '2026-11-01 12:00:00' или ISO-формат -> datetime (или None).

    PostgreSQL сам разбирает строки, а SQLite - нет (падает с ошибкой),
    поэтому дату всегда превращаем в datetime явно.
    """
    if isinstance(value, datetime.datetime):
        return value
    if not isinstance(value, str):
        return None
    try:
        dt = datetime.datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is not None:
        dt = dt.astimezone(datetime.timezone.utc).replace(tzinfo=None)
    return dt


@events_bp.route("/api/events", methods=["GET"])
def list_events():
    query = Event.query
    # Публичный фильтр: ?inclusive=1 - только инклюзивные мероприятия
    if request.args.get("inclusive") in ("1", "true"):
        query = query.filter_by(is_inclusive=True)
    events = query.order_by(Event.event_date).all()
    return jsonify([format_event_response(e) for e in events]), 200


@events_bp.route("/api/events/<int:event_id>", methods=["GET"])
def get_event(event_id):
    event = db.get_or_404(Event, event_id)
    return jsonify(format_event_response(event)), 200


@events_bp.route("/api/events", methods=["POST"])
@token_required
@role_required("organizer", "admin")
def create_event(user):
    data = request.get_json(silent=True) or {}
    title = str(data.get("title") or "").strip()
    if not title or len(title) > 100:
        return jsonify(
            {"message": "Название обязательно, до 100 символов"}), 400
    if not data.get("event_date"):
        return jsonify({"message": "Укажите дату и время"}), 400
    event_date = parse_event_date(data.get("event_date"))
    if event_date is None:
        return jsonify({"message": "Неверный формат даты. "
                        "Пример: 2026-11-01 12:00:00"}), 400

    event = Event(
        title=title,
        description=data.get("description"),
        event_date=event_date,
        location=data.get("location"),
        organizer_id=user.id,
        is_inclusive=bool(data.get("is_inclusive", False)),
        sign_language=bool(data.get("sign_language", False)),
        visual_alerts=bool(data.get("visual_alerts", False)),
    )
    db.session.add(event)
    db.session.commit()
    return jsonify({"message": "Мероприятие создано", "id": event.id}), 201


@events_bp.route("/api/events/<int:event_id>", methods=["PUT"])
@token_required
@role_required("organizer", "admin")
def update_event(user, event_id):
    event = db.get_or_404(Event, event_id)
    # Организатор правит только своё; admin - любое
    if event.organizer_id != user.id and user.role != "admin":
        return jsonify(
            {"message": "Можно редактировать только свои мероприятия"}), 403
    data = request.get_json(silent=True) or {}

    if "title" in data:
        title = str(data["title"] or "").strip()
        if not title or len(title) > 100:
            return jsonify(
                {"message": "Название обязательно, до 100 символов"}), 400
        event.title = title
    if "event_date" in data:
        event_date = parse_event_date(data["event_date"])
        if event_date is None:
            return jsonify({"message": "Неверный формат даты. "
                            "Пример: 2026-11-01 12:00:00"}), 400
        event.event_date = event_date
    for field in ("description", "location"):
        if field in data:
            setattr(event, field, data[field])
    for field in ("is_inclusive", "sign_language", "visual_alerts"):
        if field in data:
            setattr(event, field, bool(data[field]))
    db.session.commit()
    return jsonify(format_event_response(event)), 200


@events_bp.route("/api/events/<int:event_id>", methods=["DELETE"])
@token_required
@role_required("organizer", "admin")
def delete_event(user, event_id):
    event = db.get_or_404(Event, event_id)
    if event.organizer_id != user.id and user.role != "admin":
        return jsonify(
            {"message": "Можно удалять только свои мероприятия"}), 403
    db.session.delete(event)
    db.session.commit()
    return jsonify({"message": "Мероприятие удалено"}), 200
