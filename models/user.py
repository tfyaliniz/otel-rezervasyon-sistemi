from database import db
from flask_login import UserMixin
from datetime import datetime, timedelta
import secrets

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    email_verified = db.Column(db.Boolean, default=False)
    verification_code = db.Column(db.String(6))
    verification_code_expires = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    reservations = db.relationship('Reservation', backref='user', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True)
    
    def generate_verification_code(self):
        """E-posta doğrulama kodu oluştur"""
        self.verification_code = ''.join(secrets.choice('0123456789') for _ in range(6))
        self.verification_code_expires = datetime.utcnow() + timedelta(minutes=30)
        db.session.commit()
        return self.verification_code
    
    def verify_email(self, code):
        """E-posta doğrulama kodunu kontrol et"""
        if (self.verification_code == code and 
            self.verification_code_expires > datetime.utcnow()):
            self.email_verified = True
            self.verification_code = None
            self.verification_code_expires = None
            db.session.commit()
            return True
        return False
    
    def __repr__(self):
        return f'<User {self.email}>' 