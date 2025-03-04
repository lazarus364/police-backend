from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
import os
from models import db, User, Report

routes = Blueprint("routes", __name__)
mail = Mail()

UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):  # ✅ Ensure Upload Folder Exists
    os.makedirs(UPLOAD_FOLDER)

### ✅ Register User Route
@routes.route("/register", methods=["POST"])
def register():
    data = request.json
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"message": "Email already exists"}), 400
    
    user = User(email=data["email"])
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()
    
    return jsonify({"message": "User registered successfully!"}), 201

### ✅ Login User Route
@routes.route("/login", methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(email=data["email"]).first()
    
    if not user or not user.check_password(data["password"]):
        return jsonify({"message": "Invalid credentials"}), 401

    token = create_access_token(identity={"id": user.id, "role": user.role})
    return jsonify({"token": token, "userId": user.id, "role": user.role})

### ✅ Report Incident Route (With File Upload)
@routes.route("/reports", methods=["POST"])
@jwt_required()
def report_incident():
    user = get_jwt_identity()
    data = request.form

    file = request.files.get("file")
    file_path = None
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

    report = Report(
        user_id=user.get("id"),  # ✅ Prevent KeyError
        type=data["type"],
        description=data["description"],
        file_path=file_path
    )
    db.session.add(report)
    db.session.commit()
    
    return jsonify({"message": "Report submitted successfully"}), 201

### ✅ Get Reports for a User
@routes.route("/reports/<int:user_id>", methods=["GET"])
@jwt_required()
def get_reports(user_id):
    reports = Report.query.filter_by(user_id=user_id).all()
    return jsonify([
        {"id": r.id, "type": r.type, "status": r.status, "description": r.description, "file_path": r.file_path} 
        for r in reports
    ])

### ✅ Forgot Password (Send Reset Email)
@routes.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request.json
    user = User.query.filter_by(email=data["email"]).first()
    
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    reset_token = create_access_token(identity={"id": user.id})  # ✅ Generate Reset Token

    msg = Message(
        "Password Reset Request",
        sender="noreply@yourapp.com",
        recipients=[user.email]
    )
    msg.body = f"Click here to reset your password: http://localhost:3000/reset-password/{reset_token}"
    mail.send(msg)

    return jsonify({"message": "Password reset link sent!"})

### ✅ Reset Password
@routes.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.json
    token = data.get("token")
    new_password = data.get("newPassword")

    try:
        decoded = get_jwt_identity()
        user = User.query.get(decoded["id"])
        user.set_password(new_password)
        db.session.commit()
        return jsonify({"message": "Password reset successful!"})
    except:
        return jsonify({"message": "Invalid or expired token"}), 400
