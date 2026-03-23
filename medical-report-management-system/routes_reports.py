import os
import io
import base64
from uuid import uuid4
from flask import Blueprint, request, send_file, abort, current_app, redirect, url_for, session, flash, render_template
from models import db, Report, User
from encrypt import encrypt_and_b64, decrypt_from_b64
from audit import log_action

bp = Blueprint('reports', __name__)


def get_current_user():
    uid = session.get("user_id")
    if not uid:
        return None
    return User.query.get(uid)


def has_access(user, report):
    if user.role == "doctor":
        return True
    if user.role == "patient" and report.user_id == user.id:
        return True
    return False


@bp.route('/upload_report', methods=['POST'])
def upload_report():
    current = get_current_user()
    if not current:
        abort(401, "not authenticated")

    uemail = request.form.get("user_email")
    user = User.query.filter_by(email=uemail).first()
    if not user:
        abort(400, "user not found")

    f = request.files.get('file')
    if not f:
        abort(400, "no file")

    data = f.read()

    # Encrypt the file — now encrypt_and_b64 returns (iv_b64, ct_b64) or concat pair
    iv_b64, ct_b64 = encrypt_and_b64(data)

    enc_filename = f"{uuid4().hex}.enc"
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], enc_filename)
    os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)

    with open(path, 'wb') as fh:
        fh.write(base64.b64decode(ct_b64))

    report = Report(
        user_id=user.id,
        uploaded_by=current.id,
        filename_orig=f.filename,
        filename_enc=enc_filename,
        aes_iv=base64.b64decode(iv_b64),
        mime_type=f.mimetype,
    )

    db.session.add(report)
    db.session.commit()

    log_action(current.id, "report_upload", "reports", report.id, request.remote_addr)
    flash("Report uploaded successfully", "success")
    return redirect(url_for("upload_page", success=1))


@bp.route('/view_report/<int:report_id>', methods=['GET'])
def view_report(report_id):
    current = get_current_user()
    if not current:
        abort(401, "not authenticated")

    report = Report.query.get_or_404(report_id)

    if not has_access(current, report):
        log_action(current.id, "unauthorized_report_view", "reports", report_id, request.remote_addr)
        abort(403)

    enc_path = os.path.join(current_app.config['UPLOAD_FOLDER'], report.filename_enc)
    with open(enc_path, 'rb') as fh:
        ct = fh.read()

    # Decrypt
    plain = decrypt_from_b64(
        base64.b64encode(report.aes_iv).decode(),
        base64.b64encode(ct).decode()
    )

    log_action(current.id, "report_view", "reports", report_id, request.remote_addr)

    return send_file(
        io.BytesIO(plain),
        mimetype=report.mime_type,
        as_attachment=True,
        download_name=report.filename_orig
    )


@bp.route('/reports_list', methods=['GET'])
def reports_list():
    current = get_current_user()
    if not current:
        flash("Please login", "warning")
        return redirect(url_for("login"))

    if current.role == "doctor":
        reports = Report.query.order_by(Report.uploaded_at.desc()).all()
    else:
        reports = Report.query.filter_by(user_id=current.id).order_by(Report.uploaded_at.desc()).all()

    # show page with list, allowing view and delete
    return render_template("reports_list.html", reports=reports, current=current)


@bp.route('/delete_report/<int:report_id>', methods=['POST'])
def delete_report(report_id):
    current = get_current_user()
    if not current:
        abort(401, "not authenticated")

    report = Report.query.get_or_404(report_id)
    if not has_access(current, report):
        abort(403)

    # delete file
    enc_path = os.path.join(current_app.config['UPLOAD_FOLDER'], report.filename_enc)
    try:
        if os.path.exists(enc_path):
            os.remove(enc_path)
    except Exception:
        pass

    db.session.delete(report)
    db.session.commit()

    log_action(current.id, "report_delete", "reports", report_id, request.remote_addr)
    flash("Report deleted", "success")
    return redirect( url_for('reports.reports_list'))
