from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from .utils import hash_password

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User model"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.LargeBinary, nullable=False)  # Store hashed password
    role = db.Column(db.String(10), default="client")  # admin/client
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Associated client data
    client_data = db.relationship("ClientData", backref="user", lazy=True, cascade="all, delete-orphan")

    def set_password(self, password: str):
        """Set password (hashing)"""
        self.password_hash = hash_password(password)


class ClientData(db.Model):
    """Client sensitive data model"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    data = db.Column(db.LargeBinary, nullable=False)  # Encrypted sensitive data
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)