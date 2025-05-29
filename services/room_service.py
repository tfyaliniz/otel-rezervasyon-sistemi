from flask import current_app
from models.room import Room, RoomImage
from models.reservation import Reservation
from models.notification import MaintenanceRecord
from datetime import datetime, timedelta
from sqlalchemy import func
from database import db
import os

class RoomService:
    def create_room(self, room_number, room_type, capacity, price, description,
                   features=None, floor=None, size=None, has_balcony=False, has_sea_view=False):
        """Yeni oda oluştur"""
        if Room.query.filter_by(room_number=room_number).first():
            raise ValueError('Bu oda numarası zaten kullanılıyor.')
        
        room = Room(
            room_number=room_number,
            room_type=room_type,
            capacity=capacity,
            price=price,
            description=description,
            features=features or [],
            floor=floor,
            size=size,
            has_balcony=has_balcony,
            has_sea_view=has_sea_view,
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        db.session.add(room)
        db.session.commit()
        return room
    
    def update_room(self, room_id, room_number=None, room_type=None, capacity=None,
                   price=None, description=None, features=None, floor=None, size=None,
                   has_balcony=None, has_sea_view=None):
        """Oda bilgilerini güncelle"""
        room = Room.query.get_or_404(room_id)
        
        if room_number and room_number != room.room_number:
            if Room.query.filter_by(room_number=room_number).first():
                raise ValueError('Bu oda numarası zaten kullanılıyor.')
            room.room_number = room_number
        
        if room_type:
            room.room_type = room_type
        if capacity:
            room.capacity = capacity
        if price:
            room.price = price
        if description:
            room.description = description
        if features:
            room.features = features
        if floor:
            room.floor = floor
        if size:
            room.size = size
        if has_balcony is not None:
            room.has_balcony = has_balcony
        if has_sea_view is not None:
            room.has_sea_view = has_sea_view
        
        room.updated_at = datetime.utcnow()
        db.session.commit()
        return room
    
    def delete_room(self, room_id):
        """Oda sil"""
        room = Room.query.get_or_404(room_id)
        
        # Aktif rezervasyon kontrolü
        if room.has_active_reservations():
            raise ValueError('Bu oda için aktif rezervasyonlar bulunuyor.')
        
        # Oda resimlerini sil
        for image in room.images:
            try:
                os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], 'rooms', image.filename))
            except:
                pass
        
        db.session.delete(room)
        db.session.commit()
    
    def add_room_image(self, room_id, filename):
        """Oda resmi ekle"""
        room = Room.query.get_or_404(room_id)
        
        image = RoomImage(
            room_id=room_id,
            filename=filename,
            created_at=datetime.utcnow()
        )
        
        db.session.add(image)
        db.session.commit()
        return image
    
    def remove_room_image(self, image_id):
        """Oda resmi sil"""
        image = RoomImage.query.get_or_404(image_id)
        
        try:
            os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], 'rooms', image.filename))
        except:
            pass
        
        db.session.delete(image)
        db.session.commit()
    
    def get_room_by_id(self, room_id):
        """ID ile oda getir"""
        return Room.query.get_or_404(room_id)
    
    def get_all_rooms(self):
        """Tüm odaları getir"""
        return Room.query.filter_by(is_active=True).all()
    
    def get_featured_rooms(self, limit=6):
        """Öne çıkan odaları getir"""
        return Room.query.filter_by(is_active=True).order_by(
            Room.average_rating.desc(),
            Room.created_at.desc()
        ).limit(limit).all()
    
    def search_rooms(self, room_type=None, capacity=None, min_price=None, max_price=None):
        """Oda ara"""
        query = Room.query.filter_by(is_active=True)
        
        if room_type:
            query = query.filter_by(room_type=room_type)
        if capacity:
            query = query.filter(Room.capacity >= capacity)
        if min_price:
            query = query.filter(Room.price >= min_price)
        if max_price:
            query = query.filter(Room.price <= max_price)
        
        return query.all()
    
    def get_available_rooms(self, check_in, check_out, capacity=None, room_type=None):
        """Müsait odaları getir"""
        query = Room.query.filter_by(is_active=True)
        
        # Tarih çakışması olan odaları hariç tut
        unavailable_rooms = db.session.query(Reservation.room_id).filter(
            Reservation.status.in_(['pending', 'confirmed']),
            Reservation.check_in < check_out,
            Reservation.check_out > check_in
        ).subquery()
        
        query = query.filter(~Room.id.in_(unavailable_rooms))
        
        if capacity:
            query = query.filter(Room.capacity >= capacity)
        if room_type:
            query = query.filter_by(room_type=room_type)
        
        return query.all()
    
    def get_room_occupancy_rate(self, room_id, start_date, end_date):
        """Oda doluluk oranını hesapla"""
        room = Room.query.get_or_404(room_id)
        total_days = (end_date - start_date).days
        
        if total_days <= 0:
            raise ValueError('Geçersiz tarih aralığı.')
        
        occupied_days = db.session.query(func.sum(
            func.julianday(func.min(end_date, Reservation.check_out)) -
            func.julianday(func.max(start_date, Reservation.check_in))
        )).filter(
            Reservation.room_id == room_id,
            Reservation.status == 'confirmed',
            Reservation.check_in < end_date,
            Reservation.check_out > start_date
        ).scalar() or 0
        
        return (occupied_days / total_days) * 100
    
    def get_room_revenue(self, room_id, start_date, end_date):
        """Oda gelirini hesapla"""
        room = Room.query.get_or_404(room_id)
        
        revenue = db.session.query(func.sum(Reservation.total_price)).filter(
            Reservation.room_id == room_id,
            Reservation.status == 'confirmed',
            Reservation.check_in >= start_date,
            Reservation.check_out <= end_date
        ).scalar() or 0
        
        return revenue 