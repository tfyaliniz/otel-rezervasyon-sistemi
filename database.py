from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def init_db(app):
    """Veritabanını başlat"""
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Modelleri import et
    from models.user import User
    from models.room import Room, RoomImage
    from models.reservation import Reservation, Payment, Review
    from models.notification import Notification, MaintenanceRecord
    
    # Veritabanı tablolarını oluştur
    with app.app_context():
        db.create_all() 