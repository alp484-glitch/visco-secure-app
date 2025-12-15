from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from .models import db, User, ClientData
from .schemas import UserCreateSchema, ClientDataSchema, LoginSchema
from .utils import verify_password, encrypt_data, decrypt_data
from pydantic import ValidationError

bp = Blueprint("routes", __name__)


# Home page
@bp.route("/")
@login_required
def index():
    """Home page (login required)"""
    return render_template("index.html", user=current_user)


# Login
@bp.route("/login", methods=["GET", "POST"])
def login():
    """Login interface"""
    if current_user.is_authenticated:
        return redirect(url_for("routes.index"))

    if request.method == "POST":
        try:
            # Validate input
            data = LoginSchema(**request.form)
            user = User.query.filter_by(username=data.username).first()

            # Verify user and password
            if not user or not verify_password(data.password, user.password_hash):
                flash("Invalid username or password", "danger")
                return redirect(url_for("routes.login"))

            # Login user
            login_user(user, remember=False, duration=current_app.config["PERMANENT_SESSION_LIFETIME"])
            return redirect(url_for("routes.index"))

        except ValidationError as e:
            flash(f"Input error: {e.errors()[0]['msg']}", "danger")
            return redirect(url_for("routes.login"))

    return render_template("login.html")


# Register
@bp.route("/register", methods=["GET", "POST"])
def register():
    """Registration interface"""
    if current_user.is_authenticated:
        return redirect(url_for("routes.index"))

    if request.method == "POST":
        try:
            # Validate input
            data = UserCreateSchema(**request.form)

            # Check if username/email already exists
            if User.query.filter_by(username=data.username).first():
                flash("Username already exists", "danger")
                return redirect(url_for("routes.register"))
            if User.query.filter_by(email=data.email).first():
                flash("Email already exists", "danger")
                return redirect(url_for("routes.register"))

            # Create user
            user = User(username=data.username, email=data.email)
            user.set_password(data.password)
            db.session.add(user)
            db.session.commit()

            flash("Registration successful, please log in", "success")
            return redirect(url_for("routes.login"))

        except ValidationError as e:
            flash(f"Input error: {e.errors()[0]['msg']}", "danger")
            return redirect(url_for("routes.register"))

    return render_template("register.html")


# Logout
@bp.route("/logout")
@login_required
def logout():
    """Logout interface"""
    logout_user()
    flash("Logged out successfully", "success")
    return redirect(url_for("routes.login"))


# Client data management (API)
@bp.route("/api/client/data", methods=["POST"])
@login_required
def add_client_data():
    """Add client sensitive data (stored encrypted)"""
    try:
        # Validate input
        json_data = request.get_json()
        data = ClientDataSchema(**json_data)

        # Encrypt data and store
        encrypted_data = encrypt_data(data.data)
        client_data = ClientData(user_id=current_user.id, data=encrypted_data)
        db.session.add(client_data)
        db.session.commit()

        return jsonify({"status": "success", "message": "Data saved successfully"}), 200

    except ValidationError as e:
        return jsonify({"status": "error", "message": e.errors()[0]['msg']}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@bp.route("/api/client/data", methods=["GET"])
@login_required
def get_client_data():
    """Get client sensitive data (decrypted)"""
    try:
        # Get all data of current user
        client_data_list = ClientData.query.filter_by(user_id=current_user.id).all()
        result = []
        for item in client_data_list:
            result.append({
                "id": item.id,
                "data": decrypt_data(item.data),
                "created_at": item.created_at.strftime("%Y-%m-%d %H:%M:%S")
            })

        return jsonify({"status": "success", "data": result}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# Delete client data
@bp.route("/api/client/data/<int:data_id>", methods=["DELETE"])
@login_required
def delete_client_data(data_id):
    """Delete client data (GDPR right to erasure)"""
    try:
        # Only allow deleting own data
        client_data = ClientData.query.filter_by(id=data_id, user_id=current_user.id).first()
        if not client_data:
            return jsonify({"status": "error", "message": "Data does not exist"}), 404

        db.session.delete(client_data)
        db.session.commit()
        return jsonify({"status": "success", "message": "Data deleted successfully"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500