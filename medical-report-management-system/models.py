from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.BigInteger, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone = db.Column(db.String(32))
    role = db.Column(db.Enum('doctor', 'patient'), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class OTP(db.Model):
    __tablename__ = 'otps'
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(
        db.BigInteger,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )
    otp_code = db.Column(db.String(255), nullable=False)
    purpose = db.Column(db.Enum('login', 'verify'), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    attempts = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='otp_entries')

class Report(db.Model):
    __tablename__ = 'reports'
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    uploaded_by = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    filename_orig = db.Column(db.String(255))
    filename_enc = db.Column(db.String(255), nullable=False)
    aes_iv = db.Column(db.LargeBinary(16), nullable=False)
    mime_type = db.Column(db.String(100))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    owner = db.relationship('User', foreign_keys=[user_id])
    uploader = db.relationship('User', foreign_keys=[uploaded_by])

class AuditTrail(db.Model):
    __tablename__ = 'audit_trail'
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'))
    action = db.Column(db.String(100), nullable=False)
    target_table = db.Column(db.String(64))
    target_id = db.Column(db.BigInteger)
    ip_address = db.Column(db.String(64))
    details = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User')
