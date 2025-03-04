from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os
from models import db, User, Report

routes = Blueprint("routes", __name__)

UPLOAD_FOLDER = "uploads"

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

@routes.route("/login", methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(email=data["email"]).first()
    
    if not user or not user.check_password(data["password"]):
        return jsonify({"message": "Invalid credentials"}), 401

    return jsonify({"token": user.generate_token(), "userId": user.id, "role": user.role})

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
        user_id=user["id"],
        type=data["type"],
        description=data["description"],
        file_path=file_path
    )
    db.session.add(report)
    db.session.commit()
    
    return jsonify({"message": "Report submitted successfully"}), 201

@routes.route("/reports/<int:user_id>", methods=["GET"])
@jwt_required()
def get_reports(user_id):
    reports = Report.query.filter_by(user_id=user_id).all()
    return jsonify([{"id": r.id, "type": r.type, "status": r.status, "description": r.description} for r in reports])
