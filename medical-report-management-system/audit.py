from models import AuditTrail, db


def log_action(user_id, action, target_table=None, target_id=None, ip=None, details=None):
    a = AuditTrail(
        user_id=user_id,
        action=action,
        target_table=target_table,
        target_id=target_id,
        ip_address=ip,
        details=details
    )
    db.session.add(a)
    db.session.commit()
