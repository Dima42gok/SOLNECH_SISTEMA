import datetime

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


def utcnow():
    """Текущее UTC-время без tzinfo (datetime.utcnow устарел в Python 3.12)."""
    return datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")
    is_deaf = db.Column(db.Boolean, default=False)
    accessibility_needs = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=utcnow)

    events = db.relationship("Event", backref="organizer", lazy=True)
    registrations = db.relationship("Registration", backref="user", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    event_date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200))
    organizer_id = db.Column(db.Integer, db.ForeignKey("users.id"),
                             nullable=False)
    is_inclusive = db.Column(db.Boolean, default=False)
    sign_language = db.Column(db.Boolean, default=False)
    visual_alerts = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=utcnow)

    registrations = db.relationship("Registration", backref="event",
                                    lazy=True, cascade="all, delete-orphan")


class Registration(db.Model):
    __tablename__ = "registrations"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"),
                         nullable=False)
    status = db.Column(db.String(20), nullable=False, default="pending")
    accessibility_request = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=utcnow)

    __table_args__ = (
        db.UniqueConstraint("user_id", "event_id"),
        db.CheckConstraint(
            "status IN ('pending', 'confirmed', 'cancelled')",
            name="ck_registration_status",
        ),
    )
