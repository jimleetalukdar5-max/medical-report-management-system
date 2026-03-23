import os
import random
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, OTP


def register_user(email, phone, role, password):
    existing = User.query.filter_by(email=email).first()
    if existing:
        return None, "User exists"

    user = User(
        email=email,
        phone=phone,
        role=role,
        password_hash=generate_password_hash(password)
    )

    db.session.add(user)
    db.session.commit()
    return user, None


def generate_otp_for_user(user, purpose="login", minutes=1):
    otp = f"{random.randint(0, 999999):06d}"
    expires = datetime.datetime.utcnow() + datetime.timedelta(minutes=minutes)

    otp_row = OTP(
        user_id=user.id,
        otp_code=generate_password_hash(otp),
        purpose=purpose,
        expires_at=expires
    )

    db.session.add(otp_row)
    db.session.commit()
    
    return otp


def verify_otp(user, otp_code, purpose="login"):
    rows = OTP.query.filter_by(
        user_id=user.id,
        purpose=purpose
    ).order_by(OTP.created_at.desc()).all()

    if not rows:
        return False, "No OTP found"

    row = rows[0]

    if row.expires_at < datetime.datetime.utcnow():
        return False, "OTP expired"

    if row.attempts >= 2:
        return False, "Too many attempts"

    if not check_password_hash(row.otp_code, otp_code):
        row.attempts += 1
        db.session.commit()
        return False, "Invalid OTP"

    db.session.delete(row)
    db.session.commit()
    return True, None


def authenticate(email, password):
    user = User.query.filter_by(email=email).first()
    if not user:
        return None
    if not check_password_hash(user.password_hash, password):
        return None
    return user
