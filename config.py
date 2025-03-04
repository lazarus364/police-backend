import os

class Config:
    SECRET_KEY = "super-secret-key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"
    JWT_SECRET_KEY = "super-secret-jwt-key"
    
    # Email Config (Use Mailtrap for Testing)
    MAIL_SERVER = "smtp.mailtrap.io"
    MAIL_PORT = 2525
    MAIL_USERNAME = "your_mailtrap_username"
    MAIL_PASSWORD = "your_mailtrap_password"
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
