from database import db
from datetime import datetime

class Room(db.Model):
    __tablename__ = 'rooms'
    
    id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.String(10), unique=True, nullable=False)
    room_type = db.Column(db.String(50), nullable=False)  # Standart, Deluxe, Suite vb.
    capacity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    floor = db.Column(db.Integer, nullable=False)
    size = db.Column(db.Float)  # metrekare
    description = db.Column(db.Text)
    has_balcony = db.Column(db.Boolean, default=False)
    has_sea_view = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    average_rating = db.Column(db.Float, default=0.0)
    
    # İlişkiler
    maintenance_records = db.relationship('MaintenanceRecord', backref='room', lazy=True)
    images = db.relationship('RoomImage', backref='room', lazy=True)
    
    def __repr__(self):
        return f'<Room {self.room_number}>'

class RoomImage(db.Model):
    __tablename__ = 'room_images'
    
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    is_primary = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<RoomImage {self.image_path}>' 