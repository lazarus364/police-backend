from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token
from datetime import datetime

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(10), default="user")  # "admin" or "user"
    
    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def generate_token(self):
        return create_access_token(identity={"id": self.id, "role": self.role})

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # Crime, Accident, Lost Property
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default="Pending")  # Pending, In Progress, Resolved
    file_path = db.Column(db.String(255))  # Path for uploaded files
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
