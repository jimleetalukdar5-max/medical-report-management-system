from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from models import db, User
from auth import register_user, authenticate, generate_otp_for_user, verify_otp as auth_verify_otp
from routes_reports import bp as reports_bp
import os

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY

# Register blueprint
app.register_blueprint(reports_bp)

# Init DB
db.init_app(app)
with app.app_context():
    db.create_all()


@app.route("/")
def home():
    # If logged in, go to dashboard
    if session.get("user_id"):
        return redirect(url_for("dashboard"))
    return render_template("login.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email")
    password = request.form.get("password")

    user = authenticate(email, password)
    if not user:
        flash("Invalid credentials", "danger")
        return redirect(url_for("login"))

    # Generate OTP and store temp_user_id in session for verification step
    otp_plain = generate_otp_for_user(user)  # returns plaintext OTP (you should send via email/SMS)
    session["temp_user_id"] = user.id
    # NOTE: in production send OTP via SMS/email. For dev we flash it so you can see it.
    flash("OTP sent to your registered contact", "info")
    return redirect(url_for("verify_otp"))


@app.route("/verify_otp", methods=["GET", "POST"])
def verify_otp():
    temp_id = session.get("temp_user_id")
    if not temp_id:
        flash("No login attempt found. Please login first.", "warning")
        return redirect(url_for("login"))

    user = User.query.get(temp_id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("login"))

    if request.method == "GET":
        return render_template("verify_otp.html", email=user.email)

    otp_code = request.form.get("otp")
    ok, err = auth_verify_otp(user, otp_code)
    if not ok:
        flash(err or "OTP verification failed", "danger")
        return redirect(url_for("verify_otp"))

    # OTP verified -> create session
    session.pop("temp_user_id", None)
    session["user_id"] = user.id
    session["role"] = user.role
    flash("Login successful", "success")
    return redirect(url_for("dashboard"))


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out", "info")
    return redirect(url_for("login"))


@app.route("/dashboard")
def dashboard():
    uid = session.get("user_id")
    if not uid:
        flash("Please login", "warning")
        return redirect(url_for("login"))

    user = User.query.get(uid)
    if not user:
        session.clear()
        flash("Invalid session", "danger")
        return redirect(url_for("login"))

    # doctor sees all reports; patient sees only their own
    if user.role == "doctor":
        # doctor dashboard will call the blueprint endpoints or display results
        return render_template("dashboard_doctor.html", user=user)
    else:
        return render_template("dashboard_patient.html", user=user)

@app.route("/upload", methods=["GET"])
def upload_page():
    return render_template("upload.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    email = request.form.get("email")
    phone = request.form.get("phone")
    role = request.form.get("role")
    password = request.form.get("password")

    user, err = register_user(email, phone, role, password)
    if err:
        flash(err, "danger")
        return redirect(url_for("register"))

    flash("Registered successfully. Please login.", "success")
    return redirect(url_for("login"))


if __name__ == "__main__":
    os.makedirs(app.config.get("UPLOAD_FOLDER", "uploads"), exist_ok=True)
    app.run()
