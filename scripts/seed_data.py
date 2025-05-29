from app import create_app
from database import db
from models.room import Room, RoomImage
from datetime import datetime

def seed_rooms():
    rooms_data = [
        {
            'room_number': '101',
            'room_type': 'Standart Oda',
            'capacity': 2,
            'price': 750.0,
            'floor': 1,
            'size': 25.0,
            'description': 'Şehir manzaralı konforlu standart oda',
            'has_balcony': True,
            'has_sea_view': False,
            'images': [
                {'image_path': 'img/rooms/standart1.jpg', 'is_primary': True},
                {'image_path': 'img/rooms/standart2.jpg', 'is_primary': False}
            ]
        },
        {
            'room_number': '201',
            'room_type': 'Deluxe Oda',
            'capacity': 2,
            'price': 1250.0,
            'floor': 2,
            'size': 35.0,
            'description': 'Deniz manzaralı lüks deluxe oda',
            'has_balcony': True,
            'has_sea_view': True,
            'images': [
                {'image_path': 'img/rooms/deluxe1.jpg', 'is_primary': True},
                {'image_path': 'img/rooms/deluxe2.jpg', 'is_primary': False}
            ]
        },
        {
            'room_number': '301',
            'room_type': 'Suit Oda',
            'capacity': 4,
            'price': 2500.0,
            'floor': 3,
            'size': 50.0,
            'description': 'Geniş ve lüks suit oda, oturma alanı ve jakuzi',
            'has_balcony': True,
            'has_sea_view': True,
            'images': [
                {'image_path': 'img/rooms/suite1.jpg', 'is_primary': True},
                {'image_path': 'img/rooms/suite2.jpg', 'is_primary': False}
            ]
        },
        {
            'room_number': '401',
            'room_type': 'Aile Odası',
            'capacity': 6,
            'price': 3000.0,
            'floor': 4,
            'size': 65.0,
            'description': 'Geniş aile odası, iki yatak odası ve oturma alanı',
            'has_balcony': True,
            'has_sea_view': True,
            'images': [
                {'image_path': 'img/rooms/family1.jpg', 'is_primary': True},
                {'image_path': 'img/rooms/family2.jpg', 'is_primary': False}
            ]
        }
    ]
    
    for room_data in rooms_data:
        images = room_data.pop('images')
        room = Room(**room_data)
        db.session.add(room)
        db.session.flush()  # ID'yi almak için flush yapıyoruz
        
        for image_data in images:
            image = RoomImage(room_id=room.id, **image_data)
            db.session.add(image)
    
    db.session.commit()
    print('Örnek odalar eklendi.')

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        seed_rooms() 